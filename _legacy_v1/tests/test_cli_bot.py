import unittest
from unittest.mock import patch, AsyncMock
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.cli_bot import CliBot

class TestCliBot(unittest.TestCase):

    @patch('bots.base_bot.BaseBot.process_message')
    @patch('builtins.input', return_value='quit')
    def test_exit_command_prints_farewell(self, mock_input, mock_process_message):
        """Prueba que al introducir 'quit', el bot imprime una despedida."""
        bot = CliBot()
        # Mock para el cerebro para controlar la respuesta de despedida
        bot.brain.get_farewell = lambda: "Adiós, prueba superada."
        
        with patch('builtins.print') as mock_print:
            bot.run()
            # Verificamos que se llamó a print con el mensaje de despedida
            mock_print.assert_any_call("Adiós, prueba superada.")

    @patch('builtins.input', side_effect=["hola", "quit"])
    def test_interaction_and_exit(self, mock_input):
        """Prueba una interacción simple seguida de una salida."""
        bot = CliBot()
        bot.brain.get_farewell = lambda: "Adiós."
        # Reemplazamos el método real con un mock asíncrono
        bot.process_message = AsyncMock()

        bot.run()

        # Verificar que process_message fue llamado con 'hola'
        bot.process_message.assert_called_once_with("hola")

    @patch('builtins.input', return_value="!set k v")
    def test_handle_command_set(self, mock_input):
        """Prueba que el comando !set es manejado correctamente."""
        bot = CliBot()
        # Reemplazamos los métodos con mocks
        bot.handle_command = AsyncMock(return_value=True)
        bot.process_message = AsyncMock()

        bot.run()
        
        # El bucle principal llama a handle_command. Si devuelve True,
        # process_message no debe ser llamado.
        bot.handle_command.assert_called_once_with("!set k v")
        bot.process_message.assert_not_called()

if __name__ == "__main__":
    unittest.main()