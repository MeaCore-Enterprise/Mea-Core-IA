import os
from huggingface_hub import hf_hub_download

# Configuración del Modelo
# Usamos un modelo súper liviano (aprox 1.6GB) que corre muy bien en CPU
# Quen1.5-0.5B es perfecto para pruebas locales de alta velocidad en equipos de bajos recursos.
REPO_ID = "Qwen/Qwen1.5-0.5B-Chat-GGUF"
FILENAME = "qwen1_5-0_5b-chat-q8_0.gguf"

# Directorio de destino
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
OUTPUT_PATH = os.path.join(MODEL_DIR, "model.gguf")

def download_model():
    print(f"Iniciando descarga del modelo {REPO_ID}...")
    print("Esto puede tardar unos minutos dependiendo de tu conexión a internet.")
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    try:
        # Descarga el archivo GGUF usando HuggingFace Hub
        model_path = hf_hub_download(
            repo_id=REPO_ID, 
            filename=FILENAME, 
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False
        )
        
        # Renombramos a 'model.gguf' para que agent.py lo encuentre automáticamente
        if os.path.exists(OUTPUT_PATH):
            os.remove(OUTPUT_PATH)
        os.rename(model_path, OUTPUT_PATH)
        
        print("\n================================================")
        print("✅ MODELO DESCARGADO E INSTALADO SATISFACTORIAMENTE")
        print(f"Ubicación: {OUTPUT_PATH}")
        print("El Agente V2 ahora tiene la capacidad de pensar.")
        print("================================================\n")
    except Exception as e:
        print(f"\n❌ Error durante la descarga: {e}")
        print("Asegúrate de tener conexión a internet estable.")

if __name__ == "__main__":
    download_model()
