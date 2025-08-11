
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuración ---
# 1. Habla con @BotFather en Telegram para crear un bot y obtener tu token.
# 2. Pega tu token aquí.
# TOKEN = "TU_TOKEN_DE_TELEGRAM_AQUI"
TOKEN = os.environ.get("TELEGRAM_TOKEN") # Es mejor usar variables de entorno

# Función para el comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('¡Hola! Soy MEA-Core IA, conectado a Telegram.')

# Función para responder a mensajes de texto
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    
    # Aquí puedes integrar la lógica de MEA-Core
    # response = mea_core.process(user_message)
    # await update.message.reply_text(response)
    
    await update.message.reply_text(f"He recibido tu mensaje: \"{user_message}\". Aún estoy en desarrollo.")

def run_bot():
    if not TOKEN:
        print("[ERROR] El token de Telegram no está configurado.")
        print("Por favor, edita el archivo `bots/telegram_bot.py` o establece la variable de entorno TELEGRAM_TOKEN.")
        return

    # Crear la aplicación del bot
    application = Application.builder().token(TOKEN).build()

    # Registrar los manejadores de comandos y mensajes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar el bot
    print("Iniciando bot de Telegram...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()
