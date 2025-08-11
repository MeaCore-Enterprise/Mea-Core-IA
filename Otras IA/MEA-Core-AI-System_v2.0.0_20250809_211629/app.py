import os
import json
import threading
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from core.store import ensure_dir, append_jsonl, iter_jsonl
from core.chunker import make_chunks
from core.tokenize import tokenize
from core.bm25 import BM25Index
from core.feedback import QueryLearner
from core.summarize import summarize
from core.pdf_ingest import pdf_to_text
from core.neural import IntentClassifier, PersonalityEngine, LearningSystem
from core.classification import DocumentClassifier, SemanticAnalyzer, IntelligentGrouping
from core.voice import AdvancedInteraction
from core.distributed import get_distributed_scheduler, create_distributed_task, TaskType, LocalWorker
from core.ultralight_nn import create_ultralight_model, get_predefined_model, PREDEFINED_MODELS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Data paths
DATA_DIR = "data"
DOCS_PATH = os.path.join(DATA_DIR, "documents.jsonl")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.jsonl")
INDEX_PATH = os.path.join(DATA_DIR, "index.json")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.json")

# Initialize Flask app
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("SESSION_SECRET", "mea-core-local-ai-assistant")
ensure_dir(DATA_DIR)

# Initialize AI components
bm25 = BM25Index()
learner = QueryLearner()
progress = {"status": "idle", "processed": 0, "total": 0}

# Initialize advanced AI features
intent_classifier = IntentClassifier()
personality_engine = PersonalityEngine()
learning_system = LearningSystem()
document_classifier = DocumentClassifier()
semantic_analyzer = SemanticAnalyzer()
intelligent_grouping = IntelligentGrouping()
advanced_interaction = AdvancedInteraction()

# Initialize distributed computing system (lazy loading to avoid startup errors)
distributed_scheduler = None
local_worker = None

# Initialize ultra-light neural networks
ultralight_models = {
    'intent_classifier': None,
    'document_classifier': None,
    'sentiment_classifier': None
}

def get_or_create_distributed_scheduler():
    """Get or create distributed scheduler with error handling"""
    global distributed_scheduler
    if distributed_scheduler is None:
        try:
            distributed_scheduler = get_distributed_scheduler()
            distributed_scheduler.start()
            logging.info("MEA-Core distributed system initialized")
        except Exception as e:
            logging.warning(f"Distributed system not available: {e}")
            distributed_scheduler = None
    return distributed_scheduler

def get_or_create_ultralight_model(model_name: str):
    """Get or create ultralight model with error handling"""
    global ultralight_models
    if ultralight_models[model_name] is None:
        try:
            ultralight_models[model_name] = get_predefined_model(model_name)
            logging.info(f"Initialized ultralight model: {model_name}")
        except Exception as e:
            logging.warning(f"Could not initialize {model_name}: {e}")
            ultralight_models[model_name] = None
    return ultralight_models[model_name]

def save_index():
    """Save BM25 index to disk"""
    try:
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "N": bm25.N,
                "avgdl": bm25.avgdl,
                "df": bm25.df,
                "doc_len": bm25.doc_len,
                "docs": bm25.docs
            }, f, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving index: {e}")

def load_index():
    """Load BM25 index from disk"""
    if not os.path.exists(INDEX_PATH): 
        return
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            obj = json.load(f)
        bm25.N = obj.get("N", 0)
        bm25.avgdl = obj.get("avgdl", 0.0)
        bm25.df = {k:int(v) for k,v in obj.get("df", {}).items()}
        bm25.doc_len = {int(k):int(v) for k,v in obj.get("doc_len", {}).items()}
        bm25.docs = {int(k):v for k,v in obj.get("docs", {}).items()}
    except Exception as e:
        logging.error(f"Error loading index: {e}")

def build_index_from_chunks():
    """Rebuild BM25 index from stored chunks"""
    global bm25
    bm25 = BM25Index()
    for obj in iter_jsonl(CHUNKS_PATH):
        bm25.add_document(
            obj["id"], 
            obj["text"], 
            {"title": obj["title"], "doc_id": obj["doc_id"], "chunk_id": obj["chunk_id"]}
        )
    save_index()

def ingest_text(title: str, text: str, doc_id: int):
    """Process and index text document"""
    global progress
    chunks = make_chunks(text, target_chars=1200, overlap_chars=200)
    total = len(chunks)
    progress = {"status": "indexing", "processed": 0, "total": total}
    
    for i, c in enumerate(chunks, start=1):
        chunk_id = f"{doc_id}_{i}"
        rec = {
            "id": len(bm25.doc_len) + 1, 
            "doc_id": doc_id, 
            "chunk_id": i, 
            "title": title, 
            "text": c["text"]
        }
        append_jsonl(CHUNKS_PATH, rec)
        bm25.add_document(rec["id"], rec["text"], {
            "title": title, 
            "doc_id": doc_id, 
            "chunk_id": i
        })
        
        # Classify document content
        document_classifier.classify_document(rec["id"], title, c["text"])
        
        progress["processed"] = i
    
    save_index()
    progress["status"] = "done"

# Load existing index on startup
load_index()

@app.route("/")
def root():
    """Serve the main interface"""
    return send_from_directory("static", "index.html")

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok", 
        "docs_indexed": bm25.N, 
        "avgdl": bm25.avgdl, 
        "progress": progress
    })

@app.route("/add_txt", methods=["POST"])
def add_txt():
    """Add text document to index"""
    try:
        data = request.form if request.form else request.json
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        title = (data.get("title") or "Untitled Document").strip()
        text = (data.get("text") or "").strip()
        
        if not text:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        doc_id = sum(1 for _ in iter_jsonl(DOCS_PATH)) + 1
        append_jsonl(DOCS_PATH, {"doc_id": doc_id, "title": title, "chars": len(text)})
        threading.Thread(target=ingest_text, args=(title, text, doc_id), daemon=True).start()
        
        return jsonify({"ok": True, "doc_id": doc_id})
    except Exception as e:
        logging.error(f"Error adding text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/add_pdf", methods=["POST"])
def add_pdf():
    """Add PDF document to index"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "Please upload a PDF file"}), 400
        
        f = request.files["file"]
        if f.filename is None or not f.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are supported"}), 400
        
        path = os.path.join(DATA_DIR, f.filename)
        f.save(path)
        text = pdf_to_text(path)
        title = request.form.get("title", f.filename)
        
        doc_id = sum(1 for _ in iter_jsonl(DOCS_PATH)) + 1
        append_jsonl(DOCS_PATH, {"doc_id": doc_id, "title": title, "chars": len(text)})
        threading.Thread(target=ingest_text, args=(title, text, doc_id), daemon=True).start()
        
        return jsonify({"ok": True, "doc_id": doc_id})
    except Exception as e:
        logging.error(f"Error adding PDF: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/progress")
def get_progress():
    """Get document processing progress"""
    return jsonify(progress)

@app.route("/query", methods=["POST"])
def query():
    """Process user query and return results"""
    try:
        payload = request.json or {}
        q = (payload.get("q") or "").strip()
        k = int(payload.get("k", 6))
        
        if not q:
            return jsonify({"error": "Missing query 'q'"}), 400
        
        q_terms = tokenize(q)
        
        # Classify query intent
        intent_scores = intent_classifier.classify(q)
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
        
        # Record query for learning
        learning_system.record_query(q, [], None)
        
        # Get initial results
        ranked = bm25.score(q_terms)
        if not ranked:
            # Generate helpful response based on intent
            no_results_msg = personality_engine.format_response(
                "No documents found. Please add some documents first.",
                "no_results"
            )
            return jsonify({
                "query": q,
                "results": [],
                "summary": no_results_msg,
                "total": 0,
                "intent": primary_intent,
                "suggestions": ["Upload a PDF document", "Add text content", "Try a different query"]
            })
        
        top_ids = [doc_id for doc_id, _ in ranked[:k]]
        top_texts, top_titles = [], []
        
        # Get chunk content for top results
        chunk_map = {}
        for obj in iter_jsonl(CHUNKS_PATH):
            chunk_map[obj["id"]] = obj
        
        for doc_id in top_ids:
            if doc_id in chunk_map:
                chunk = chunk_map[doc_id]
                top_texts.append(chunk["text"])
                top_titles.append(chunk["title"])
        
        # Apply personalization boost
        personalized_ranked = []
        for doc_id, score in ranked:
            if doc_id in chunk_map:
                chunk = chunk_map[doc_id]
                boost = learning_system.get_personalized_boost(q, chunk["title"])
                personalized_score = score * boost
                personalized_ranked.append((doc_id, personalized_score))
        
        # Re-sort with personalized scores
        personalized_ranked.sort(key=lambda x: x[1], reverse=True)
        
        # Generate enhanced summary with personality
        raw_summary = summarize(top_texts[:3], q_terms, max_sents=3) if top_texts else "No relevant content found."
        enhanced_summary = personality_engine.format_response(raw_summary, "search_results")
        
        # Group results intelligently
        result_data = []
        for i, (doc_id, score) in enumerate(personalized_ranked[:k]):
            if doc_id in chunk_map:
                chunk = chunk_map[doc_id]
                category = document_classifier.get_document_category(doc_id)
                
                result_data.append({
                    "rank": i + 1,
                    "title": chunk["title"],
                    "text": chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"],
                    "score": round(score, 3),
                    "doc_id": chunk["doc_id"],
                    "chunk_id": chunk["chunk_id"],
                    "category": category
                })
        
        # Group results by category
        grouped_results = intelligent_grouping.group_search_results(result_data, q)
        
        # Extract key phrases and entities from query
        entities = semantic_analyzer.extract_entities(q)
        key_phrases = semantic_analyzer.extract_key_phrases(q, max_phrases=5)
        
        return jsonify({
            "query": q,
            "results": result_data,
            "grouped_results": grouped_results,
            "summary": enhanced_summary,
            "total": len(personalized_ranked),
            "intent": primary_intent,
            "intent_scores": intent_scores,
            "entities": entities,
            "key_phrases": [phrase for phrase, score in key_phrases],
            "suggestions": advanced_interaction.get_interaction_suggestions()
        })
        
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/feedback", methods=["POST"])
def feedback():
    """Learn from user feedback"""
    try:
        payload = request.json or {}
        q_terms = payload.get("query_terms", [])
        pos_docs = payload.get("positive_docs", [])
        neg_docs = payload.get("negative_docs", [])
        
        if q_terms:
            weights = learner.apply_feedback(q_terms, pos_docs, neg_docs)
            
            # Save feedback for persistence
            feedback_data = {
                "query_terms": q_terms,
                "positive_docs": len(pos_docs),
                "negative_docs": len(neg_docs),
                "weights_updated": len(weights)
            }
            append_jsonl(FEEDBACK_PATH, feedback_data)
            
            return jsonify({"ok": True, "weights_updated": len(weights)})
        
        return jsonify({"error": "Missing query_terms"}), 400
        
    except Exception as e:
        logging.error(f"Error processing feedback: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/personality", methods=["POST"])
def adjust_personality():
    """Adjust AI personality settings"""
    try:
        data = request.json or {}
        
        for trait, value in data.items():
            if trait in personality_engine.personality_traits:
                personality_engine.adjust_trait(trait, float(value))
        
        return jsonify({
            "ok": True, 
            "current_personality": personality_engine.personality_traits
        })
        
    except Exception as e:
        logging.error(f"Error adjusting personality: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze_content():
    """Analyze text content for entities, relationships, and topics"""
    try:
        data = request.json or {}
        text = data.get("text", "")
        
        if not text:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        # Extract entities and relationships
        entities = semantic_analyzer.extract_entities(text)
        relationships = semantic_analyzer.analyze_relationships(text)
        key_phrases = semantic_analyzer.extract_key_phrases(text, max_phrases=10)
        
        # Classify intent if it's a query-like text
        intent_scores = intent_classifier.classify(text)
        
        return jsonify({
            "entities": entities,
            "relationships": relationships,
            "key_phrases": [{"phrase": phrase, "score": score} for phrase, score in key_phrases],
            "intent_classification": intent_scores,
            "word_count": len(text.split()),
            "character_count": len(text)
        })
        
    except Exception as e:
        logging.error(f"Error analyzing content: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/learning/train", methods=["POST"])
def train_learning():
    """Train the system with user feedback"""
    try:
        data = request.json or {}
        query = data.get("query", "")
        feedback_type = data.get("type", "")  # 'positive', 'negative', 'intent'
        content = data.get("content", "")
        
        if feedback_type == "intent" and query:
            intent = data.get("intent", "question")
            strength = data.get("strength", 1.0)
            intent_classifier.train(query, intent, strength)
            
            return jsonify({"ok": True, "message": f"Trained intent classifier for '{intent}'"})
        
        elif feedback_type in ["positive", "negative"] and query:
            if feedback_type == "positive":
                learning_system.learn_from_feedback(query, [content], [])
            else:
                learning_system.learn_from_feedback(query, [], [content])
            
            return jsonify({"ok": True, "message": f"Recorded {feedback_type} feedback"})
        
        return jsonify({"error": "Invalid training data"}), 400
        
    except Exception as e:
        logging.error(f"Error training system: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/stats/advanced")
def advanced_stats():
    """Get advanced system statistics"""
    try:
        stats = {
            "basic": {
                "docs_indexed": bm25.N,
                "avg_document_length": round(bm25.avgdl, 2),
                "vocabulary_size": len(bm25.df)
            },
            "learning": {
                "queries_processed": len(learning_system.query_history),
                "frequent_queries": learning_system.get_frequent_queries(5),
                "topic_interests": dict(list(learning_system.topic_interests.items())[:10])
            },
            "personality": {
                "current_traits": personality_engine.personality_traits
            },
            "categories": {},
            "advanced_features": {
                "voice_enabled": advanced_interaction.voice.voice_enabled,
                "gesture_enabled": advanced_interaction.gestures.gesture_enabled,
                "display_mode": advanced_interaction.holo_display.display_mode
            }
        }
        
        # Get category distribution
        if hasattr(document_classifier, 'document_categories'):
            category_counts = {}
            for doc_categories in document_classifier.document_categories.values():
                max_category = max(doc_categories.items(), key=lambda x: x[1])[0] if doc_categories else 'general'
                category_counts[max_category] = category_counts.get(max_category, 0) + 1
            stats["categories"] = category_counts
        
        return jsonify(stats)
        
    except Exception as e:
        logging.error(f"Error getting advanced stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/voice/setup", methods=["POST"])
def setup_voice():
    """Setup voice interaction features"""
    try:
        data = request.json or {}
        
        # Configure voice settings
        if "settings" in data:
            advanced_interaction.voice.configure_voice(data["settings"])
        
        # Initialize features
        setup_results = advanced_interaction.initialize_advanced_features()
        
        return jsonify({
            "ok": True,
            "features_initialized": setup_results,
            "voice_settings": advanced_interaction.voice.voice_settings,
            "suggestions": advanced_interaction.get_interaction_suggestions()
        })
        
    except Exception as e:
        logging.error(f"Error setting up voice: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/hud/config", methods=["GET", "POST"])
def hud_configuration():
    """Configure HUD display settings"""
    try:
        if request.method == "POST":
            data = request.json or {}
            
            if "display_mode" in data:
                advanced_interaction.holo_display.set_display_mode(data["display_mode"])
            
            if "elements" in data:
                for element, enabled in data["elements"].items():
                    advanced_interaction.holo_display.toggle_hud_element(element, enabled)
        
        return jsonify({
            "current_config": advanced_interaction.holo_display.get_hud_config(),
            "available_modes": ["windowed", "floating", "fullscreen", "hud"],
            "available_elements": list(advanced_interaction.holo_display.hud_elements.keys())
        })
        
    except Exception as e:
        logging.error(f"Error configuring HUD: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/distributed/status")
def distributed_status():
    """Get distributed computing system status"""
    try:
        scheduler = get_or_create_distributed_scheduler()
        if scheduler:
            stats = scheduler.get_system_stats()
            return jsonify({
                "distributed_enabled": True,
                "system_stats": stats,
                "scheduler_running": scheduler.running
            })
        else:
            return jsonify({
                "distributed_enabled": False,
                "message": "Distributed system not available - running in standalone mode"
            })
            
    except Exception as e:
        logging.error(f"Error getting distributed status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/distributed/submit", methods=["POST"])
def submit_distributed_task():
    """Submit a task to the distributed computing system"""
    try:
        scheduler = get_or_create_distributed_scheduler()
        if not scheduler:
            return jsonify({"error": "Distributed system not available"}), 503
            
        data = request.json or {}
        task_type = data.get("task_type", "")
        task_data = data.get("data", {})
        priority = data.get("priority", 0)
        
        if not task_type or task_type not in [t.value for t in TaskType]:
            return jsonify({"error": "Invalid or missing task_type"}), 400
            
        task = create_distributed_task(task_type, task_data, priority=priority)
        task_id = scheduler.submit_task(task)
        
        return jsonify({
            "ok": True,
            "task_id": task_id,
            "message": f"Task submitted to distributed system"
        })
        
    except Exception as e:
        logging.error(f"Error submitting distributed task: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/distributed/result/<task_id>")
def get_distributed_result(task_id):
    """Get result of a distributed task"""
    try:
        scheduler = get_or_create_distributed_scheduler()
        if not scheduler:
            return jsonify({"error": "Distributed system not available"}), 503
            
        result = scheduler.get_task_result(task_id)
        
        if result is None:
            # Check if task is still running
            if task_id in scheduler.running_tasks:
                return jsonify({
                    "status": "running",
                    "message": "Task is still being processed"
                })
            elif task_id in scheduler.failed_tasks:
                return jsonify({
                    "status": "failed",
                    "error": scheduler.failed_tasks[task_id]
                }), 500
            else:
                return jsonify({"error": "Task not found"}), 404
                
        return jsonify({
            "status": "completed",
            "result": result
        })
        
    except Exception as e:
        logging.error(f"Error getting distributed result: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/models/ultralight")
def ultralight_models_status():
    """Get status of ultra-light neural networks"""
    try:
        model_status = {}
        
        for model_name in ultralight_models.keys():
            model = get_or_create_ultralight_model(model_name)
            
            if model:
                if hasattr(model, 'is_trained'):
                    model_status[model_name] = {
                        "loaded": True,
                        "trained": model.is_trained,
                        "type": type(model).__name__
                    }
                elif hasattr(model, 'update_count'):
                    model_status[model_name] = {
                        "loaded": True,
                        "updates": model.update_count,
                        "type": type(model).__name__
                    }
                else:
                    model_status[model_name] = {
                        "loaded": True,
                        "type": type(model).__name__
                    }
            else:
                model_status[model_name] = {
                    "loaded": False,
                    "error": "Failed to initialize"
                }
        
        return jsonify({
            "models": model_status,
            "available_models": list(PREDEFINED_MODELS.keys())
        })
        
    except Exception as e:
        logging.error(f"Error getting ultralight models status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/models/train", methods=["POST"])
def train_ultralight_model():
    """Train an ultra-light neural network"""
    try:
        data = request.json or {}
        model_name = data.get("model_name", "")
        training_data = data.get("data", [])
        labels = data.get("labels", [])
        epochs = data.get("epochs", 50)
        
        if not model_name or model_name not in ultralight_models:
            return jsonify({"error": "Invalid model name"}), 400
            
        if not training_data or not labels:
            return jsonify({"error": "Missing training data or labels"}), 400
            
        model = get_or_create_ultralight_model(model_name)
        if not model:
            return jsonify({"error": f"Could not initialize {model_name}"}), 500
        
        # Convert data to numpy arrays
        import numpy as np
        X = np.array(training_data, dtype=np.float32)
        y = np.array(labels, dtype=np.float32)
        
        # Train the model
        if hasattr(model, 'train'):
            model.train(X, y, epochs=epochs)
            training_history = getattr(model, 'training_history', [])
            
            return jsonify({
                "ok": True,
                "message": f"Model {model_name} trained successfully",
                "epochs": epochs,
                "final_loss": training_history[-1] if training_history else None,
                "training_samples": len(X)
            })
        elif hasattr(model, 'fit'):
            model.fit(X, y, epochs=epochs)
            
            return jsonify({
                "ok": True,
                "message": f"Model {model_name} trained successfully",
                "epochs": epochs,
                "training_samples": len(X)
            })
        else:
            return jsonify({"error": f"Model {model_name} does not support training"}), 400
            
    except Exception as e:
        logging.error(f"Error training ultralight model: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/models/predict", methods=["POST"])
def predict_ultralight_model():
    """Make predictions with ultra-light neural networks"""
    try:
        data = request.json or {}
        model_name = data.get("model_name", "")
        input_data = data.get("data", [])
        
        if not model_name or model_name not in ultralight_models:
            return jsonify({"error": "Invalid model name"}), 400
            
        if not input_data:
            return jsonify({"error": "Missing input data"}), 400
            
        model = get_or_create_ultralight_model(model_name)
        if not model:
            return jsonify({"error": f"Could not initialize {model_name}"}), 500
        
        # Convert data to numpy array
        import numpy as np
        X = np.array(input_data, dtype=np.float32)
        
        # Make predictions
        if hasattr(model, 'predict'):
            predictions = model.predict(X)
            
            # Convert numpy arrays to lists for JSON serialization
            if isinstance(predictions, np.ndarray):
                predictions = predictions.tolist()
                
            return jsonify({
                "predictions": predictions,
                "model_used": model_name,
                "input_shape": X.shape
            })
        else:
            return jsonify({"error": f"Model {model_name} does not support prediction"}), 400
            
    except Exception as e:
        logging.error(f"Error making predictions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/system/farm")
def render_farm_dashboard():
    """Get render farm style dashboard data"""
    try:
        # Get basic system stats
        basic_stats = {
            "docs_indexed": bm25.N,
            "vocab_size": len(bm25.df),
            "avg_doc_length": round(bm25.avgdl, 2),
            "system_status": "ready"
        }
        
        # Get distributed system stats if available
        distributed_stats = {}
        scheduler = get_or_create_distributed_scheduler()
        if scheduler:
            distributed_stats = scheduler.get_system_stats()
        
        # Get model stats
        model_stats = {}
        for model_name in ultralight_models.keys():
            model = ultralight_models.get(model_name)
            if model:
                if hasattr(model, 'is_trained'):
                    model_stats[model_name] = {"trained": model.is_trained}
                elif hasattr(model, 'update_count'):
                    model_stats[model_name] = {"updates": model.update_count}
                else:
                    model_stats[model_name] = {"status": "loaded"}
                    
        # Get advanced learning stats
        learning_stats = {
            "queries_processed": len(learning_system.query_history) if hasattr(learning_system, 'query_history') else 0,
            "personality_traits": personality_engine.personality_traits if hasattr(personality_engine, 'personality_traits') else {},
            "neural_features_active": bool(intent_classifier and document_classifier)
        }
        
        return jsonify({
            "basic": basic_stats,
            "distributed": distributed_stats,
            "models": model_stats,
            "learning": learning_stats,
            "render_farm_style": {
                "total_compute_nodes": 1 + (len(distributed_stats.get('workers', {}).get('active', [])) if distributed_stats else 0),
                "processing_capacity": "Ultra-Light AI Optimized",
                "memory_efficiency": "Low Resource Consumption",
                "inference_speed": "Sub-millisecond"
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting render farm dashboard: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
