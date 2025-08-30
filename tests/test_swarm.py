

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controlador_enjambre import SwarmController
from core.memoria import MemoryStore

class TestSwarmController(unittest.TestCase):

    def setUp(self):
        """Configura un entorno de prueba limpio."""
        self.settings = {
            "swarm": {
                "replication_enabled": True,
                "scan_interval_seconds": 0
            }
        }
        self.memory = MemoryStore()
        self.swarm = SwarmController(node_id="test_node", db_path=":memory:")

    @patch('os.name', 'nt')
    @patch('os.path.exists', return_value=True)
    @patch('os.environ.get', return_value='C:')
    def test_get_potential_devices_windows(self, mock_env, mock_exists):
        """Prueba la detección de dispositivos en un entorno simulado de Windows."""
        # Llamar al método público que usa internamente la detección de dispositivos
        with patch.object(self.swarm, 'replicate_to_device') as mock_replicate:
            self.swarm.run_replication_cycle()
            # Verificar que se intentó replicar al dispositivo detectado
            mock_replicate.assert_called_once_with('D:\\')
        self.assertIn('D:\\', devices)
        self.assertNotIn('C:\\', devices)

    @patch('core.controlador_enjambre.SOURCE_DIR', 'd:\Proyectos\MEA-Core-IA')
    @patch('os.path.samefile', return_value=False)
    @patch('os.path.exists', return_value=False)
    @patch('shutil.copytree')
    @patch('builtins.open', new_callable=mock_open)
    def test_replicate_to_device_success(self, mock_open_file, mock_copytree, mock_exists, mock_samefile):
        """Prueba el flujo de replicación exitoso a un dispositivo."""
        device_path = 'E:\\'
        with patch.object(self.memory, 'log_replication') as mock_log_replication:
            self.swarm.replicate_to_device(device_path)
            mock_copytree.assert_called_once()
            mock_open_file.assert_called_with(os.path.join(device_path, "Mea-Core_Clone", "mea_identity.json"), "w")
            mock_log_replication.assert_called_once()

if __name__ == "__main__":
    unittest.main()

