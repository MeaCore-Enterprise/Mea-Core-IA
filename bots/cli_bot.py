import requests

API_URL = "http://localhost:8000/ask"

while True:
    user_input = input("Tú > ")
    if user_input.lower() in ["exit()", "salir"]:
        break
    try:
                response = requests.post(API_URL, json={"question": user_input})
        response.raise_for_status()  # Lanza una excepción para errores HTTP
        print("Mea-Core >", response.json()["answer"])
    except requests.exceptions.RequestException as e:
        print(f"\n[Error de Conexión] No se pudo conectar a la API en {API_URL}.")
        print("Asegúrate de que el servidor esté corriendo: uvicorn server.app:app --reload --host 0.0.0.0 --port 8000")
        break
    except Exception as e:
        print(f"Ocurrió un error: {e}")
