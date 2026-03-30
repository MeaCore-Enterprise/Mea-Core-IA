
import argparse
from engine import MeaEngine

def main(args):
    # Carga el modelo entrenado desde el archivo especificado
    try:
        engine = MeaEngine.load_model(args.model_path)
    except FileNotFoundError:
        print(f"Error: No se encontro el archivo del modelo en '{args.model_path}'.")
        print("Asegurate de haber entrenado el modelo primero con 'train.py'.")
        return

    # Bucle interactivo para probar palabras
    print("\nMotor Mea-Core cargado. Escribe una palabra para encontrar terminos similares.")
    print("Escribe 'exit()' o presiona Ctrl+C para salir.")
    
    while True:
        try:
            # Solicita una palabra al usuario
            input_word = input("\nPalabra a consultar > ")
            if input_word.lower() == 'exit()':
                break

            # Encuentra y muestra las palabras mas similares
            similar_words = engine.find_similar_words(input_word, top_n=args.top_n)
            
            if similar_words:
                print(f"\nPalabras mas similares a '{input_word}':")
                # Imprime cada palabra similar y su puntuacion de similitud
                for word, score in similar_words:
                    print(f"- {word} (similitud: {score:.4f})")

        except KeyboardInterrupt:
            print("\nSaliendo del modo de prueba.")
            break
        except Exception as e:
            print(f"Ocurrio un error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probar el motor de Mea-Core entrenado.")

    parser.add_argument("--model_path", type=str, default="mea_engine.pth", help="Ruta al archivo del modelo entrenado.")
    parser.add_argument("--top_n", type=int, default=10, help="Numero de palabras similares a mostrar.")

    args = parser.parse_args()
    main(args)
