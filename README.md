# MEA-Core V2 (Arquitectura Distribuida - Swarm AI)

Esta es la recreación desde cero del proyecto MEA-Core con una arquitectura orientada a microservicios/enjambre, diseñada para que múltiples PCs compartan recursos de memoria e inferencia.

## Componentes

1. **Broker de Mensajes (Redis)**: Actúa como el nodo de conexión rápida en tiempo real.
2. **Memoria Vectorial (ChromaDB)**: Reemplaza a SQLite para permitir búsqueda semántica rápida de contexto.
3. **API Gateway (FastAPI)**: El punto de entrada asíncrono para interactuar con el agente.
4. **Agente (Cerebro)**: Lógica principal preparada para inyectar LLMs locales (como Llama.cpp) y comunicarse con el enjambre.

## Cómo Ejecutar (Simulando un enjambre de 2 PCs)

1. **Iniciar el Broker Redis**
   (Requiere tener Docker instalado)
   ```bash
   docker-compose up -d
   ```

2. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Arrancar el Nodo 1 (Simulando PC Principal)**
   En una terminal, ejecuta el servidor en el puerto 8000:
   ```bash
   uvicorn api.server:app --port 8000 --reload
   ```

4. **Arrancar el Nodo 2 (Simulando PC Secundario)**
   En OTRA terminal, ejecuta otra instancia en el puerto 8001 (simulando otra máquina en la red LAN que se conecta al mismo cluster Redis):
   ```bash
   uvicorn api.server:app --port 8001
   ```

## Pruebas de Funcionamiento de Enjambre

Puedes enseñarle un concepto o frase a la IA en el **Nodo 1**:
```bash
curl -X POST "http://localhost:8000/learn" -H "Content-Type: application/json" -d "{\"text\": \"El código secreto de la base de datos es 12345\"}"
```

Y luego preguntarle al **Nodo 2**. Debido a que están conectados con Redis (`memory_sync`), el Nodo 2 interceptó el recuerdo que generó el Nodo 1 y lo agregó a su base de datos vectorial local al instante:
```bash
curl -X POST "http://localhost:8001/chat" -H "Content-Type: application/json" -d "{\"text\": \"¿Cual es el código secreto?\"}"
```
