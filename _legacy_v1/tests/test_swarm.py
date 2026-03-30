# tests/test_swarm.py

import asyncio
import pytest
import websockets
from unittest.mock import MagicMock, AsyncMock

from core.swarm import SwarmNode
from core.gestor_configuracion import GestorConfiguracion

# Usar pytest-asyncio para marcar tests asíncronos
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_config():
    """Crea un mock del GestorConfiguracion."""
    mock = MagicMock(spec=GestorConfiguracion)
    mock.get_node_id.return_value = "test-node-0"
    return mock

async def test_node_connects_to_peers(mock_config):
    """Verifica que un nodo intenta conectarse a los peers de su configuración."""
    peers = ["ws://localhost:8001", "ws://localhost:8002"]
    mock_config.get_swarm_peers.return_value = peers
    
    node = SwarmNode()
    node.config = mock_config
    
    # Mockear la función de conexión de websockets
    websockets.connect = AsyncMock()
    
    await node.connect_to_peers()
    
    assert websockets.connect.call_count == 2
    websockets.connect.assert_any_call(peers[0])
    websockets.connect.assert_any_call(peers[1])

async def test_broadcast_sends_to_all_connected_peers(mock_config):
    """Verifica que el broadcast envía un mensaje a todos los peers conectados."""
    mock_config.get_swarm_peers.return_value = []
    node = SwarmNode()
    node.config = mock_config

    # Simular dos peers conectados
    mock_ws_1 = AsyncMock(spec=websockets.WebSocketClientProtocol)
    mock_ws_2 = AsyncMock(spec=websockets.WebSocketClientProtocol)
    node.connected_peers = {
        "ws://peer1:8000": mock_ws_1,
        "ws://peer2:8000": mock_ws_2
    }

    message = {"type": "state_update", "payload": {"status": "testing"}}
    await node.broadcast(message['type'], message['payload'])

    # Verificar que se llamó a send() en ambos websockets
    assert mock_ws_1.send.call_count == 1
    assert mock_ws_2.send.call_count == 1

async def test_scalability_simulation_10_nodes():
    """
    Simula un escenario con 10 nodos para verificar que la lógica de conexión escala.
    Esto no crea conexiones reales, solo simula la lógica de la aplicación.
    """
    num_nodes = 10
    nodes = []
    all_peers = [f"ws://node-{i}:8000" for i in range(num_nodes)]

    # Mockear la conexión de websockets para que no falle
    websockets.connect = AsyncMock()

    for i in range(num_nodes):
        mock_config = MagicMock(spec=GestorConfiguracion)
        mock_config.get_node_id.return_value = f"node-{i}"
        # Cada nodo conoce a todos los demás (excluyéndose a sí mismo)
        peer_list = [p for p in all_peers if p != f"ws://node-{i}:8000"]
        mock_config.get_swarm_peers.return_value = peer_list
        
        node = SwarmNode()
        node.config = mock_config
        nodes.append(node)

    # Simular que todos los nodos intentan conectarse a sus peers
    connection_tasks = [node.connect_to_peers() for node in nodes]
    await asyncio.gather(*connection_tasks)

    # Cada uno de los 10 nodos debe intentar conectarse a los otros 9
    total_connection_attempts = 10 * 9
    assert websockets.connect.call_count == total_connection_attempts