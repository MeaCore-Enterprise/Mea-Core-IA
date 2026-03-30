# core/federated.py

import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.datasets import make_classification
from typing import List, Dict, Any

# Nota: Este es un prototipo usando scikit-learn. 
# SGDClassifier es útil aquí porque soporta `partial_fit`,
# lo que simula el aprendizaje continuo en cada nodo.

class FederatedLearningNode:
    """
    Gestiona el ciclo de vida del aprendizaje federado en un único nodo.
    """
    def __init__(self, n_features=100, n_classes=2):
        """
        Inicializa el modelo local.
        
        Args:
            n_features (int): Número de características que el modelo espera.
            n_classes (int): Número de clases de salida.
        """
        # Usamos SGDClassifier que permite actualizaciones incrementales.
        self.model = SGDClassifier(loss='log_loss', max_iter=1, warm_start=True)
        self.n_features = n_features
        self.classes = np.arange(n_classes)
        # Inicializar el modelo "en frío" la primera vez
        self.model.fit(np.zeros((1, n_features)), [0], classes=self.classes)

    def get_model_weights(self) -> Dict[str, np.ndarray]:
        """
        Extrae los pesos (coeficientes e intercepto) del modelo local.
        Estos son los parámetros que se compartirán con el enjambre.
        
        Returns:
            Dict[str, np.ndarray]: Un diccionario con los coeficientes y el intercepto.
        """
        return {
            'coef': self.model.coef_,
            'intercept': self.model.intercept_
        }

    def set_model_weights(self, weights: Dict[str, np.ndarray]):
        """
        Actualiza el modelo local con nuevos pesos (generalmente, los promediados).
        
        Args:
            weights (Dict[str, np.ndarray]): Diccionario con 'coef' e 'intercept'.
        """
        if 'coef' in weights and 'intercept' in weights:
            self.model.coef_ = weights['coef']
            self.model.intercept_ = weights['intercept']
            print("Modelo local actualizado con los pesos federados.")
        else:
            print("Error: Los pesos recibidos no tienen el formato esperado.")

    def train_on_local_data(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Entrena (o re-entrena) el modelo usando solo los datos locales.
        Usa `partial_fit` para simular el aprendizaje continuo.
        
        Args:
            X_train (np.ndarray): Muestras de entrenamiento locales.
            y_train (np.ndarray): Etiquetas de entrenamiento locales.
        """
        if X_train.shape[0] == 0:
            print("No hay datos locales para entrenar.")
            return
            
        print(f"Entrenando modelo local con {X_train.shape[0]} muestras.")
        # Usamos partial_fit para actualizar el modelo sin empezar de cero.
        self.model.partial_fit(X_train, y_train, classes=self.classes)


def average_weights(all_weights: List[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
    """
    Calcula el promedio de los pesos de múltiples modelos.
    Esta es la función clave del agregador en el aprendizaje federado.
    
    Args:
        all_weights (List[Dict[str, np.ndarray]]): Una lista de diccionarios de pesos de cada nodo.
        
    Returns:
        Dict[str, np.ndarray]: El diccionario de pesos promediado.
    """
    if not all_weights:
        return {}

    # Sumar todos los coeficientes e interceptos
    avg_coef = np.sum([w['coef'] for w in all_weights], axis=0) / len(all_weights)
    avg_intercept = np.sum([w['intercept'] for w in all_weights], axis=0) / len(all_weights)
    
    print(f"Promediando pesos de {len(all_weights)} nodos.")
    
    return {
        'coef': avg_coef,
        'intercept': avg_intercept
    }

# --- Ejemplo de uso simulado --- 
# En una implementación real, la comunicación de pesos se haría a través del SwarmNode.

def simulate_federated_learning_round():
    """
    Simula una ronda completa de aprendizaje federado entre 3 nodos.
    """
    print("--- Iniciando simulación de ronda de Aprendizaje Federado ---")
    
    # 1. Crear datos sintéticos para simular los datos locales de cada nodo
    X, y = make_classification(n_samples=300, n_features=100, n_informative=10, n_redundant=0, n_classes=2, random_state=42)
    X_node1, y_node1 = X[:100], y[:100]
    X_node2, y_node2 = X[100:200], y[100:200]
    X_node3, y_node3 = X[200:], y[200:]

    # 2. Inicializar un nodo de aprendizaje federado para cada instancia simulada
    node1 = FederatedLearningNode()
    node2 = FederatedLearningNode()
    node3 = FederatedLearningNode()

    # 3. Cada nodo entrena su modelo con sus datos locales
    node1.train_on_local_data(X_node1, y_node1)
    node2.train_on_local_data(X_node2, y_node2)
    node3.train_on_local_data(X_node3, y_node3)

    # 4. Recolectar los pesos de todos los nodos (esto lo haría el Swarm)
    all_node_weights = [
        node1.get_model_weights(),
        node2.get_model_weights(),
        node3.get_model_weights()
    ]

    # 5. Un nodo (o un servidor central) promedia los pesos
    averaged_global_weights = average_weights(all_node_weights)

    # 6. Distribuir los pesos promediados de vuelta a todos los nodos (vía Swarm)
    node1.set_model_weights(averaged_global_weights)
    node2.set_model_weights(averaged_global_weights)
    node3.set_model_weights(averaged_global_weights)
    
    print("--- Simulación de ronda completada. Todos los nodos tienen el modelo actualizado. ---")

if __name__ == '__main__':
    simulate_federated_learning_round()
