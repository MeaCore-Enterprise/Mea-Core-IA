
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
from collections import Counter
import re

# --- 1. Vocabulario ---
# Gestiona el mapeo de palabras a IDs numericos y viceversa.
class Vocabulary:
    def __init__(self):
        # Diccionarios para la conversion palabra <-> indice
        self.word2idx = {"<UNK>": 0} # Token para palabras desconocidas
        self.idx2word = ["<UNK>"]
        # Contador para la frecuencia de las palabras
        self.word_counts = Counter()

    def add_word(self, word):
        """Añade una palabra al vocabulario (sin crear indice aun)."""
        self.word_counts[word] += 1

    def build_vocab(self, corpus, min_count=5):
        """
        Construye el vocabulario final a partir de un corpus.
        Filtra palabras que no alcanzan una frecuencia minima (min_count).
        """
        # Primero, cuenta todas las palabras del corpus
        for word in corpus:
            self.add_word(word)

        # Segundo, asigna indices solo a las palabras que cumplen con min_count
        for word, count in self.word_counts.items():
            if count >= min_count:
                if word not in self.word2idx:
                    self.idx2word.append(word)
                    self.word2idx[word] = len(self.idx2word) - 1
    
    def get_index(self, word):
        """Obtiene el indice de una palabra, o el de <UNK> si no existe."""
        return self.word2idx.get(word, 0)

    def __len__(self):
        return len(self.idx2word)

# --- 2. Modelo Skip-gram ---
# La arquitectura de red neuronal para aprender los embeddings.
class SkipGramModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(SkipGramModel, self).__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim

        # Capa de Embeddings: el corazon del modelo.
        # Cada fila es el vector de una palabra.
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)

        # Capa de salida: proyecta el embedding para predecir palabras de contexto.
        self.output_layer = nn.Linear(embedding_dim, vocab_size)

    def forward(self, target_word_idx):
        """
        Paso hacia adelante: toma el indice de la palabra objetivo
        y predice la probabilidad de cada palabra del vocabulario de ser su contexto.
        """
        # Obtiene el vector embedding de la palabra objetivo
        word_embedding = self.embeddings(target_word_idx)
        
        # Calcula los scores para cada palabra del vocabulario
        scores = self.output_layer(word_embedding)
        
        # Devuelve los scores (la funcion de perdida aplicara Softmax)
        return scores

# --- 3. Motor Principal ---
# Une el vocabulario y el modelo, y gestiona el guardado/carga.
class MeaEngine:
    def __init__(self, embedding_dim=100, min_word_count=5):
        self.config = {
            "embedding_dim": embedding_dim,
            "min_word_count": min_word_count
        }
        self.vocab = None
        self.model = None

    def build(self, text_corpus):
        """Construye el vocabulario a partir de un corpus de texto."""
        print("Construyendo vocabulario...")
        self.vocab = Vocabulary()
        # Tokenizacion simple: minusculas y division por espacios/puntuacion
        words = re.findall(r'\b\w+\b', text_corpus.lower())
        self.vocab.build_vocab(words, self.config["min_word_count"])
        print(f"Vocabulario construido con {len(self.vocab)} palabras unicas.")

        # Inicializa el modelo con el tamaño del vocabulario
        self.model = SkipGramModel(
            vocab_size=len(self.vocab),
            embedding_dim=self.config["embedding_dim"]
        )

    def get_trained_embeddings(self):
        """Devuelve la matriz de embeddings entrenada."""
        if self.model:
            # .weight contiene la matriz de embeddings
            return self.model.embeddings.weight.data
        return None

    def find_similar_words(self, word, top_n=10):
        """
        Encuentra las palabras mas similares a una dada usando similitud de coseno.
        """
        if not self.model or not self.vocab:
            raise Exception("El modelo no ha sido entrenado o cargado.")

        word_idx = self.vocab.get_index(word.lower())
        if word_idx == 0: # <UNK>
            print(f"La palabra '{word}' no se encuentra en el vocabulario.")
            return []

        # Normaliza todos los embeddings para el calculo de similitud de coseno
        embeddings = self.get_trained_embeddings()
        embeddings_norm = F.normalize(embeddings, p=2, dim=1)
        
        # Obtiene el embedding de la palabra de interes
        word_vec = embeddings_norm[word_idx]

        # Calcula la similitud de coseno (producto punto con vectores normalizados)
        cosine_sim = torch.matmul(embeddings_norm, word_vec)

        # Obtiene los indices y scores de las N palabras mas similares
        # El resultado incluye la propia palabra, por lo que pedimos top_n + 1
        top_results = torch.topk(cosine_sim, k=top_n + 1)

        similar_words = []
        for score, idx in zip(top_results.values, top_results.indices):
            # Omitimos la palabra de entrada
            if idx.item() != word_idx:
                similar_words.append((self.vocab.idx2word[idx.item()], score.item()))
        
        return similar_words

    def save_model(self, file_path):
        """Guarda el motor (config, vocabulario, pesos del modelo) en un archivo."""
        if not self.model or not self.vocab:
            raise Exception("No hay nada que guardar. Entrena el modelo primero.")
        
        model_data = {
            "config": self.config,
            "word2idx": self.vocab.word2idx,
            "idx2word": self.vocab.idx2word,
            "model_state_dict": self.model.state_dict()
        }
        torch.save(model_data, file_path)
        print(f"Modelo guardado en {file_path}")

    @staticmethod
    def load_model(file_path):
        """Carga un motor pre-entrenado desde un archivo."""
        model_data = torch.load(file_path)
        
        # Reconstruye el motor con la configuracion guardada
        engine = MeaEngine(embedding_dim=model_data["config"]["embedding_dim"])
        
        # Reconstruye el vocabulario
        engine.vocab = Vocabulary()
        engine.vocab.word2idx = model_data["word2idx"]
        engine.vocab.idx2word = model_data["idx2word"]
        
        # Reconstruye el modelo y carga los pesos
        engine.model = SkipGramModel(
            vocab_size=len(engine.vocab),
            embedding_dim=engine.config["embedding_dim"]
        )
        engine.model.load_state_dict(model_data["model_state_dict"])
        engine.model.eval() # Pone el modelo en modo de evaluacion
        
        print(f"Modelo cargado desde {file_path}")
        return engine
