
import torch
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import argparse
import glob
import re
from engine import MeaEngine

def tokenize(text):
    """Funcion simple de tokenizacion."""
    return re.findall(r'\b\w+\b', text.lower())

def create_skipgram_dataset(tokens, vocab, window_size=2):
    """
    Crea pares de (palabra_objetivo, palabra_de_contexto) para el modelo Skip-gram.
    """
    targets = []
    contexts = []
    
    # Convierte todos los tokens a indices numericos
    indexed_tokens = [vocab.get_index(token) for token in tokens]

    for i, target_idx in enumerate(indexed_tokens):
        # Ignoramos palabras desconocidas en el centro
        if target_idx == 0:
            continue

        # Define la ventana de contexto alrededor de la palabra objetivo
        start = max(0, i - window_size)
        end = min(len(indexed_tokens), i + window_size + 1)

        # Recorre las palabras en la ventana
        for j in range(start, end):
            if i == j: # No queremos que la palabra sea su propio contexto
                continue
            
            context_idx = indexed_tokens[j]
            # Ignoramos palabras de contexto desconocidas
            if context_idx == 0:
                continue
            
            targets.append(target_idx)
            contexts.append(context_idx)
            
    return torch.LongTensor(targets), torch.LongTensor(contexts)

def main(args):
    # --- 1. Carga y Preparacion de Datos ---
    print("Cargando archivos de texto...")
    corpus = ""
    # Busca todos los archivos .txt en la ruta especificada
    for file_path in glob.glob(f"{args.data_path}/**/*.txt", recursive=True):
        with open(file_path, 'r', encoding='utf-8') as f:
            corpus += f.read() + "\n"
    
    if not corpus:
        print("No se encontraron archivos .txt en la ruta especificada. Abortando.")
        return

    print(f"Se cargaron {len(corpus)} caracteres para el entrenamiento.")

    # --- 2. Construccion del Motor y Vocabulario ---
    engine = MeaEngine(
        embedding_dim=args.embedding_dim,
        min_word_count=args.min_count
    )
    engine.build(corpus)

    # --- 3. Creacion del Dataset de Entrenamiento ---
    print("Creando dataset para Skip-gram...")
    tokens = tokenize(corpus)
    targets, contexts = create_skipgram_dataset(tokens, engine.vocab, args.window_size)
    dataset = TensorDataset(targets, contexts)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    # --- 4. Configuracion del Entrenamiento ---
    model = engine.model
    # Usamos CrossEntropyLoss que combina LogSoftmax y NLLLoss para eficiencia
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    # Mueve el modelo a la GPU si esta disponible
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Entrenando en dispositivo: {device}")

    # --- 5. Bucle de Entrenamiento ---
    model.train() # Pone el modelo en modo de entrenamiento
    for epoch in range(args.epochs):
        total_loss = 0
        for i, (target_batch, context_batch) in enumerate(dataloader):
            # Mueve los datos al dispositivo (CPU/GPU)
            target_batch = target_batch.to(device)
            context_batch = context_batch.to(device)

            # Reinicia los gradientes
            optimizer.zero_grad()

            # Forward pass: predecir scores de contexto desde la palabra objetivo
            scores = model(target_batch)

            # Calcular la perdida
            loss = criterion(scores, context_batch)

            # Backward pass: calcular gradientes
            loss.backward()

            # Actualizar los pesos del modelo
            optimizer.step()

            total_loss += loss.item()

            # Imprime el progreso cada N lotes
            if (i + 1) % 100 == 0:
                print(f'Epoch [{epoch+1}/{args.epochs}], Lote [{i+1}/{len(dataloader)}], Perdida: {loss.item():.4f}')
        
        avg_loss = total_loss / len(dataloader)
        print(f'Fin de Epoch [{epoch+1}/{args.epochs}], Perdida Promedio: {avg_loss:.4f}')

    # --- 6. Guardado del Modelo ---
    engine.save_model(args.model_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenar el motor de Mea-Core desde cero.")
    
    parser.add_argument("--data_path", type=str, required=True, help="Ruta a la carpeta con los archivos .txt para entrenar.")
    parser.add_argument("--model_path", type=str, default="mea_engine.pth", help="Ruta donde se guardara el modelo entrenado.")
    parser.add_argument("--embedding_dim", type=int, default=100, help="Dimension de los vectores de embedding.")
    parser.add_argument("--epochs", type=int, default=10, help="Numero de epocas de entrenamiento.")
    parser.add_argument("--batch_size", type=int, default=128, help="Tamaño del lote de entrenamiento.")
    parser.add_argument("--learning_rate", type=float, default=0.001, help="Tasa de aprendizaje.")
    parser.add_argument("--window_size", type=int, default=2, help="Tamaño de la ventana de contexto (palabras a cada lado).")
    parser.add_argument("--min_count", type=int, default=5, help="Frecuencia minima para que una palabra sea incluida en el vocabulario.")

    args = parser.parse_args()
    main(args)
