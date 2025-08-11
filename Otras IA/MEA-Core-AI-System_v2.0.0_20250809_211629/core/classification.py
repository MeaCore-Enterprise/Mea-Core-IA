"""
Document classification and semantic analysis for MEA-Core
Automatic topic detection and intelligent document organization
"""
import json
import math
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
from .tokenize import tokenize

class DocumentClassifier:
    """Classify documents into topics and categories"""
    
    def __init__(self):
        self.topic_models = {}
        self.document_categories = {}
        self.topic_vocabulary = defaultdict(set)
        self.category_keywords = {
            'legal': {
                'spanish': ['contrato', 'ley', 'derecho', 'legal', 'jurídico', 'tribunal', 
                          'demanda', 'sentencia', 'código', 'artículo', 'normativa'],
                'english': ['contract', 'law', 'legal', 'court', 'lawsuit', 'judgment',
                          'regulation', 'statute', 'agreement', 'litigation', 'clause']
            },
            'medical': {
                'spanish': ['médico', 'salud', 'enfermedad', 'tratamiento', 'diagnóstico',
                          'hospital', 'paciente', 'síntoma', 'medicina', 'clínico'],
                'english': ['medical', 'health', 'disease', 'treatment', 'diagnosis',
                          'hospital', 'patient', 'symptom', 'medicine', 'clinical']
            },
            'technical': {
                'spanish': ['técnico', 'sistema', 'software', 'programa', 'código',
                          'datos', 'algoritmo', 'tecnología', 'digital', 'informática'],
                'english': ['technical', 'system', 'software', 'program', 'code',
                          'data', 'algorithm', 'technology', 'digital', 'computer']
            },
            'financial': {
                'spanish': ['financiero', 'dinero', 'banco', 'crédito', 'inversión',
                          'económico', 'precio', 'costo', 'presupuesto', 'factura'],
                'english': ['financial', 'money', 'bank', 'credit', 'investment',
                          'economic', 'price', 'cost', 'budget', 'invoice']
            },
            'educational': {
                'spanish': ['educación', 'estudiante', 'curso', 'universidad', 'aprender',
                          'enseñar', 'profesor', 'clase', 'estudio', 'académico'],
                'english': ['education', 'student', 'course', 'university', 'learn',
                          'teach', 'professor', 'class', 'study', 'academic']
            }
        }
    
    def classify_document(self, doc_id: int, title: str, content: str) -> Dict[str, float]:
        """Classify document into categories with confidence scores"""
        tokens = tokenize(content.lower())
        title_tokens = tokenize(title.lower())
        all_tokens = tokens + title_tokens
        
        category_scores = {}
        
        for category, languages in self.category_keywords.items():
            score = 0.0
            total_keywords = 0
            
            for lang, keywords in languages.items():
                keyword_matches = sum(1 for token in all_tokens if token in keywords)
                total_keywords += len(keywords)
                
                # Weight title matches higher
                title_matches = sum(1 for token in title_tokens if token in keywords)
                score += keyword_matches + (title_matches * 2)
            
            # Normalize by document length and keyword count
            if all_tokens and total_keywords:
                normalized_score = score / (len(all_tokens) * 0.01 + total_keywords * 0.1)
                category_scores[category] = min(normalized_score, 1.0)
            else:
                category_scores[category] = 0.0
        
        # Store classification
        self.document_categories[doc_id] = category_scores
        
        return category_scores
    
    def get_document_category(self, doc_id: int) -> str:
        """Get primary category for document"""
        if doc_id not in self.document_categories:
            return 'general'
        
        scores = self.document_categories[doc_id]
        if not scores:
            return 'general'
        
        max_category = max(scores.items(), key=lambda x: x[1])
        
        # Only return category if confidence is high enough
        if max_category[1] > 0.1:
            return max_category[0]
        
        return 'general'
    
    def get_similar_documents(self, doc_id: int, limit: int = 5) -> List[Tuple[int, float]]:
        """Find similar documents based on category scores"""
        if doc_id not in self.document_categories:
            return []
        
        target_scores = self.document_categories[doc_id]
        similarities = []
        
        for other_doc_id, other_scores in self.document_categories.items():
            if other_doc_id == doc_id:
                continue
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(target_scores, other_scores)
            similarities.append((other_doc_id, similarity))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
    
    def _cosine_similarity(self, scores1: Dict[str, float], scores2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two category score vectors"""
        # Get all categories
        all_categories = set(scores1.keys()) | set(scores2.keys())
        
        # Create vectors
        vec1 = [scores1.get(cat, 0.0) for cat in all_categories]
        vec2 = [scores2.get(cat, 0.0) for cat in all_categories]
        
        # Calculate dot product and magnitudes
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(v * v for v in vec1))
        magnitude2 = math.sqrt(sum(v * v for v in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

class SemanticAnalyzer:
    """Basic semantic analysis for better understanding"""
    
    def __init__(self):
        self.entity_patterns = {
            'person': ['sr.', 'sra.', 'dr.', 'prof.', 'ing.', 'mr.', 'mrs.', 'dr.', 'prof.'],
            'organization': ['s.a.', 'ltda.', 'inc.', 'corp.', 'ltd.', 'co.', 'company', 'empresa'],
            'location': ['ciudad', 'país', 'estado', 'provincia', 'región', 'city', 'country', 'state'],
            'date': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                    'january', 'february', 'march', 'april', 'may', 'june'],
            'money': ['$', '€', '£', '¥', 'peso', 'dollar', 'euro', 'pound']
        }
        
        self.relationship_patterns = {
            'cause_effect': ['porque', 'debido a', 'resulta en', 'causa', 'because', 'due to', 'results in'],
            'comparison': ['mejor que', 'peor que', 'similar a', 'como', 'better than', 'worse than', 'similar to'],
            'temporal': ['antes', 'después', 'durante', 'cuando', 'before', 'after', 'during', 'when'],
            'conditional': ['si', 'entonces', 'a menos que', 'if', 'then', 'unless']
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        tokens = text.split()
        entities = defaultdict(list)
        
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            
            # Check entity patterns
            for entity_type, patterns in self.entity_patterns.items():
                if any(pattern in token_lower for pattern in patterns):
                    # Include surrounding context
                    context_start = max(0, i - 1)
                    context_end = min(len(tokens), i + 2)
                    entity_phrase = ' '.join(tokens[context_start:context_end])
                    entities[entity_type].append(entity_phrase)
        
        return dict(entities)
    
    def analyze_relationships(self, text: str) -> List[Dict[str, str]]:
        """Identify semantic relationships in text"""
        relationships = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            for rel_type, patterns in self.relationship_patterns.items():
                for pattern in patterns:
                    if pattern in sentence.lower():
                        parts = sentence.lower().split(pattern, 1)
                        if len(parts) == 2:
                            relationships.append({
                                'type': rel_type,
                                'pattern': pattern,
                                'subject': parts[0].strip(),
                                'object': parts[1].strip(),
                                'full_sentence': sentence
                            })
                            break
        
        return relationships
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[Tuple[str, float]]:
        """Extract key phrases with importance scores"""
        sentences = text.split('.')
        phrase_scores = defaultdict(float)
        
        for sentence in sentences:
            tokens = tokenize(sentence.lower())
            
            # Generate n-grams (2-4 words)
            for n in range(2, 5):
                for i in range(len(tokens) - n + 1):
                    phrase = ' '.join(tokens[i:i+n])
                    
                    # Skip if contains only common words
                    if self._is_meaningful_phrase(phrase):
                        # Score based on frequency and position
                        phrase_scores[phrase] += 1.0
        
        # Sort by score and return top phrases
        sorted_phrases = sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_phrases[:max_phrases]
    
    def _is_meaningful_phrase(self, phrase: str) -> bool:
        """Check if phrase is meaningful (not just stop words)"""
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo',
                     'the', 'of', 'and', 'to', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 'for'}
        
        tokens = phrase.split()
        meaningful_tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
        
        return len(meaningful_tokens) >= len(tokens) * 0.5

class TopicModeling:
    """Simple topic modeling using term clustering"""
    
    def __init__(self, num_topics: int = 10):
        self.num_topics = num_topics
        self.topics = {}
        self.document_topics = {}
        self.topic_terms = defaultdict(Counter)
        self.term_document_freq = defaultdict(int)
        self.document_count = 0
    
    def train_topics(self, documents: List[Tuple[int, str]]):
        """Train topic model on documents"""
        self.document_count = len(documents)
        
        # Calculate term frequencies
        all_terms = set()
        doc_term_freq = {}
        
        for doc_id, content in documents:
            tokens = tokenize(content.lower())
            term_freq = Counter(tokens)
            doc_term_freq[doc_id] = term_freq
            all_terms.update(tokens)
            
            # Update document frequency for each unique term
            for term in set(tokens):
                self.term_document_freq[term] += 1
        
        # Calculate TF-IDF for each document
        doc_tfidf = {}
        for doc_id, term_freq in doc_term_freq.items():
            tfidf = {}
            for term, tf in term_freq.items():
                df = self.term_document_freq[term]
                idf = math.log(self.document_count / (df + 1))
                tfidf[term] = tf * idf
            doc_tfidf[doc_id] = tfidf
        
        # Simple clustering based on term similarity
        self._cluster_documents(doc_tfidf)
    
    def _cluster_documents(self, doc_tfidf: Dict[int, Dict[str, float]]):
        """Simple document clustering into topics"""
        import random
        
        # Initialize random centroids
        all_terms = set()
        for terms in doc_tfidf.values():
            all_terms.update(terms.keys())
        
        all_terms = list(all_terms)
        centroids = {}
        
        for topic_id in range(self.num_topics):
            # Random selection of terms for initial centroids
            centroid_terms = random.sample(all_terms, min(20, len(all_terms)))
            centroids[topic_id] = {term: random.uniform(0.1, 1.0) for term in centroid_terms}
        
        # Simple assignment based on similarity
        for doc_id, tfidf in doc_tfidf.items():
            best_topic = 0
            best_score = 0
            
            for topic_id, centroid in centroids.items():
                score = self._calculate_similarity(tfidf, centroid)
                if score > best_score:
                    best_score = score
                    best_topic = topic_id
            
            self.document_topics[doc_id] = best_topic
            
            # Update topic terms
            for term, score in tfidf.items():
                if score > 0.1:  # Only significant terms
                    self.topic_terms[best_topic][term] += score
    
    def _calculate_similarity(self, doc_tfidf: Dict[str, float], centroid: Dict[str, float]) -> float:
        """Calculate similarity between document and topic centroid"""
        common_terms = set(doc_tfidf.keys()) & set(centroid.keys())
        if not common_terms:
            return 0.0
        
        similarity = sum(doc_tfidf[term] * centroid[term] for term in common_terms)
        return similarity / len(common_terms)
    
    def get_document_topic(self, doc_id: int) -> int:
        """Get primary topic for document"""
        return self.document_topics.get(doc_id, 0)
    
    def get_topic_terms(self, topic_id: int, limit: int = 10) -> List[Tuple[str, float]]:
        """Get top terms for topic"""
        if topic_id not in self.topic_terms:
            return []
        
        terms = self.topic_terms[topic_id]
        sorted_terms = sorted(terms.items(), key=lambda x: x[1], reverse=True)
        return sorted_terms[:limit]
    
    def get_related_documents(self, doc_id: int, limit: int = 5) -> List[int]:
        """Get documents from same topic"""
        doc_topic = self.get_document_topic(doc_id)
        
        related_docs = [
            other_doc_id for other_doc_id, topic in self.document_topics.items()
            if topic == doc_topic and other_doc_id != doc_id
        ]
        
        return related_docs[:limit]

class IntelligentGrouping:
    """Intelligent document and result grouping"""
    
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.semantic_analyzer = SemanticAnalyzer()
        self.topic_model = TopicModeling()
    
    def group_search_results(self, results: List[Dict], query: str) -> Dict[str, List[Dict]]:
        """Group search results intelligently"""
        if not results:
            return {'general': results}
        
        groups = defaultdict(list)
        
        for result in results:
            doc_id = result.get('doc_id', 0)
            title = result.get('title', '')
            text = result.get('text', '')
            
            # Get document category
            if hasattr(self, '_cached_categories') and doc_id in self._cached_categories:
                category = self._cached_categories[doc_id]
            else:
                category_scores = self.classifier.classify_document(doc_id, title, text)
                category = max(category_scores.items(), key=lambda x: x[1])[0] if category_scores else 'general'
            
            # Add to appropriate group
            groups[category].append(result)
        
        return dict(groups)
    
    def analyze_document_collection(self, documents: List[Tuple[int, str, str]]) -> Dict[str, any]:
        """Analyze entire document collection"""
        analysis = {
            'total_documents': len(documents),
            'categories': defaultdict(int),
            'topics': {},
            'entities': defaultdict(list),
            'key_phrases': [],
            'relationships': []
        }
        
        # Classify all documents
        all_entities = defaultdict(list)
        all_relationships = []
        
        for doc_id, title, content in documents:
            # Classify document
            category_scores = self.classifier.classify_document(doc_id, title, content)
            primary_category = max(category_scores.items(), key=lambda x: x[1])[0] if category_scores else 'general'
            analysis['categories'][primary_category] += 1
            
            # Extract entities and relationships
            entities = self.semantic_analyzer.extract_entities(content)
            for entity_type, entity_list in entities.items():
                all_entities[entity_type].extend(entity_list)
            
            relationships = self.semantic_analyzer.analyze_relationships(content)
            all_relationships.extend(relationships)
        
        # Train topic model
        doc_contents = [(doc_id, content) for doc_id, title, content in documents]
        self.topic_model.train_topics(doc_contents)
        
        # Get topic information
        for topic_id in range(self.topic_model.num_topics):
            topic_terms = self.topic_model.get_topic_terms(topic_id)
            if topic_terms:
                analysis['topics'][f'topic_{topic_id}'] = topic_terms
        
        # Aggregate entities and relationships
        analysis['entities'] = {k: list(set(v)) for k, v in all_entities.items()}
        analysis['relationships'] = all_relationships[:50]  # Top 50 relationships
        
        return analysis