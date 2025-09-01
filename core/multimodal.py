# core/multimodal.py

import torch
from torchvision import models, transforms
from PIL import Image
from typing import List, Tuple
import requests
from io import BytesIO

# --- Procesamiento de Imágenes ---

class ImageProcessor:
    """
    Procesa imágenes para realizar clasificación simple usando un modelo pre-entrenado.
    """
    def __init__(self):
        # Cargar un modelo pre-entrenado (ResNet18 es ligero y rápido)
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.model.eval() # Poner el modelo en modo de evaluación

        # Cargar las etiquetas de ImageNet
        try:
            response = requests.get("https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt")
            self.labels = [line.strip() for line in response.text.split("\n")]
        except Exception:
            # Fallback por si no hay conexión
            self.labels = ["unknown"] * 1000

        # Definir las transformaciones que se aplicarán a la imagen
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def classify_image_from_url(self, image_url: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Descarga una imagen desde una URL y la clasifica.
        """
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content)).convert('RGB')
            return self._classify(img, top_k)
        except Exception as e:
            print(f"Error procesando imagen desde URL {image_url}: {e}")
            return [("Error de procesamiento", 0.0)]

    def classify_image_from_path(self, image_path: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Carga una imagen desde una ruta local y la clasifica.
        """
        try:
            img = Image.open(image_path).convert('RGB')
            return self._classify(img, top_k)
        except Exception as e:
            print(f"Error procesando imagen desde {image_path}: {e}")
            return [("Error de procesamiento", 0.0)]

    def _classify(self, img: Image.Image, top_k: int) -> List[Tuple[str, float]]:
        """
        Realiza la clasificación de la imagen.
        """
        img_t = self.preprocess(img)
        batch_t = torch.unsqueeze(img_t, 0)

        with torch.no_grad():
            out = self.model(batch_t)
        
        probabilities = torch.nn.functional.softmax(out[0], dim=0)
        
        # Obtener las top K predicciones
        top_prob, top_catid = torch.topk(probabilities, top_k)
        
        results = []
        for i in range(top_prob.size(0)):
            label = self.labels[top_catid[i]]
            probability = top_prob[i].item()
            results.append((label, probability))
            
        return results

# --- Procesamiento de Audio (Stub) ---

class AudioProcessor:
    """
    Un stub (marcador de posición) para la funcionalidad de voz a texto.
    En una implementación real, esto se conectaría con Whisper.cpp o una API.
    """
    def transcribe_audio_from_path(self, audio_path: str) -> str:
        print(f"[Audio STUB] Transcribiendo audio desde: {audio_path}")
        # Simulación de la transcripción
        if "hello" in audio_path:
            return "Hello, this is a test transcription."
        else:
            return "This is a simulated transcription of an audio file."

if __name__ == '__main__':
    # --- Demo de Clasificación de Imagen ---
    print("--- Demo de Clasificación de Imagen ---")
    image_proc = ImageProcessor()
    # URL de una imagen de ejemplo (un perro Golden Retriever)
    image_url = "https://github.com/pytorch/hub/raw/master/images/dog.jpg"
    results = image_proc.classify_image_from_url(image_url)
    print(f"Clasificación para la imagen en {image_url}:")
    for label, prob in results:
        print(f"  - {label}: {prob:.2%}")

    # --- Demo de Transcripción de Audio ---
    print("\n--- Demo de Transcripción de Audio (Stub) ---")
    audio_proc = AudioProcessor()
    transcription = audio_proc.transcribe_audio_from_path("/path/to/some/hello_world.wav")
    print(f"Texto transcrito: '{transcription}'")
