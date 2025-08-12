import discord
import os
import sys
from typing import List

# Añadir el directorio raíz al path para poder importar los módulos del core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager
from core.memory import MemoryStore
from core.ethics import EthicsCore
from core.brain import Brain
from core.remote_logger import RemoteLogger
from core.swarm import SwarmController

class MeaDiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar todos los componentes del core, igual que en CliBot
        self.settings_manager = SettingsManager()
        self.responses = self.settings_manager.get_responses()
        self.mem: MemoryStore = MemoryStore()
        self.ethics: EthicsCore = EthicsCore()
        self.brain: Brain = Brain(self.settings_manager.settings, self.responses)
        self.remote_logger: RemoteLogger = RemoteLogger(self.settings_manager.settings)
        self.swarm_controller: SwarmController = SwarmController(self.settings_manager.settings, self.mem)
        self.context: List[str] = []

    async def on_ready(self):
        instance_id = self.mem.get_instance_id()
        print(f'--- MEA-Core (Discord Bot) Conectado como {self.user} (ID: {instance_id[:8]}) ---')
        if self.remote_logger.enabled:
            print("[INFO] Aprendizaje remoto: ACTIVADO")
        else:
            print("[INFO] Aprendizaje remoto: DESACTIVADO")
        if self.swarm_controller.replication_enabled:
            print("[INFO] Replicación de enjambre: ACTIVADA")
        else:
            print("[INFO] Replicación de enjambre: DESACTIVADA")
        print(f'--- {self.brain.get_greeting()} ---')
        # Iniciar el ciclo de enjambre en segundo plano
        self.loop.create_task(self.swarm_controller.run_replication_cycle_async())


    async def handle_command(self, message: discord.Message) -> bool:
        q = message.content
        q_lower = q.lower()
        
        if q.startswith("!set "):
            try:
                _, key, *rest = q.split()
                value = " ".join(rest)
                self.mem.set(key, value)
                await message.channel.send(f'[Memoria] `{key}` = `{value}`')
            except ValueError:
                await message.channel.send("[Error] Comando !set mal formado. Uso: `!set <clave> <valor>`")
            return True
            
        if q.startswith("!get "):
            try:
                _, key = q.split()
                value = self.mem.get(key)
                await message.channel.send(f'[Memoria] `{key}` -> `{value or "No encontrado"}`')
            except ValueError:
                await message.channel.send("[Error] Comando !get mal formado. Uso: `!get <clave>`")
            return True
            
        if q_lower == "!dump":
            dump = self.mem.dump_all()
            # Discord tiene un límite de 2000 caracteres por mensaje
            dump_str = str(dump)
            if len(dump_str) > 1980:
                await message.channel.send(f'[Memoria] Dump completo (parcial):\n```{\n}dump_str[:1980]}...```')
            else:
                await message.channel.send(f'[Memoria] Dump completo:\n```{\n}dump_str}```')
            return True
            
        return False

    async def on_message(self, message: discord.Message):
        # 1. Ignorar mensajes del propio bot
        if message.author == self.user:
            return

        # 2. Manejar comandos especiales
        if await self.handle_command(message):
            return

        # 3. Procesar el mensaje a través del core
        q = message.content
        
        # 3a. Comprobación ética
        if not self.ethics.check_action(q):
            explanation = self.ethics.explain_decision(q)
            await message.channel.send(f"[Ética] {explanation}")
            return

        # 3b. Obtener respuesta del cerebro
        respuestas = self.brain.get_response(q)
        
        # 3c. Enviar respuestas
        for respuesta in respuestas:
            await message.channel.send(respuesta)

        # 4. Registrar en la memoria y logs remotos
        self.mem.log_conversation(user_input=q, bot_output=respuestas)
        self.remote_logger.log(user_input=q, bot_output=respuestas)
        self.context.append(q)

def run_bot():
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if not TOKEN:
        print("[ERROR] El token de Discord no está configurado.")
        print("Por favor, establece la variable de entorno DISCORD_TOKEN.")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    
    client = MeaDiscordBot(intents=intents)
    
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print("[ERROR] Falló el inicio de sesión. El token de Discord es inválido.")
    except Exception as e:
        print(f"[ERROR] Ocurrió un error inesperado al ejecutar el bot: {e}")

if __name__ == '__main__':
    run_bot()