"""
Clase base para todos los bots de MEA-Core.

Esta clase maneja la inicialización de los componentes del nócleo y la lógica
comón para el manejo de comandos, permitiendo que los bots específicos de cada
plataforma se centren ónicamente en la interacción con el usuario.
"""

import sys
import os
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gestor_configuracion import SettingsManager
from core.memoria import MemoryStore
from core.etica import EthicsCore
from core.cerebro import Brain
from core.logger_remoto import RemoteLogger
from core.controlador_enjambre import SwarmController
from core.conocimiento import KnowledgeManager
from core.controlador_replicacion import ReplicationController # Importar el controlador de replicación

class BaseBot:
    """Clase base abstracta para los bots de MEA-Core."""

    def __init__(self, node_id: str):
        """
        Inicializa los componentes comunes del nócleo de la IA.

        Args:
            node_id (str): Un identificador ónico para la instancia del bot (ej. 'cli', 'discord').
        """
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        self.responses = self.settings_manager.get_responses()
        
        # Configuración de la base de datos
        from core.database import engine, SessionLocal
        self.db_session = SessionLocal()

        # Instanciación de componentes del núcleo
        self.memory = MemoryStore()
        self.knowledge_base = KnowledgeManager()
        self.swarm_controller = SwarmController(node_id=node_id)
        self.ethics = EthicsCore()

        self.brain = Brain(
            settings=self.settings,
            responses=self.responses,
            memory=self.memory,
            knowledge=self.knowledge_base,
            ethics=self.ethics
        )
        self.remote_logger = RemoteLogger(self.settings)
        self.context: List[str] = []
        self.is_running: bool = True

    async def send_message(self, message: str, **kwargs):
        """Método abstracto para enviar un mensaje a la plataforma."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")

    async def handle_command(self, command: str, **kwargs) -> bool:
        """
        Procesa comandos comunes que empiezan con '!'.

        Returns:
            bool: True si el comando fue manejado, False en caso contrario.
        """
        command_lower = command.lower()

        # Comandos de memoria episódica (reemplazan !set y !get)
        if command_lower.startswith("!log "):
            try:
                _, *value_parts = command.split()
                log_content = " ".join(value_parts)
                self.memory.log_episode(self.db_session, "manual_log", "command", {"content": log_content})
                await self.send_message(f"[Memoria] Anotado: '{log_content}'", **kwargs)
            except ValueError:
                await self.send_message("[Error] Comando !log mal formado.", **kwargs)
            return True

        if command_lower.startswith("!query "):
            try:
                _, *query_parts = command.split()
                query = " ".join(query_parts)
                results = self.memory.get_memory(self.db_session, query)
                response = f"[Memoria] Resultados para '{query}':\n"
                if not results:
                    response += "- No se encontraron recuerdos relevantes."
                else:
                    for res in results:
                        response += f"- {res['data']}\n"
                await self.send_message(response, **kwargs)
            except ValueError:
                await self.send_message("[Error] Comando !query mal formado.", **kwargs)
            return True

        return False

    async def process_message(self, message: str, **kwargs):
        """Procesa un mensaje de usuario, lo pasa al cerebro y envía la respuesta."""
        if await self.handle_command(message, **kwargs):
            return

        if not self.ethics.check_action(message):
            explanation = self.ethics.explain_decision(message)
            await self.send_message(f"[Etica] {explanation}", **kwargs)
            return

        responses = self.brain.get_response(self.db_session, message, context=self.context)
        for response in responses:
            await self.send_message(response, **kwargs)

        # Registrar la conversación como un episodio en la memoria
        self.memory.log_episode(
            self.db_session,
            type="conversation",
            source="user_interaction",
            data={"user_input": message, "bot_output": responses}
        )
        self.remote_logger.log(user_input=message, bot_output=responses)
        self.context.append(message)

    def run(self):
        """Método abstracto para iniciar el bot."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")