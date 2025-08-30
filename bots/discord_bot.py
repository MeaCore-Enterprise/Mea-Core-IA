import discord
import os
import requests

API_URL = "http://localhost:8000/ask"
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

class MeaDiscordBot(discord.Client):
    async def on_ready(self):
        print(f'--- MEA-Core (Discord Bot) Conectado como {self.user} ---')
        print("Listo para responder preguntas.")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        
        if message.author.bot:
            return

        question = message.content
        
        try:
            response = requests.post(API_URL, json={"question": question})
            response.raise_for_status()
            answer_data = response.json()
            
            answer = answer_data.get("answer", "No entendí 🤔")
            
            if isinstance(answer, list):
                response_text = "\n".join(str(item) for item in answer)
            else:
                response_text = str(answer)

            if not response_text.strip():
                response_text = "No tengo una respuesta para eso en este momento."

            await message.channel.send(response_text)

        except requests.exceptions.RequestException as e:
            print(f"[Error de Conexión] No se pudo conectar a la API: {e}")
            await message.channel.send("Lo siento, no puedo conectar con mi cerebro ahora mismo. 🧠")
        except Exception as e:
            print(f"[Error Inesperado] Ocurrió un error: {e}")
            await message.channel.send("Ha ocurrido un error inesperado al procesar tu solicitud.")

def run_bot():
    if not DISCORD_TOKEN:
        print("[ERROR] El token de Discord no está configurado.")
        print("Por favor, establece la variable de entorno DISCORD_TOKEN.")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    
    client = MeaDiscordBot(intents=intents)
    
    try:
        client.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("[ERROR] Falló el inicio de sesión. El token de Discord es inválido.")
    except Exception as e:
        print(f"[ERROR] Ocurrió un error inesperado al ejecutar el bot: {e}")

if __name__ == '__main__':
    run_bot()