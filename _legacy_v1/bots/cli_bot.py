import asyncio
import os
import sys

# Add the root directory to the path to allow imports from 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.base_bot import BaseBot

class CliBot(BaseBot):
    """Bot para interactuar con MEA-Core a través de la línea de comandos."""

    def __init__(self):
        """Inicializa el bot de CLI."""
        super().__init__(node_id='cli')
        print(self.responses.get("welcome_cli", "--- MEA-Core (CLI) ---"))

    async def send_message(self, message: str, **kwargs):
        """Envía un mensaje a la consola."""
        print(f"Mea-Core > {message}")

    def run(self):
        """Inicia el bucle principal de escucha y respuesta del bot de CLI."""
        print(self.responses.get("cli_instructions", "Escribe tu mensaje. Usa '/reset-memory' para borrar la memoria, o 'salir' para terminar."))
        
        # Cargar y mostrar contexto de conversaciones anteriores
        last_episodes = self.brain.memory.get_last_episodes(5)
        if last_episodes:
            print("\n--- Historial de conversación reciente ---")
            for episode in last_episodes:
                if episode.get('type') == 'conversation':
                    user_input = episode['data'].get('user_input', '')
                    bot_output = ' '.join(episode['data'].get('bot_output', []))
                    print(f"Tú > {user_input}")
                    print(f"Mea-Core > {bot_output}")
            print("----------------------------------------\n")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        while self.is_running:
            try:
                user_input = input("Tú > ")
                if user_input.lower() in ["exit()", "salir", "quit"]:
                    self.is_running = False
                    print(self.brain.get_farewell())
                elif user_input.lower() == "/reset-memory":
                    confirm = input("¿Estás seguro de que quieres borrar toda la memoria? Esta acción es irreversible. (s/n): ")
                    if confirm.lower() == 's':
                        self.brain.memory.reset_memory()
                    else:
                        print("Operación cancelada.")
                else:
                    loop.run_until_complete(self.process_message(user_input))
            except KeyboardInterrupt:
                self.is_running = False
                print(f"\n{self.brain.get_farewell()}")
            except Exception as e:
                print(f"[Error Inesperado] Ocurrió un error: {e}")
                self.is_running = False

if __name__ == "__main__":
    bot = CliBot()
    bot.run()
