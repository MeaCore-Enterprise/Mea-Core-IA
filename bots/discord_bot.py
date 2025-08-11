
import discord
import os

# --- Configuración --- 
# 1. Crea una aplicación de bot en el Portal de Desarrolladores de Discord.
# 2. Obtén el token de tu bot y pégalo aquí.
# 3. Habilita los "Message Content Intent" en la configuración de tu bot.
# TOKEN = "TU_TOKEN_DE_DISCORD_AQUI"
TOKEN = os.environ.get("DISCORD_TOKEN") # Es mejor usar variables de entorno

class MeaDiscordBot(discord.Client):
    async def on_ready(self):
        print(f'¡Conectado como {self.user}!')

    async def on_message(self, message):
        # Ignorar mensajes del propio bot
        if message.author == self.user:
            return

        # Comando de prueba
        if message.content.startswith('!hola'):
            await message.channel.send('¡Hola! Soy MEA-Core IA, conectado a Discord.')

        # Aquí puedes integrar la lógica de MEA-Core
        # Por ejemplo, podrías llamar a los módulos del core para generar una respuesta
        # response = mea_core.process(message.content)
        # await message.channel.send(response)

def run_bot():
    if not TOKEN:
        print("[ERROR] El token de Discord no está configurado.")
        print("Por favor, edita el archivo `bots/discord_bot.py` o establece la variable de entorno DISCORD_TOKEN.")
        return

    intents = discord.Intents.default()
    intents.message_content = True  # Habilitar el intent de contenido de mensajes
    
    client = MeaDiscordBot(intents=intents)
    client.run(TOKEN)

if __name__ == '__main__':
    run_bot()
