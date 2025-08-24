# 🧠 MEA-Core: IA Ligera Local

[![CI/CD Status](https://github.com/MEA-Technology/MEA-Core-IA/actions/workflows/ci.yml/badge.svg)](https://github.com/MEA-Technology/MEA-Core-IA/actions/workflows/ci.yml)

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

> **Nota:** Algunas funcionalidades avanzadas (como el modo `rule_engine`) requieren librerías adicionales. Si el sistema te lo indica, puedes instalarlas con `pip install experta`.

### 3. Poblar la Base de Conocimiento

La IA puede aprender de documentos externos. Ejecuta el siguiente script una vez para poblar la base de conocimiento inicial.

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

## ✅ Pruebas e Integración Continua

El proyecto utiliza `pytest` para las pruebas unitarias y de integración. Para ejecutar todas las pruebas localmente:

```bash
pytest
```

Hemos configurado un pipeline de Integración Continua (CI) con GitHub Actions. Las pruebas se ejecutan automáticamente en cada `push` y `pull request` para asegurar la calidad y estabilidad del código.

---

## 🤖 Arquitectura y Modos de Operación

El `core/brain.py` es el componente central que orquesta la respuesta de la IA. Puede operar en tres modos distintos, configurables en `config/settings.json` bajo la clave `brain.mode`.

### Modo `rule_engine` (Por Defecto)
- **Descripción:** Es el modo más avanzado y recomendado. Utiliza un motor de reglas basado en la librería `Experta` para un razonamiento complejo y contextual.
- **Fortalezas:** Permite definir comportamientos sofisticados y manejar diálogos de manera más fluida.

### Modo `ml` (Machine Learning)
- **Descripción:** Utiliza un modelo de clasificación de texto simple (TF-IDF + Regresión Logística con `scikit-learn`) para determinar la intención del usuario y elegir una respuesta.
- **Fallback:** Si `scikit-learn` no está instalado, el sistema no podrá usar este modo.

### Modo `rule` (Simple)
- **Descripción:** Un sistema básico de mapeo directo `pregunta -> respuesta`. Es el modo más simple y se utiliza como fallback si los otros modos no están disponibles o no encuentran una respuesta.

### Servidor para Aprendizaje Remoto
- **Función:** De manera opcional, Mea-Core puede enviar conversaciones a un servidor central para análisis y aprendizaje a mayor escala.
- **Configuración:** Se controla desde `config/settings.json` -> `remote_learning` -> `enabled`.
- **Ejecución:** `uvicorn server.main:app --reload`.

---

## 🛠️ Herramientas Adicionales

Para crear una copia de seguridad de las bases de datos (`memoria` y `conocimiento`), ejecuta:

```bash
python tools/backup_db.py
```

---

## 💡 Meta y Contribuciones

La meta final es crear una IA que funcione como "Jarvis para todos".

¡Las contribuciones son bienvenidas! Nuestro pipeline de CI validará tus cambios. No dudes en abrir un Issue, hacer un Fork o contactar por redes a MEA-Technology.
