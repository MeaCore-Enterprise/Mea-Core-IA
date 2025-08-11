"""
Simple neural network implementation for MEA-Core
Local training without external dependencies
"""
import json
import math
import random
from typing import List, Dict, Tuple
from .tokenize import tokenize

class SimplePerceptron:
    """Basic perceptron for intent classification and response scoring"""
    
    def __init__(self, input_size: int, learning_rate: float = 0.1):
        self.weights = [random.uniform(-0.5, 0.5) for _ in range(input_size)]
        self.bias = random.uniform(-0.5, 0.5)
        self.learning_rate = learning_rate
        self.input_size = input_size
    
    def predict(self, inputs: List[float]) -> float:
        """Forward pass - compute weighted sum + bias"""
        if len(inputs) != self.input_size:
            inputs = inputs[:self.input_size] + [0.0] * (self.input_size - len(inputs))
        
        weighted_sum = sum(w * x for w, x in zip(self.weights, inputs))
        return self.sigmoid(weighted_sum + self.bias)
    
    def train_step(self, inputs: List[float], target: float) -> float:
        """Single training step with gradient descent"""
        prediction = self.predict(inputs)
        error = target - prediction
        
        # Update weights and bias
        for i in range(len(self.weights)):
            if i < len(inputs):
                self.weights[i] += self.learning_rate * error * inputs[i] * prediction * (1 - prediction)
        
        self.bias += self.learning_rate * error * prediction * (1 - prediction)
        return abs(error)
    
    @staticmethod
    def sigmoid(x: float) -> float:
        """Sigmoid activation function"""
        return 1 / (1 + math.exp(-max(-500, min(500, x))))  # Clamp to prevent overflow

class IntentClassifier:
    """Classify user queries into intents: question, search, command"""
    
    def __init__(self):
        self.feature_size = 20
        self.classifiers = {
            'question': SimplePerceptron(self.feature_size),
            'search': SimplePerceptron(self.feature_size),
            'command': SimplePerceptron(self.feature_size)
        }
        self.vocabulary = set()
        self.intent_patterns = {
            'question': ['qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'quién', 'cuál',
                        'what', 'how', 'when', 'where', 'why', 'who', 'which', '?'],
            'search': ['busca', 'encuentra', 'muestra', 'dame', 'lista', 'ver',
                      'search', 'find', 'show', 'list', 'get', 'display'],
            'command': ['abre', 'ejecuta', 'borra', 'elimina', 'crear', 'hacer',
                       'open', 'run', 'delete', 'remove', 'create', 'make', 'add']
        }
        
        # Pre-populate vocabulary
        for patterns in self.intent_patterns.values():
            self.vocabulary.update(patterns)
    
    def extract_features(self, text: str) -> List[float]:
        """Extract numerical features from text"""
        tokens = tokenize(text.lower())
        features = []
        
        # Pattern matching features
        for intent, patterns in self.intent_patterns.items():
            pattern_score = sum(1 for token in tokens if token in patterns) / len(tokens) if tokens else 0
            features.append(pattern_score)
        
        # Text statistics
        features.extend([
            len(tokens) / 20,  # Normalized length
            text.count('?') / len(text) if text else 0,  # Question marks
            text.count('!') / len(text) if text else 0,  # Exclamation marks
            sum(1 for word in tokens if word in self.vocabulary) / len(tokens) if tokens else 0
        ])
        
        # Pad or truncate to feature_size
        while len(features) < self.feature_size:
            features.append(0.0)
        
        return features[:self.feature_size]
    
    def classify(self, text: str) -> Dict[str, float]:
        """Classify text into intent probabilities"""
        features = self.extract_features(text)
        scores = {}
        
        for intent, classifier in self.classifiers.items():
            scores[intent] = classifier.predict(features)
        
        return scores
    
    def train(self, text: str, intent: str, strength: float = 1.0):
        """Train classifier with user feedback"""
        features = self.extract_features(text)
        
        for intent_name, classifier in self.classifiers.items():
            target = strength if intent_name == intent else 0.0
            classifier.train_step(features, target)

class PersonalityEngine:
    """Manages AI personality and response tone"""
    
    def __init__(self):
        self.personality_traits = {
            'formality': 0.5,      # 0=casual, 1=formal
            'technicality': 0.5,   # 0=simple, 1=technical
            'verbosity': 0.5,      # 0=concise, 1=verbose
            'enthusiasm': 0.5,     # 0=neutral, 1=excited
            'helpfulness': 0.8     # 0=minimal, 1=helpful
        }
        
        self.response_templates = {
            'greeting': {
                'casual': ["¡Hola! ¿En qué puedo ayudarte?", "Hey, ¿qué necesitas?"],
                'formal': ["Buenos días. ¿Cómo puedo asistirle?", "Saludos. ¿En qué puedo ser de ayuda?"]
            },
            'search_results': {
                'enthusiastic': ["¡Encontré información relevante!", "¡Perfecto! Aquí tienes los resultados:"],
                'neutral': ["Resultados de búsqueda:", "Información encontrada:"]
            },
            'no_results': {
                'helpful': ["No encontré resultados, pero puedes intentar:", "Sin resultados. Te sugiero:"],
                'minimal': ["Sin resultados.", "No encontrado."]
            }
        }
    
    def adjust_trait(self, trait: str, value: float):
        """Adjust personality trait (0.0 to 1.0)"""
        if trait in self.personality_traits:
            self.personality_traits[trait] = max(0.0, min(1.0, value))
    
    def get_response_style(self, context: str) -> Dict[str, str]:
        """Get appropriate response style based on personality"""
        style = {}
        
        if self.personality_traits['formality'] > 0.6:
            style['tone'] = 'formal'
        else:
            style['tone'] = 'casual'
        
        if self.personality_traits['enthusiasm'] > 0.6:
            style['energy'] = 'enthusiastic'
        else:
            style['energy'] = 'neutral'
            
        if self.personality_traits['helpfulness'] > 0.7:
            style['assistance'] = 'helpful'
        else:
            style['assistance'] = 'minimal'
        
        return style
    
    def format_response(self, content: str, response_type: str) -> str:
        """Format response based on personality"""
        style = self.get_response_style(response_type)
        
        # Select appropriate template
        if response_type in self.response_templates:
            templates = self.response_templates[response_type]
            
            # Choose template based on style
            for style_key, style_value in style.items():
                if style_value in templates:
                    prefix = random.choice(templates[style_value])
                    return f"{prefix}\n\n{content}"
        
        return content

class LearningSystem:
    """Manages continuous learning from user interactions"""
    
    def __init__(self):
        self.user_preferences = {}
        self.query_history = []
        self.response_feedback = {}
        self.topic_interests = {}
        
    def record_query(self, query: str, results: List[Dict], feedback: str = None):
        """Record user query and results for learning"""
        self.query_history.append({
            'query': query,
            'timestamp': self._get_timestamp(),
            'results_count': len(results),
            'feedback': feedback
        })
        
        # Track topic interests
        tokens = tokenize(query.lower())
        for token in tokens:
            if len(token) > 3:  # Ignore short words
                self.topic_interests[token] = self.topic_interests.get(token, 0) + 1
    
    def learn_from_feedback(self, query: str, positive_docs: List[str], negative_docs: List[str]):
        """Learn from explicit user feedback"""
        query_key = query.lower().strip()
        
        if query_key not in self.response_feedback:
            self.response_feedback[query_key] = {'positive': [], 'negative': []}
        
        self.response_feedback[query_key]['positive'].extend(positive_docs)
        self.response_feedback[query_key]['negative'].extend(negative_docs)
    
    def get_personalized_boost(self, query: str, doc_title: str) -> float:
        """Calculate personalization boost for document relevance"""
        boost = 1.0
        
        # Boost based on topic interests
        query_tokens = set(tokenize(query.lower()))
        title_tokens = set(tokenize(doc_title.lower()))
        
        for token in query_tokens.intersection(title_tokens):
            interest_score = self.topic_interests.get(token, 0)
            boost += interest_score * 0.1
        
        return min(boost, 2.0)  # Cap at 2x boost
    
    def get_frequent_queries(self, limit: int = 10) -> List[str]:
        """Get most frequent user queries"""
        query_counts = {}
        for entry in self.query_history:
            query = entry['query'].lower().strip()
            query_counts[query] = query_counts.get(query, 0) + 1
        
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [query for query, count in sorted_queries[:limit]]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        import time
        return str(int(time.time()))