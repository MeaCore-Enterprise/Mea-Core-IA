"""
Modulo de aprendizaje activo y evolución para MEA-Core-IA.
"""

from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression

# Intentar importar modAL y manejar el fallo si no está instalado
try:
    from modAL.models import ActiveLearner
    from modAL.uncertainty import uncertainty_sampling
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False

class ActiveLearningModule:
    """
    Gestiona el ciclo de aprendizaje activo para mejorar un modelo de clasificación subyacente.
    """
    def __init__(self, initial_data: Tuple[np.ndarray, np.ndarray] = None):
        if not MODAL_AVAILABLE:
            print("[Advertencia] modAL no está instalado. El módulo de aprendizaje activo estará deshabilitado.")
            print("Para usarlo, ejecuta: pip install modal-python")
            self.learner = None
            return

        # 1. Definir el estimador base (un clasificador de scikit-learn)
        estimator = LogisticRegression()

        # 2. Crear un conjunto de datos inicial (puede ser vacío o con algunos ejemplos)
        if initial_data and len(initial_data[0]) > 0:
            X_initial, y_initial = initial_data
        else:
            # Creamos datos de ejemplo para que el modelo no falle al empezar
            X_initial = np.array([[1, 1], [2, 2], [1, 2], [2, 1]])
            y_initial = np.array([0, 1, 0, 1])

        # 3. Simular un "pool" de datos no etiquetados de donde el learner puede preguntar
        self.X_pool = np.random.rand(100, 2) # 100 muestras, 2 características

        # 4. Inicializar el ActiveLearner
        self.learner = ActiveLearner(
            estimator=estimator,
            query_strategy=uncertainty_sampling, # Estrategia: preguntar por lo que menos seguro está
            X_training=X_initial,
            y_training=y_initial
        )
        print("[Aprendizaje Activo] Módulo inicializado y listo.")

    def get_uncertain_samples(self, n_instances: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Obtiene las 'n' muestras del pool sobre las que el modelo tiene más dudas.
        Devuelve los índices y las muestras en sí.
        """
        if not self.learner:
            return np.array([]), np.array([])

        query_idx, query_instance = self.learner.query(self.X_pool, n_instances=n_instances)
        return query_idx, query_instance

    def teach(self, indices: np.ndarray, labels: np.ndarray) -> None:
        """
        "Enseña" al learner con nuevas etiquetas para las muestras dudosas.
        
        Args:
            indices: Los índices de las muestras en el pool que se van a etiquetar.
            labels: Las etiquetas correctas para esas muestras.
        """
        if not self.learner:
            return

        # Extraer las muestras del pool usando los índices
        samples = self.X_pool[indices]

        # Enseñar al learner con las nuevas muestras y etiquetas
        self.learner.teach(X=samples, y=labels)

        # Eliminar las muestras recién etiquetadas del pool
        self.X_pool = np.delete(self.X_pool, indices, axis=0)

        print(f"[Aprendizaje Activo] Modelo re-entrenado con {len(labels)} nueva(s) instancia(s).")

    def get_model_accuracy(self) -> float:
        """Calcula la precisión del modelo actual sobre el conjunto de entrenamiento."""
        if not self.learner:
            return 0.0
        return self.learner.score(self.learner.X_training, self.learner.y_training)