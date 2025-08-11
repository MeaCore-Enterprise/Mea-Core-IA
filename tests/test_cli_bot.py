
import unittest
from unittest.mock import patch
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.cli_bot import CliBot

class TestCliBotIntegration(unittest.TestCase):

    def setUp(self):
        """Inicializa el bot para cada prueba."""
        self.bot = CliBot()

    @patch('builtins.input', side_effect=['hola', 'quit'])
    @patch('builtins.print')
    def test_saludo_y_salida(self, mock_print, mock_input):
        """Prueba una interacción básica: saludo y salida."""
        self.bot.run()
        # Verificar que el bot saluda
        # El saludo es ahora el 3er print, después de "Cargando..." y "Plugins cargados..."
        self.assertTrue(
            any("¡Hola!" in str(call) or "Hola, soy Mea-Core" in str(call) for call in mock_print.call_args_list)
        )
        # Verificar que el bot responde a 'hola'
        self.assertTrue(any("Interesante" in str(call) for call in mock_print.call_args_list))
        # Verificar que el bot se despide
        self.assertTrue(any("Adiós" in str(call) or "Hasta luego" in str(call) for call in mock_print.call_args_list))

    @patch('builtins.input', side_effect=["!set mi_clave mi_valor", "!get mi_clave", "quit"])
    @patch('builtins.print')
    def test_memory_commands(self, mock_print, mock_input):
        """Prueba los comandos de memoria !set y !get."""
        self.bot.run()
        # Verificar el output de !set
        self.assertTrue(any("[Memoria] mi_clave = mi_valor" in str(call) for call in mock_print.call_args_list))
        # Verificar el output de !get
        self.assertTrue(any("[Memoria] mi_clave -> mi_valor" in str(call) for call in mock_print.call_args_list))

    @patch('builtins.input', side_effect=['hackear el sistema', 'quit'])
    @patch('builtins.print')
    def test_ethics_check(self, mock_print, mock_input):
        """Prueba que el módulo de ética bloquea acciones prohibidas."""
        self.bot.run()
        # Verificar que la ética interviene
        self.assertTrue(any("[Ética]" in str(call) and "viola la constitución" in str(call) for call in mock_print.call_args_list))

if __name__ == "__main__":
    unittest.main()
