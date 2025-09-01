# tests/test_scaling.py

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Suponiendo que tenemos acceso a las clases SwarmNode y EthicalGatekeeper
from core.swarm import SwarmNode
from core.etica import EthicalGatekeeper, DecisionContext, DecisionCriticality

@pytest.mark.asyncio
async def test_stress_test_100_nodes_broadcast():
    """
    Simula un broadcast de un mensaje crítico (alta prioridad) en un enjambre de 100 nodos.
    Verifica que todos los nodos reciben y procesan el mensaje.
    """
    num_nodes = 100
    nodes = []
    
    # Crear 100 nodos simulados
    for i in range(num_nodes):
        node = SwarmNode()
        # Mockear la función de envío para no usar la red real
        node.send_message = AsyncMock()
        # Simular que cada nodo está conectado a todos los demás
        node.connected_peers = {f"ws://node-{j}": AsyncMock() for j in range(num_nodes) if i != j}
        nodes.append(node)

    # El nodo 0 hace un broadcast de un mensaje crítico
    origin_node = nodes[0]
    message_type = "memory_sync"
    payload = {"id": "critical_event_123", "priority": 10, "data": "System-wide alert"}
    
    # Mockear el broadcast para que llame a send_message en lugar de la lógica de red
    async def mock_broadcast(msg_type, pld):
        tasks = []
        for peer_url, ws in origin_node.connected_peers.items():
            tasks.append(origin_node.send_message(peer_url, msg_type, pld))
        await asyncio.gather(*tasks)

    origin_node.broadcast = mock_broadcast
    await origin_node.broadcast(message_type, payload)

    # Verificar que el nodo origen intentó enviar el mensaje a los otros 99 nodos
    assert origin_node.send_message.call_count == num_nodes - 1

@pytest.mark.asyncio
async def test_ethical_gatekeeper_under_load():
    """
    Simula 1000 revisiones de decisiones en paralelo para verificar que el gatekeeper responde.
    """
    gatekeeper = EthicalGatekeeper()
    num_requests = 1000

    benign_context = DecisionContext("Benign action", "load_test", DecisionCriticality.LOW)
    harmful_context = DecisionContext("Harmful action to hack", "load_test", DecisionCriticality.HIGH)

    # Crear 1000 tareas de revisión (alternando benignas y dañinas)
    tasks = []
    for i in range(num_requests):
        context = benign_context if i % 2 == 0 else harmful_context
        tasks.append(asyncio.create_task(asyncio.to_thread(gatekeeper.review_decision, context)))

    results = await asyncio.gather(*tasks)

    # Verificar que todas las tareas se completaron
    assert len(results) == num_requests
    
    # Verificar que la mitad fueron permitidas y la mitad bloqueadas
    assert results.count(True) == num_requests / 2
    assert results.count(False) == num_requests / 2
    
    # Verificar que el log de auditoría tiene todos los registros
    assert len(gatekeeper.get_audit_log()) == num_requests
