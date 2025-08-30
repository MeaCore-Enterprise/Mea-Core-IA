import unittest
import numpy as np
import pytest
from unittest.mock import patch

# Añadir el directorio raíz al path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.evolucion import ActiveLearningModule, MODAL_AVAILABLE

@pytest.fixture
def initial_data():
    """Provides a basic set of initial data for the learner."""
    X_initial = np.array([[1, 1], [2, 2], [1, 2], [2, 1]])
    y_initial = np.array([0, 1, 0, 1])
    return X_initial, y_initial

@pytest.mark.skipif(not MODAL_AVAILABLE, reason="modAL library is not installed")
class TestActiveLearningModule(unittest.TestCase):

    def setUp(self, data=None):
        """Initializes the ActiveLearningModule for each test."""
        # Usamos datos de ejemplo si no se proporcionan
        if data is None:
            X_initial = np.array([[1, 1], [2, 2]])
            y_initial = np.array([0, 1])
            data = (X_initial, y_initial)
        self.alm = ActiveLearningModule(initial_data=data)

    def test_initialization(self):
        """Tests that the module initializes correctly."""
        self.assertIsNotNone(self.alm.learner)
        self.assertEqual(len(self.alm.learner.X_training), 2)

    def test_get_uncertain_samples(self):
        """Tests that the query method returns the correct number of samples."""
        n_samples = 3
        # Asegurarse de que el pool no sea más pequeño que las muestras solicitadas
        if len(self.alm.X_pool) < n_samples:
            self.alm.X_pool = np.random.rand(n_samples * 2, 2)
        indices, instances = self.alm.get_uncertain_samples(n_instances=n_samples)
        self.assertEqual(len(indices), n_samples)
        self.assertEqual(len(instances), n_samples)

    def test_teach(self):
        """Tests that teaching the learner increases its knowledge."""
        initial_training_size = len(self.alm.learner.X_training)
        initial_pool_size = len(self.alm.X_pool)

        # 1. Get a sample to teach
        indices, _ = self.alm.get_uncertain_samples(n_instances=1)
        
        # 2. Create a label for it
        dummy_label = np.array([0])

        # 3. Teach the module
        self.alm.teach(indices, dummy_label)

        # 4. Verify the state has changed
        self.assertEqual(len(self.alm.learner.X_training), initial_training_size + 1)
        self.assertEqual(len(self.alm.X_pool), initial_pool_size - 1)

    def test_model_accuracy_improves(self):
        """Tests that accuracy improves with new, consistent data."""
        X_initial = np.array([[1, 1], [2, 2], [1.1, 1.1], [2.1, 2.1]])
        y_initial = np.array([0, 1, 0, 1])
        self.setUp(data=(X_initial, y_initial))

        initial_accuracy = self.alm.get_model_accuracy()
        self.assertEqual(initial_accuracy, 1.0)

        # Teach with a new, clear sample consistent with the pattern (class 1)
        new_sample = np.array([[2.2, 2.2]])
        new_label = np.array([1])
        
        # Para enseñar, necesitamos añadirlo al pool, obtener su índice y luego enseñar
        self.alm.X_pool = np.vstack([self.alm.X_pool, new_sample])
        new_sample_idx = np.array([len(self.alm.X_pool) - 1]) # El índice del último elemento

        self.alm.teach(new_sample_idx, new_label)

        new_accuracy = self.alm.get_model_accuracy()
        self.assertGreaterEqual(new_accuracy, initial_accuracy)

# Test for when the optional dependency is not installed
@patch('core.evolucion.MODAL_AVAILABLE', False)
def test_disabled_module(): # Corregido: eliminado 'self'
    """Tests that the module is disabled if modAL is not available."""
    alm = ActiveLearningModule()
    assert alm.learner is None
    # Methods should not crash and return empty values
    indices, instances = alm.get_uncertain_samples()
    assert len(indices) == 0
    assert alm.get_model_accuracy() == 0.0