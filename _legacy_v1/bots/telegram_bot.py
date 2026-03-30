"""Bot de Telegram para interactuar con MEA-Core."""

import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.base_bot import BaseBot

class MeaTelegramBot(BaseBot):
    """Implementación del bot para Telegram."""

    def __init__(self):
        """Inicializa el bot y los componentes del núcleo de MEA."""
        super().__init__(node_id="telegram")
        instance_id = self.memory.get_instance_id()
        print(f'--- MEA-Core (Telegram Bot) Iniciado (ID: {instance_id[:8]}) ---')

    async def send_message(self, message: str, **kwargs):
        """Envía un mensaje al chat de Telegram."""
        update = kwargs.get('update')
        if update:
            await update.message.reply_text(message, parse_mode='MarkdownV2')

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /start y envía un saludo."""
        greeting = self.brain.get_greeting()
        await update.message.reply_text(f'¡Hola! Soy MEA-Core IA. {greeting}')

    async def set_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /set para guardar un par clave-valor en la memoria."""
        try:
            key = context.args[0]
            value = " ".join(context.args[1:])
            await self.handle_command(f"!set {key} {value}", update=update)
        except (IndexError, ValueError):
            await update.message.reply_text("Uso: `/set <clave> <valor>`")

    async def get_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /get para recuperar un valor de la memoria."""
        try:
            key = context.args[0]
            await self.handle_command(f"!get {key}", update=update)
        except IndexError:
            await update.message.reply_text("Uso: `/get <clave>`")

    async def dump_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja el comando /dump para mostrar todo el contenido de la memoria kv."""
        await self.handle_command("!dump", update=update)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja los mensajes de texto que no son comandos."""
        await self.process_message(update.message.text, update=update)

    def run(self):
        """Configura y ejecuta el bot de Telegram."""
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
        application.run_polling()

if __name__ == '__main__':
    bot = MeaTelegramBot()
    bot.run()