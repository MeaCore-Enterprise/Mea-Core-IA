"""
MEA-Core Ultra-Light Neural Networks
Lightweight neural networks optimized for resource-constrained environments
"""

import numpy as np
import json
import pickle
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import threading
from pathlib import Path

# Simple activation functions
def relu(x):
    return np.maximum(0, x)

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def tanh(x):
    return np.tanh(x)

def softmax(x):
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

def silu(x):
    """SiLU/Swish activation function"""
    return x * sigmoid(x)

@dataclass
class ModelConfig:
    input_dim: int
    hidden_dims: List[int]
    output_dim: int
    activation: str = 'relu'
    use_bias: bool = True
    dropout_rate: float = 0.0
    quantization: str = 'none'  # 'none', 'int8', 'int4'
    
class BaseNeuralNetwork(ABC):
    """Base class for ultra-light neural networks"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.weights = []
        self.biases = []
        self.is_trained = False
        self.training_history = []
        
        # Activation function mapping
        self.activation_funcs = {
            'relu': relu,
            'sigmoid': sigmoid, 
            'tanh': tanh,
            'silu': silu
        }
        
        self.activation = self.activation_funcs.get(config.activation, relu)
        
    @abstractmethod
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass through the network"""
        pass
        
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100):
        """Train the network"""
        pass
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        return self.forward(X)
        
    def save(self, path: str):
        """Save model to disk"""
        model_data = {
            'config': self.config,
            'weights': [w.tolist() for w in self.weights],
            'biases': [b.tolist() for b in self.biases] if self.biases else [],
            'is_trained': self.is_trained,
            'training_history': self.training_history
        }
        
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)
            
    @classmethod
    def load(cls, path: str):
        """Load model from disk"""
        with open(path, 'r') as f:
            model_data = json.load(f)
            
        config = ModelConfig(**model_data['config'])
        model = cls(config)
        
        model.weights = [np.array(w) for w in model_data['weights']]
        model.biases = [np.array(b) for b in model_data['biases']] if model_data['biases'] else []
        model.is_trained = model_data['is_trained']
        model.training_history = model_data['training_history']
        
        return model

class UltraLightMLP(BaseNeuralNetwork):
    """Ultra-light Multi-Layer Perceptron optimized for CPU inference"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization"""
        layer_dims = [self.config.input_dim] + self.config.hidden_dims + [self.config.output_dim]
        
        self.weights = []
        self.biases = []
        
        for i in range(len(layer_dims) - 1):
            # Xavier initialization
            limit = np.sqrt(6.0 / (layer_dims[i] + layer_dims[i + 1]))
            weight = np.random.uniform(-limit, limit, (layer_dims[i], layer_dims[i + 1]))
            
            self.weights.append(weight.astype(np.float32))
            
            if self.config.use_bias:
                bias = np.zeros(layer_dims[i + 1], dtype=np.float32)
                self.biases.append(bias)
                
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass with optimized matrix operations"""
        if x.ndim == 1:
            x = x.reshape(1, -1)
            
        current = x.astype(np.float32)
        
        # Hidden layers
        for i in range(len(self.weights) - 1):
            current = np.dot(current, self.weights[i])
            
            if self.config.use_bias and i < len(self.biases):
                current += self.biases[i]
                
            current = self.activation(current)
            
            # Simple dropout during training
            if hasattr(self, 'training') and self.training and self.config.dropout_rate > 0:
                mask = np.random.random(current.shape) > self.config.dropout_rate
                current = current * mask / (1 - self.config.dropout_rate)
        
        # Output layer (no activation for regression, softmax for classification)
        output = np.dot(current, self.weights[-1])
        if self.config.use_bias and len(self.biases) == len(self.weights):
            output += self.biases[-1]
            
        return output
        
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, 
              learning_rate: float = 0.001, batch_size: int = 32, verbose: bool = True):
        """Simple SGD training with momentum"""
        self.training = True
        
        X = X.astype(np.float32)
        y = y.astype(np.float32)
        
        if y.ndim == 1 and self.config.output_dim > 1:
            # Convert to one-hot encoding for classification
            y_onehot = np.zeros((len(y), self.config.output_dim))
            y_onehot[np.arange(len(y)), y.astype(int)] = 1
            y = y_onehot
            
        # Initialize momentum terms
        momentum = 0.9
        weight_velocities = [np.zeros_like(w) for w in self.weights]
        bias_velocities = [np.zeros_like(b) for b in self.biases] if self.biases else []
        
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            total_loss = 0.0
            n_batches = 0
            
            # Mini-batch training
            for i in range(0, n_samples, batch_size):
                batch_X = X_shuffled[i:i + batch_size]
                batch_y = y_shuffled[i:i + batch_size]
                
                # Forward pass
                predictions = self.forward(batch_X)
                
                # Compute loss (MSE for regression, cross-entropy for classification)
                if self.config.output_dim == 1:
                    loss = np.mean((predictions - batch_y) ** 2)
                    output_grad = 2 * (predictions - batch_y) / len(batch_y)
                else:
                    # Softmax + cross-entropy
                    predictions_softmax = softmax(predictions)
                    loss = -np.mean(batch_y * np.log(predictions_softmax + 1e-8))
                    output_grad = (predictions_softmax - batch_y) / len(batch_y)
                
                # Backward pass (simplified)
                self._backward_pass(batch_X, output_grad, learning_rate, momentum, 
                                  weight_velocities, bias_velocities)
                
                total_loss += loss
                n_batches += 1
                
            avg_loss = total_loss / n_batches
            self.training_history.append(avg_loss)
            
            if verbose and (epoch + 1) % 20 == 0:
                logging.info(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.6f}")
                
        self.training = False
        self.is_trained = True
        
    def _backward_pass(self, X, output_grad, learning_rate, momentum, weight_velocities, bias_velocities):
        """Simplified backpropagation"""
        # This is a simplified version - in practice you'd want full backprop
        # For ultra-light models, we can use approximations
        
        # Simple gradient approximation for the last layer
        if len(self.weights) > 0:
            # Get the input to the last layer (simplified)
            if len(self.weights) == 1:
                layer_input = X
            else:
                # Forward to second-to-last layer
                layer_input = X
                for i in range(len(self.weights) - 1):
                    layer_input = np.dot(layer_input, self.weights[i])
                    if self.config.use_bias and i < len(self.biases):
                        layer_input += self.biases[i]
                    layer_input = self.activation(layer_input)
            
            # Update last layer weights
            weight_grad = np.dot(layer_input.T, output_grad)
            weight_velocities[-1] = momentum * weight_velocities[-1] - learning_rate * weight_grad
            self.weights[-1] += weight_velocities[-1]
            
            if self.config.use_bias and bias_velocities:
                bias_grad = np.mean(output_grad, axis=0)
                bias_velocities[-1] = momentum * bias_velocities[-1] - learning_rate * bias_grad
                self.biases[-1] += bias_velocities[-1]

class OnlineLinearClassifier:
    """Online linear classifier using FTRL-Proximal for incremental learning"""
    
    def __init__(self, n_features: int, alpha: float = 1.0, beta: float = 1.0, 
                 l1_reg: float = 0.1, l2_reg: float = 1.0):
        self.n_features = n_features
        self.alpha = alpha
        self.beta = beta 
        self.l1_reg = l1_reg
        self.l2_reg = l2_reg
        
        # FTRL-Proximal parameters
        self.z = np.zeros(n_features)  # Lazy weights
        self.n = np.zeros(n_features)  # Squared gradient accumulator
        self.weights = np.zeros(n_features)
        
        self.update_count = 0
        
    def _get_weight(self, i: int) -> float:
        """Get weight with L1 regularization applied"""
        if abs(self.z[i]) <= self.l1_reg:
            return 0.0
        else:
            return -(self.z[i] - np.sign(self.z[i]) * self.l1_reg) / (
                (self.beta + np.sqrt(self.n[i])) / self.alpha + self.l2_reg
            )
    
    def predict_proba(self, x: np.ndarray) -> float:
        """Predict probability"""
        if x.ndim == 1:
            # Update weights lazily
            for i in range(self.n_features):
                self.weights[i] = self._get_weight(i)
            
            logit = np.dot(x, self.weights)
            return sigmoid(logit)
        else:
            # Batch prediction
            probas = []
            for sample in x:
                probas.append(self.predict_proba(sample))
            return np.array(probas)
    
    def predict(self, x: np.ndarray) -> np.ndarray:
        """Make binary predictions"""
        probas = self.predict_proba(x)
        return (probas > 0.5).astype(int)
    
    def partial_fit(self, x: np.ndarray, y: float):
        """Update model with a single sample"""
        if x.ndim > 1:
            for i in range(len(x)):
                self.partial_fit(x[i], y[i])
            return
            
        # Get current prediction
        pred = self.predict_proba(x)
        
        # Compute gradient
        gradient = (pred - y) * x
        
        # Update FTRL parameters
        for i in range(self.n_features):
            if abs(gradient[i]) > 1e-8:  # Avoid tiny updates
                old_n = self.n[i]
                self.n[i] += gradient[i] ** 2
                
                sigma = (np.sqrt(self.n[i]) - np.sqrt(old_n)) / self.alpha
                self.z[i] += gradient[i] - sigma * self.weights[i]
                
        self.update_count += 1
        
    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 1):
        """Batch training"""
        for epoch in range(epochs):
            for i in range(len(X)):
                self.partial_fit(X[i], y[i])

class MiniTransformer:
    """Mini-Transformer for short text processing"""
    
    def __init__(self, vocab_size: int, d_model: int = 128, n_heads: int = 4, 
                 n_layers: int = 2, max_seq_len: int = 64):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.max_seq_len = max_seq_len
        
        # Initialize parameters (simplified)
        self.embedding = np.random.randn(vocab_size, d_model) * 0.1
        self.pos_embedding = np.random.randn(max_seq_len, d_model) * 0.1
        
        # Multi-head attention parameters (simplified)
        self.attention_weights = []
        for layer in range(n_layers):
            layer_weights = {
                'W_q': np.random.randn(d_model, d_model) * np.sqrt(2.0 / d_model),
                'W_k': np.random.randn(d_model, d_model) * np.sqrt(2.0 / d_model),
                'W_v': np.random.randn(d_model, d_model) * np.sqrt(2.0 / d_model),
                'W_o': np.random.randn(d_model, d_model) * np.sqrt(2.0 / d_model),
            }
            self.attention_weights.append(layer_weights)
        
        # Simple feed-forward layers
        self.ff_weights = []
        for layer in range(n_layers):
            ff_dim = d_model * 4  # Standard transformer ratio
            layer_ff = {
                'W1': np.random.randn(d_model, ff_dim) * np.sqrt(2.0 / d_model),
                'b1': np.zeros(ff_dim),
                'W2': np.random.randn(ff_dim, d_model) * np.sqrt(2.0 / ff_dim),
                'b2': np.zeros(d_model),
            }
            self.ff_weights.append(layer_ff)
    
    def scaled_dot_product_attention(self, Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
        """Simplified attention mechanism"""
        d_k = Q.shape[-1]
        scores = np.dot(Q, K.transpose(-2, -1)) / np.sqrt(d_k)
        
        # Apply softmax
        attn_weights = softmax(scores)
        
        # Apply attention to values
        output = np.dot(attn_weights, V)
        return output
    
    def forward(self, input_ids: np.ndarray) -> np.ndarray:
        """Forward pass (simplified transformer)"""
        seq_len = len(input_ids)
        
        # Embedding + positional encoding
        x = self.embedding[input_ids] + self.pos_embedding[:seq_len]
        
        # Transformer layers
        for layer in range(self.n_layers):
            # Multi-head attention (simplified to single head)
            Q = np.dot(x, self.attention_weights[layer]['W_q'])
            K = np.dot(x, self.attention_weights[layer]['W_k']) 
            V = np.dot(x, self.attention_weights[layer]['W_v'])
            
            # Attention
            attn_out = self.scaled_dot_product_attention(Q, K, V)
            attn_out = np.dot(attn_out, self.attention_weights[layer]['W_o'])
            
            # Residual connection + layer norm (simplified)
            x = x + attn_out
            
            # Feed forward
            ff_out = np.dot(x, self.ff_weights[layer]['W1']) + self.ff_weights[layer]['b1']
            ff_out = relu(ff_out)
            ff_out = np.dot(ff_out, self.ff_weights[layer]['W2']) + self.ff_weights[layer]['b2']
            
            # Residual connection
            x = x + ff_out
            
        return x
    
    def encode_text(self, text: str, tokenizer_vocab: Dict[str, int]) -> List[int]:
        """Simple tokenization"""
        # Very basic tokenizer - replace with proper tokenizer in real use
        tokens = text.lower().split()
        return [tokenizer_vocab.get(token, tokenizer_vocab.get('<UNK>', 0)) for token in tokens[:self.max_seq_len]]

class ModelCompression:
    """Utilities for model compression"""
    
    @staticmethod
    def quantize_weights(weights: np.ndarray, quantization: str = 'int8') -> np.ndarray:
        """Quantize model weights"""
        if quantization == 'int8':
            # Simple linear quantization to 8-bit
            w_min, w_max = weights.min(), weights.max()
            scale = (w_max - w_min) / 255
            zero_point = int(-w_min / scale)
            
            quantized = np.round((weights - w_min) / scale).astype(np.int8)
            return quantized, scale, zero_point, w_min
            
        elif quantization == 'int4':
            # 4-bit quantization (stored in int8)
            w_min, w_max = weights.min(), weights.max()
            scale = (w_max - w_min) / 15  # 4-bit range
            
            quantized = np.round((weights - w_min) / scale).astype(np.int8)
            quantized = np.clip(quantized, 0, 15)
            
            return quantized, scale, 0, w_min
            
        return weights
    
    @staticmethod
    def prune_weights(weights: np.ndarray, sparsity: float = 0.5) -> np.ndarray:
        """Apply magnitude-based pruning"""
        threshold = np.percentile(np.abs(weights), sparsity * 100)
        pruned_weights = weights.copy()
        pruned_weights[np.abs(weights) < threshold] = 0
        return pruned_weights

# Model factory
def create_ultralight_model(model_type: str, **kwargs) -> BaseNeuralNetwork:
    """Factory function to create ultra-light models"""
    
    if model_type == 'mlp':
        config = ModelConfig(**kwargs)
        return UltraLightMLP(config)
    elif model_type == 'linear':
        return OnlineLinearClassifier(**kwargs)
    elif model_type == 'mini_transformer':
        return MiniTransformer(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

# Example usage and model definitions
PREDEFINED_MODELS = {
    'intent_classifier': {
        'type': 'mlp',
        'input_dim': 128,  # After dimensionality reduction
        'hidden_dims': [64, 32],
        'output_dim': 4,  # question, request, command, analysis
        'activation': 'relu'
    },
    'document_classifier': {
        'type': 'mlp',
        'input_dim': 256,
        'hidden_dims': [128, 64],
        'output_dim': 5,  # legal, medical, technical, financial, educational
        'activation': 'silu'
    },
    'sentiment_classifier': {
        'type': 'linear',
        'n_features': 100,
        'alpha': 1.0,
        'l1_reg': 0.1
    },
    'text_embedder': {
        'type': 'mini_transformer',
        'vocab_size': 5000,
        'd_model': 128,
        'n_heads': 4,
        'n_layers': 2
    }
}

def get_predefined_model(model_name: str):
    """Get a predefined model configuration"""
    if model_name not in PREDEFINED_MODELS:
        raise ValueError(f"Unknown predefined model: {model_name}")
        
    config = PREDEFINED_MODELS[model_name].copy()
    model_type = config.pop('type')
    
    return create_ultralight_model(model_type, **config)