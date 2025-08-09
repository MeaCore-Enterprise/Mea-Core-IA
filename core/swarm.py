"""
Módulo de comunicación y sincronización de enjambre para MEA-Core-IA.
"""
from typing import List, Dict, Any

class SwarmNode:
    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.peers: List[str] = []
        self.state: Dict[str, Any] = {}

    def connect(self, peer_id: str) -> None:
        if peer_id not in self.peers:
            self.peers.append(peer_id)

    def broadcast(self, message: str) -> None:
        # Simulación: imprime el mensaje a todos los peers
        for peer in self.peers:
            print(f"[Swarm] {self.node_id} -> {peer}: {message}")

    def sync_state(self, new_state: Dict[str, Any]) -> None:
        self.state.update(new_state)
