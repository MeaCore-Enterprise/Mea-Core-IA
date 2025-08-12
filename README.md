# 🧠 MEA-Core: IA Ligera Local

¡Bienvenido a MEA-Core! Este es un proyecto experimental para desarrollar una inteligencia artificial **extremadamente ligera**, que corre localmente en hardware limitado, sin depender de servidores ni nubes.

---

## 🚀 Guía de Inicio Rápido

Sigue estos pasos para poner en marcha el proyecto.

### 1. Requisitos Previos
- Python 3.10 o superior.
- Git.

### 2. Instalación

```bash
# Clona el repositorio (si aún no lo has hecho)
git clone <URL_DEL_REPOSITORIO>
cd MEA-Core-IA

# (Recomendado) Crea y activa un entorno virtual
python -m venv venv
# En Windows
.\venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate

# Instala las dependencias
pip install -r requirements.txt
```

### 3. Poblar la Base de Conocimiento (¡Nuevo!)

La IA ahora puede aprender de documentos externos. Hemos incluido un importador para los "Manifiestos de IA". Ejecútalo una vez para poblar la base de conocimiento.

```bash
python tools/import_manifestos.py
```

### 4. Ejecutar el Bot de Línea de Comandos (CLI)

Este es el método principal para interactuar con la IA.

```bash
python main.py
```

Ahora puedes hacerle preguntas como `¿cuáles son tus principios éticos?`.

---

## 🛠️ Herramientas Adicionales

### Backup de Bases de Datos

Para crear una copia de seguridad de tu memoria de conversaciones (`mea_memory.db`) y de la base de conocimiento (`knowledge_base.db`), ejecuta:

```bash
python tools/backup_db.py
```
Los backups se guardarán en la carpeta `data/backups/`.

---

## ✅ Ejecutar las Pruebas

El proyecto incluye un conjunto de pruebas unitarias y de integración para asegurar la calidad del código. Ahora hay 22 tests.

```bash
pytest
```

---

## 🤖 Arquitectura Avanzada

### Aprendizaje Remoto y Servidor Central

- **Función:** Mea-Core puede enviar las conversaciones a un servidor central para un análisis y aprendizaje a mayor escala.
- **Configuración:** Se controla desde `config/settings.json` -> `remote_learning` -> `enabled` (por defecto `false`).
- **Para ejecutar el servidor:** Abre una segunda terminal y corre `uvicorn server.main:app --reload`.

### Cerebro Neuronal

- **Función:** El `core/brain.py` puede usar un clasificador de texto (TF-IDF + Regresión Logística) para encontrar la mejor respuesta.
- **Configuración:** Se controla desde `config/settings.json` -> `brain` -> `mode` (`rule` o `ml`).
- **Fallback:** Si `scikit-learn` no está instalado, el sistema volverá al modo `rule` automáticamente.

---

## 💡 Meta final
Crear una IA que funcione como "Jarvis para todos", incluso en PCs antiguas.

¿Te animas a contribuir o proponer ideas?  
🛸 Abre un Issue, haz un Fork o contacta por redes MEA-Technology.
