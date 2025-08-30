import unittest
from unittest.mock import patch, call
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.cli_bot import CliBot

class TestCliBot(unittest.TestCase):

    @patch('bots.cli_bot.CliBot.setup')
    @patch('bots.cli_bot.CliBot.process_input')
    @patch('builtins.input', return_value='quit')
    def test_exit_command_prints_farewell(self, mock_input, mock_process, mock_setup):
        """Prueba que al introducir 'quit', el bot imprime una despedida."""
        bot = CliBot()
        # Mock para el cerebro para controlar la respuesta de despedida
        bot.brain.get_farewell = lambda: "Adiós, prueba superada."
        
        with patch('builtins.print') as mock_print:
            bot.run()
            # Verificamos que se llamó a print con el mensaje de despedida
            mock_print.assert_any_call("Adiós, prueba superada.")

    @patch('bots.cli_bot.CliBot.setup')
    @patch('builtins.input', side_effect=["hola", "quit"])
    def test_interaction_and_exit(self, mock_input, mock_setup):
        """Prueba una interacción simple seguida de una salida."""
        bot = CliBot()
        bot.brain.get_farewell = lambda: "Adiós."
        bot.process_input = unittest.mock.AsyncMock()

        bot.run()

        # Verificar que process_input fue llamado con 'hola'
        bot.process_input.assert_called_once_with("hola")

    @patch('bots.cli_bot.CliBot.setup')
    @patch('builtins.input', return_value="!set k v")
    def test_handle_command_set(self, mock_input, mock_setup):
        """Prueba que el comando !set es manejado correctamente."""
        bot = CliBot()
        bot.handle_command = unittest.mock.MagicMock(return_value=True)
        bot.process_input = unittest.mock.AsyncMock()

        bot.run()
        
        # El bucle principal llama a handle_command. Si devuelve True,
        # process_input no debe ser llamado.
        bot.handle_command.assert_called_once_with("!set k v")
        bot.process_input.assert_not_called()

if __name__ == "__main__":
    unittest.main()