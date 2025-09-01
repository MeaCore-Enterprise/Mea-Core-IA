# tools/export_to_onnx.py

import torch
import torch.onnx
import os

# Asumimos que el modelo principal de Mea-Core es un modelo PyTorch.
# Esta es una simulación de cómo se vería el script.

class MeaCoreLanguageModel(torch.nn.Module):
    """ Un modelo de lenguaje de ejemplo que representa el núcleo de Mea-Core. """
    def __init__(self, vocab_size=10000, embedding_dim=128, hidden_dim=256):
        super(MeaCoreLanguageModel, self).__init__()
        self.embedding = torch.nn.Embedding(vocab_size, embedding_dim)
        self.lstm = torch.nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = torch.nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        # Tomamos la última salida de la secuencia
        last_output = lstm_out[:, -1, :]
        output = self.fc(last_output)
        return output

def export_model_to_onnx(model, dummy_input, output_path):
    """
    Exporta un modelo PyTorch al formato ONNX.
    
    Args:
        model (torch.nn.Module): El modelo a exportar.
        dummy_input (torch.Tensor): Un tensor de entrada de ejemplo con las dimensiones correctas.
        output_path (str): La ruta donde se guardará el archivo .onnx.
    """
    print(f"Exportando el modelo a {output_path}...")
    
    try:
        torch.onnx.export(
            model,                        # El modelo a ejecutar
            dummy_input,                  # Entrada del modelo
            output_path,                  # Dónde guardar el modelo
            export_params=True,           # Guardar los pesos entrenados
            opset_version=11,             # La versión de ONNX a usar
            do_constant_folding=True,     # Ejecutar optimizaciones de plegado de constantes
            input_names=['input'],        # Nombre de la entrada
            output_names=['output'],      # Nombre de la salida
            dynamic_axes={'input': {0: 'batch_size', 1: 'sequence_length'}, # Ejes de tamaño variable
                          'output': {0: 'batch_size'}}
        )
        print(f"Modelo exportado exitosamente a {output_path}")
        return True
    except Exception as e:
        print(f"Error durante la exportación a ONNX: {e}")
        return False

if __name__ == "__main__":
    # 1. Cargar o instanciar el modelo de Mea-Core
    # En un caso real, se cargaría un modelo pre-entrenado desde un archivo .pth
    print("Cargando el modelo de Mea-Core (simulado)...")
    mea_model = MeaCoreLanguageModel()
    mea_model.eval() # Poner el modelo en modo de evaluación

    # 2. Definir la ruta de salida
    output_dir = "models/onnx_exports"
    os.makedirs(output_dir, exist_ok=True)
    onnx_output_path = os.path.join(output_dir, "mea_core_model.onnx")

    # 3. Crear una entrada de ejemplo (dummy input)
    # El modelo espera un batch de secuencias de IDs de tokens
    batch_size = 1
    sequence_length = 20
    dummy_input_tensor = torch.randint(0, 10000, (batch_size, sequence_length), dtype=torch.long)

    # 4. Ejecutar la exportación
    export_model_to_onnx(mea_model, dummy_input_tensor, onnx_output_path)
