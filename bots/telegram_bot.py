import os
import sys
from typing import List
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Añadir el directorio raíz al path para poder importar los módulos del core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager
from core.memory import MemoryStore
from core.ethics import EthicsCore
from core.brain import Brain
from core.remote_logger import RemoteLogger
from core.swarm import SwarmController

class MeaTelegramBot:
    def __init__(self):
        # Inicializar todos los componentes del core
        self.settings_manager = SettingsManager()
        self.responses = self.settings_manager.get_responses()
        self.mem: MemoryStore = MemoryStore()
        self.ethics: EthicsCore = EthicsCore()
        self.brain: Brain = Brain(self.settings_manager.settings, self.responses)
        self.remote_logger: RemoteLogger = RemoteLogger(self.settings_manager.settings)
        self.swarm_controller: SwarmController = SwarmController(self.settings_manager.settings, self.mem)
        self.context: List[str] = []
        instance_id = self.mem.get_instance_id()
        print(f'--- MEA-Core (Telegram Bot) Iniciado (ID: {instance_id[:8]}) ---')

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        greeting = self.brain.get_greeting()
        await update.message.reply_text(f'¡Hola! Soy MEA-Core IA. {greeting}')

    async def set_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            key = context.args[0]
            value = " ".join(context.args[1:])
            self.mem.set(key, value)
            await update.message.reply_text(f'[Memoria] `{key}` = `{value}`', parse_mode='MarkdownV2')
        except (IndexError, ValueError):
            await update.message.reply_text("Uso: `/set <clave> <valor>`")

    async def get_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            key = context.args[0]
            value = self.mem.get(key)
            await update.message.reply_text(f'[Memoria] `{key}` -> `{value or "No encontrado"}`', parse_mode='MarkdownV2')
        except IndexError:
            await update.message.reply_text("Uso: `/get <clave>`")

    async def dump_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        dump = self.mem.dump_all()
        dump_str = str(dump)
        # Telegram tiene un límite de 4096 caracteres
        if len(dump_str) > 4000:
            await update.message.reply_text(f'[Memoria] Dump completo (parcial):\n```\n{dump_str[:4000]}...\n```', parse_mode='MarkdownV2')
        else:
            await update.message.reply_text(f'[Memoria] Dump completo:\n```\n{dump_str}\n```', parse_mode='MarkdownV2')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        q = update.message.text

        # 1. Comprobación ética
        if not self.ethics.check_action(q):
            explanation = self.ethics.explain_decision(q)
            await update.message.reply_text(f"[Ética] {explanation}")
            return

        # 2. Obtener respuesta del cerebro
        respuestas = self.brain.get_response(q)

        # 3. Enviar respuestas
        for respuesta in respuestas:
            await update.message.reply_text(respuesta)

        # 4. Registrar en la memoria y logs remotos
        self.mem.log_conversation(user_input=q, bot_output=respuestas)
        self.remote_logger.log(user_input=q, bot_output=respuestas)
        self.context.append(q)

    def run(self):
        TOKEN = os.environ.get("TELEGRAM_TOKEN")
        if not TOKEN:
            print("[ERROR] El token de Telegram no está configurado.")
            print("Por favor, establece la variable de entorno TELEGRAM_TOKEN.")
            return

        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("set", self.set_command))
        application.add_handler(CommandHandler("get", self.get_command))
        application.add_handler(CommandHandler("dump", self.dump_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print("Iniciando bot de Telegram...")
        # Iniciar ciclo de enjambre en segundo plano (de forma síncrona en un hilo)