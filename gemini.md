# MEA-Core-IA Project Analysis

## 1. Project Overview

**MEA-Core** is a Python-based project to develop an experimental, lightweight, and modular Artificial Intelligence that can run locally on limited hardware. Its core philosophy is to be independent of cloud servers for its main operations.

The project is architected to be highly modular, with distinct components for core functionalities like ethics, memory, knowledge, and curiosity. It's designed to be extensible through a plugin system. The AI can be interacted with via a command-line interface (CLI), and it also includes components for a server-based API and bots for platforms like Discord and Telegram.

A key feature is its ability to learn from documents. The knowledge base can be populated using external text, and the AI uses techniques like BM25 and semantic search to retrieve relevant information. The "brain" of the AI is configurable and can operate in different modes: a simple rule-based system, a more advanced rules engine (`Experta`), or a machine learning model (using `scikit-learn`) for intent classification.

## 2. Building and Running

### 2.1. Installation

1.  **Clone the repository** (if not already done).
2.  **(Recommended)** Create and activate a Python virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:** The project's dependencies are listed in `requirements.txt`. The `main.py` script automatically handles this.
    ```bash
    pip install -r requirements.txt
    ```

### 2.2. Initial Setup

Before the first run, the knowledge base needs to be populated. The `main.py` script also automates this by running the `tools/import_manifestos.py` script if the database is not found.

### 2.3. Running the Application

There are multiple ways to run the project:

*   **Main CLI Bot (Recommended):** The primary entry point which handles all setup and starts the interactive CLI.
    ```bash
    python main.py
    ```
*   **Direct CLI Bot:** To run the CLI bot without the automated setup checks.
    ```bash
    python bots/cli_bot.py
    ```
*   **API Server:** The project includes a FastAPI server for remote learning and interaction. The `main.py` script can start this automatically if configured. To run it manually:
    ```bash
    uvicorn server.main:app --reload
    ```

### 2.4. Running Tests

The project uses `pytest` for testing. There are currently 22 tests defined in the `tests/` directory.
```bash
pytest
```

## 3. Project Structure & Conventions

*   **Application Core (`core/`):** This is the heart of the AI.
    *   `brain.py`: Manages response generation, switching between rule-based, ML, and knowledge-base lookups.
    *   `engine.py`: A simpler, initial version of the core logic.
    *   `memory.py`, `knowledge_base.py`: Handle memory and information retrieval.
    *   `ethics.py`, `goals.py`, `curiosity.py`: High-level AI concepts implemented as modules.
    *   `settings_manager.py`: Manages project configuration.
*   **Bots (`bots/`):** Contains the different interfaces for interacting with the AI (CLI, Discord, Telegram).
*   **Configuration (`config/`):**
    *   `settings.json`: Main configuration file for toggling features like `remote_learning` or the brain's `mode`.
    *   `responses.json`: Contains predefined conversational responses (greetings, specific answers).
*   **Data (`data/`):** Stores persistent data like the memory and knowledge base SQLite databases.
*   **Documentation (`docs/`):** Contains high-level planning documents like the AI Manifesto and Technical Roadmap, which define the project's vision and architecture.
*   **Tools (`tools/`):** Includes utility scripts for tasks like backing up databases or importing knowledge.
*   **Development Conventions:**
    *   The code follows a modular and decoupled architecture, as outlined in `docs/ROADMAP_TECNICO.md`.
    *   Testing is done with `pytest`, and test files are kept separate in the `tests/` directory.
    *   The project has `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` files, indicating a standard open-source contribution workflow.
