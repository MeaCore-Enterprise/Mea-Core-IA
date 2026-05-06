# MEA-Core V3 Hive Mind

**Inteligencia Artificial Distribuida y Auto-Evolutiva**

MEA-Core V3 es un sistema de IA distribuido que opera en red local (LAN), combinando múltiples nodos en un enjambre auto-organizado capaz de buscar conocimiento y mejorar su propio rendimiento.

## Características

- **Arquitectura Swarm**: Múltiples PCs coordinadas en red local
- **Agentes especializados**: Explorer / Worker / Validator
- **Auto-evolutivo**: Modifica su propio harness (como SICA/MiniMax M2.7)
- **Knowledge Gatherer**: Búsqueda web + RAG automático
- **Gemini API**: Integración con Google Gemini para tareas complejas
- **Memoria distribuida**: ChromaDB + Redis para sincronización

## Requisitos

- Python 3.10+
- Redis (Docker)
- 8 GB RAM mínimo
- [API Key de Gemini](https://aistudio.google.com/app/apikey) (opcional)

## Instalación

### 1. Clonar y configurar

```bash
# Copiar configuración
copy .env.example .env
```

Edita `.env` y reemplaza:
```
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Iniciar Redis

```bash
docker-compose up -d
```

## Ejecución

### Servidor principal (Nodo 1)

```bash
uvicorn api.server:app --port 8000 --reload
```

### Nodos adicionales (otras PCs)

En otra terminal/PC:
```bash
set PORT=8001
uvicorn api.server:app --port 8001
```

## API Endpoints

| Método | Endpoint | Descripción |
|-------|----------|-------------|
| GET | `/` | Información del sistema |
| GET | `/health` | Estado de salud |
| POST | `/chat` | Chatear con IA |
| POST | `/learn` | Enseñar un hecho |
| GET | `/swarm/stats` | Estadísticas del swarm |
| POST | `/swarm/execute` | Ejecutar tarea en swarm |
| GET | `/knowledge/search?q=...` | Buscar en la web |
| GET | `/memory/search?q=...` | Buscar en memoria |
| POST | `/memory/reset` | Resetear memoria |

## Pruebas

### Aprender algo desde Nodo 1
```bash
curl -X POST "http://localhost:8000/learn" -H "Content-Type: application/json" -d "{\"text\": \"El código secreto es 12345\"}"
```

### Preguntar desde Nodo 2
```bash
curl -X POST "http://localhost:8001/chat" -H "Content-Type: application/json" -d "{\"text\": \"¿Cuál es el código secreto?\"}"
```

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│              MEA-CORE V3 HIVE MIND              │
├─────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ Nodo 1  │◄─►│ Nodo 2  │◄─►│ Nodo N  │         │
│  │ (Main)  │  │ (Work)  │  │ (Edge)  │         │
│  └─────────┘  └─────────┘  └─────────┘         │
│         ▲         ▲         ▲                  │
│         └────────┼────────┘                  │
│                  ▼                           │
│         ┌───────────────┐                    │
│         │ Redis Broker │                    │
│         └───────────────┘                    │
├─────────────────────────────────────────────────┤
│  Módulos:                                  │
│  • mea/ (núcleo)                         │
│  • agents/ (swarm)                        │
│  • evolution/ (auto-evo)                │
│  • knowledge/ (búsqueda)                │
└─────────────────────────────────────────────────┘
```

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key de Gemini | - |
| `REDIS_URL` | URL de Redis | `redis://localhost:6379` |
| `RUN_MODE` | Modo: local/hybrid/api | `hybrid` |
| `PORT` | Puerto del servidor | `8000` |
| `LLM_MODEL_PATH` | Ruta al modelo GGUF | `./models/model.gguf` |

## Seguridad

- El archivo `.env` contiene secrets y está en `.gitignore`
- Nunca commitear API keys al repositorio
- Usar diferentes API keys por nodo si es necesario

## Licencia

MIT

## Inspiración

Basado en conceptos de:
- MiniMax M2.7 (Self-Evolution)
- SICA (Self-Improving Coding Agent)
- SwarmSys (Decentralized Multi-Agent)
- Fortytwo (Peer-Ranked Consensus)