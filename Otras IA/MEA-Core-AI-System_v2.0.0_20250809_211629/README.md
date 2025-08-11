# MEA-Core: Advanced Local AI Assistant System

MEA-Core es un sistema de asistente de IA local avanzado inspirado en Jarvis, que opera completamente offline con redes neuronales personalizadas y algoritmos de aprendizaje automático.

## ✨ Características Principales

### 🧠 Sistema Neural Avanzado
- **Clasificación de Intenciones**: Red neuronal personalizada para entender intenciones de consulta
- **Aprendizaje Incremental**: Adaptación en tiempo real a preferencias del usuario
- **Motor de Personalidad**: Rasgos de personalidad de IA personalizables
- **Sistema de Aprendizaje**: Mejora continua de interacciones del usuario

### 📚 Inteligencia de Documentos
- **Clasificación Inteligente**: Categorización automática de documentos
- **Análisis Semántico**: Extracción de entidades y detección de relaciones
- **Agrupación Inteligente**: Organización dinámica de resultados

### 🌐 Computación Distribuida
- **Granja de Inferencia**: Sistema distribuido tipo render farm
- **Redes Neuronales Ultraligeras**: Modelos optimizados para hardware de bajos recursos
- **Balanceador de Carga**: Distribución inteligente de tareas de IA
- **Workers Heterogéneos**: Soporte para PCs, laptops, Raspberry Pi, móviles

### 🎤 Interacciones Avanzadas
- **Procesamiento de Voz**: Capacidades de speech-to-text y text-to-speech
- **Reconocimiento de Gestos**: Soporte para navegación basada en gestos
- **Pantalla HUD**: Modo de visualización holográfica estilo heads-up display
- **Interfaz Multimodal**: Integración fluida de texto, voz y gestos

## 🔧 Instalación y Configuración

### Requisitos del Sistema
- Python 3.8+
- 4GB RAM mínimo (optimizado para hardware de bajos recursos)
- Procesador: Celeron o superior
- Sistema operativo: Linux, Windows, macOS

### Instalación Rápida

1. **Extraer el paquete**:
   ```bash
   unzip MEA-Core-AI-System_v2.0.0.zip
   cd MEA-Core-AI-System
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar el sistema**:
   ```bash
   python main.py
   ```

4. **Acceder a la interfaz web**:
   Abrir http://localhost:5000 en tu navegador

### Configuración del Cluster Distribuido

1. **Editar configuración**:
   ```bash
   nano mea_cluster_config.yaml
   ```

2. **Iniciar workers adicionales**:
   ```bash
   python -m core.distributed --worker
   ```

## 📖 Uso

### Interfaz Web
- **Chat**: Interfaz de chat en tiempo real con análisis de IA
- **Subida de Documentos**: Soporte para PDF y archivos de texto
- **Panel de Control**: Estadísticas del sistema y monitoreo
- **Configuración de Personalidad**: Ajustar rasgos de personalidad de IA

### API REST
- `POST /search` - Búsqueda inteligente de documentos
- `POST /add_text` - Añadir contenido de texto
- `POST /add_pdf` - Subir documentos PDF
- `GET /health` - Estado del sistema
- `POST /personality` - Ajustar personalidad de IA
- `POST /analyze` - Análisis de contenido avanzado

### Sistema Distribuido
- `GET /distributed/status` - Estado del cluster
- `POST /distributed/submit` - Enviar tarea distribuida
- `GET /models/ultralight` - Estado de redes neuronales

## 🎯 Casos de Uso

### Personal
- Asistente de investigación personal
- Gestión de documentos y conocimiento
- Análisis de texto y escritura

### Profesional
- Soporte a la toma de decisiones
- Análisis de documentos legales/médicos
- Sistema de gestión del conocimiento organizacional

### Desarrollo
- Prototipado de IA local
- Investigación en redes neuronales ligeras
- Computación distribuida de baja latencia

## 🏗️ Arquitectura

### Componentes Principales
- **Motor BM25**: Indexación y recuperación de documentos
- **Redes Neuronales**: Clasificación de intenciones y documentos
- **Sistema de Aprendizaje**: Adaptación y personalización continua
- **Scheduler Distribuido**: Orquestación de tareas de IA
- **Interfaz Web**: Frontend responsive estilo Jarvis

### Tecnologías
- **Backend**: Flask, NumPy, psutil
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **IA**: Redes neuronales personalizadas, algoritmos BM25
- **Almacenamiento**: JSONL, sistema de archivos local

## 🔄 Desarrollo y Contribución

### Estructura del Proyecto
```
MEA-Core/
├── main.py                 # Punto de entrada
├── app.py                  # Aplicación Flask principal
├── core/                   # Módulos de IA principales
│   ├── bm25.py            # Motor de búsqueda BM25
│   ├── neural.py          # Redes neuronales
│   ├── distributed.py     # Sistema distribuido
│   └── ultralight_nn.py   # Redes ultraligeras
├── static/                 # Assets web
├── data/                   # Almacenamiento de datos
└── mea_cluster_config.yaml # Configuración de cluster
```

### Personalización
- Modificar `mea_cluster_config.yaml` para configuración de cluster
- Ajustar modelos en `core/ultralight_nn.py`
- Personalizar interfaz en `static/`

## 🚀 Roadmap

### Próximas Características
- [ ] WebGPU para aceleración en navegadores
- [ ] Soporte para más formatos de documentos
- [ ] API de integración con servicios externos  
- [ ] Modo de depuración y profiling avanzado
- [ ] Soporte nativo para contenedores Docker

### Optimizaciones Planificadas
- [ ] Cuantización INT4 para modelos
- [ ] Poda estructurada de redes neuronales
- [ ] Compilación JIT de kernels críticos
- [ ] Caché adaptativo inteligente

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver LICENSE para detalles.

## 🤝 Soporte

Para soporte técnico, documentación adicional o consultas:
- Documentación: Revisar `replit.md` para detalles técnicos
- Configuración: Ver `mea_cluster_config.yaml` para opciones avanzadas
- Logs: Los archivos de log se encuentran en `data/logs/`

---

**MEA-Core v2.0** - Sistema de IA Local Distribuido de Próxima Generación
Desarrollado con ❤️ para la comunidad de IA local y privada.
