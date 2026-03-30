# MEA-Core-Enterprise

<div align="center">
  <img src="branding/logo.svg" alt="Mea-Core-Enterprise Logo" width="400"/>
</div>

**Copyright (c) 2025, Mea-Core-Enterprise. All rights reserved.**

---

## 1. Overview

MEA-Core is a modular artificial intelligence platform designed for local execution, ensuring data privacy and operational independence.

This software is confidential and proprietary. Unauthorized copying, distribution, or use of this software, or any part thereof, is strictly prohibited.

## 2. Project Status

- **Fase 1: Consolidación Interna ✅ (Completada)**
- **Fase 2: Expansión Visible ⏳ (En Progreso)**

> Para una visión estratégica detallada, incluyendo el roadmap completo y los objetivos de negocio, por favor consulta nuestro **[README para Enterprise](README_ENTERPRISE.md)**.

> Para un seguimiento técnico de las tareas, consulta los checklists de cada fase: `docs/CHECKLIST.md` (Fase 1) y `CHECKLIST_FASE2.md` (Fase 2).

## 3. Core Features

- **Local AI Engine:** A language and reasoning engine that provides insights from internal knowledge bases.
- **Modular and Scalable Architecture:** Built with decoupled components for ethics, memory, knowledge, and reasoning.
- **Secure, Local-First Operation:** All core processing and data storage are handled locally.
- **Integrated Knowledge Base:** The system leverages its own knowledge base for reasoning and responses.
- **Multi-Interface Deployment:** Includes a Command-Line Interface (CLI) and a REST API.

## 4. Ejemplos de Interacción (CLI)

```text
Usuario > ¿Qué sabes del Proyecto Omega?
Mea-Core > El Proyecto Omega es un manifiesto orientado a la soberanía digital...
```

## 5. Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip` for package management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/KronoxYT/Mea-Core.git
    cd Mea-Core
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    # On Windows, use: .venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    The main script will attempt to do this for you, but you can do it manually:
    ```bash
    pip install -r requirements.txt
    ```

## 6. Usage

### Command-Line Interface (CLI)

The primary way to interact with Mea-Core is through the CLI.

1.  **Run the main application:**
    ```bash
    python main.py
    ```

2.  **Available Commands:**
    -   Type any message to chat with the AI.
    -   `/reset-memory`: Clears the entire conversation history and knowledge. Requires confirmation.
    -   `salir` or `quit`: Exits the application.

### API Server

Mea-Core also includes a FastAPI server for programmatic access.

1.  **Run the server:**
    ```bash
    uvicorn server.main:app --reload
    ```

2.  **Access the API documentation:**
    Once the server is running, you can access the interactive API documentation (Swagger UI) at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## 7. Disclaimer

> **Este software es experimental, en fase de investigación y desarrollo. Su uso sin autorización puede tener consecuencias legales.**

---
© 2025 Mea-Core-Enterprise. Todos los derechos reservados.  
Sitio oficial: [próximamente]  
Contacto: contacto@meacore.ai
