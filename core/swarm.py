# core/swarm.py

import asyncio
import websockets
import json
from typing import List, Dict, Any

from core.gestor_configuracion import GestorConfiguracion

class SwarmNode:
    """
    Representa un nodo en el enjambre de Mea-Core.
    Gestiona la comunicación (entrada/salida) con otros nodos.
    """
    def __init__(self):
        self.config = GestorConfiguracion()
        self.peers = self.config.get_swarm_peers()
        self.node_id = self.config.get_node_id()  # Asumiendo que habrá un ID de nodo
        self.server = None
        self.connected_peers = {}

    async def start_server(self, host: str, port: int):
        """Inicia el servidor WebSocket para escuchar a otros nodos."""
        print(f"Iniciando servidor de enjambre en {host}:{port}")
        self.server = await websockets.serve(self.handle_connection, host, port)
        await self.server.wait_closed()

    async def handle_connection(self, websocket, path):
        """Maneja las conexiones entrantes de otros nodos."""
        peer_address = websocket.remote_address
        print(f"Nuevo nodo conectado al enjambre: {peer_address}")
        try:
            async for message in websocket:
                await self.process_message(message, peer_address)
        except websockets.exceptions.ConnectionClosed:
            print(f"Nodo del enjambre desconectado: {peer_address}")
        finally:
            # Lógica para eliminar el peer si es necesario
            pass

    async def process_message(self, message: str, source: tuple):
        """Procesa un mensaje recibido de otro nodo."""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("payload")
            
            print(f"Mensaje recibido de {source}: Tipo={message_type}")

            if message_type == "heartbeat":
                # Responder a heartbeats para mantener la conexión viva
                pass
            elif message_type == "state_update":
                # Lógica para actualizar el estado local con la información recibida
                print(f"Actualización de estado recibida: {payload}")
            elif message_type == "vote_request":
                # Lógica para participar en una votación
                print(f"Solicitud de voto recibida: {payload}")
                # Aquí iría la lógica para que el nodo emita su voto
            else:
                print(f"Tipo de mensaje desconocido: {message_type}")

        except json.JSONDecodeError:
            print(f"Error decodificando mensaje JSON de {source}: {message}")

    async def connect_to_peers(self):
        """Intenta conectarse a todos los peers definidos en la configuración."""
        for peer_url in self.peers:
            try:
                websocket = await websockets.connect(peer_url)
                self.connected_peers[peer_url] = websocket
                print(f"Conectado exitosamente al peer: {peer_url}")
                # Opcional: Enviar un mensaje de saludo/identificación
                await self.send_message(peer_url, "handshake", {"node_id": self.node_id})
            except Exception as e:
                print(f"No se pudo conectar al peer {peer_url}: {e}")

    async def broadcast(self, message_type: str, payload: Dict[str, Any]):
        """Envía un mensaje a todos los peers conectados."""
        message = json.dumps({"type": message_type, "payload": payload, "origin_node": self.node_id})
        print(f"Transmitiendo a {len(self.connected_peers)} peers: {message_type}")
        for peer_url, websocket in self.connected_peers.items():
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                print(f"Conexión perdida con {peer_url}. Eliminando de peers activos.")
                # Lógica para reconexión podría ir aquí
                del self.connected_peers[peer_url]

    async def send_message(self, peer_url: str, message_type: str, payload: Dict[str, Any]):
        """Envía un mensaje a un peer específico."""
        if peer_url in self.connected_peers:
            message = json.dumps({"type": message_type, "payload": payload, "origin_node": self.node_id})
            try:
                await self.connected_peers[peer_url].send(message)
                print(f"Mensaje enviado a {peer_url}: {message_type}")
            except websockets.exceptions.ConnectionClosed:
                print(f"Conexión perdida con {peer_url} al intentar enviar mensaje.")
        else:
            print(f"Intento de enviar mensaje a peer no conectado: {peer_url}")

# Ejemplo de cómo se podría usar (esto iría en un punto de entrada principal)
async def main():
    node = SwarmNode()
    # Se necesitaría una forma de obtener el host/puerto local desde la config
    # Por ahora, hardcodeado para el ejemplo
    host = "0.0.0.0"
    port = 8000 # Puerto base, debería ser configurable
    
    # Iniciar el servidor en segundo plano
    server_task = asyncio.create_task(node.start_server(host, port))
    
    # Dar tiempo al servidor para que inicie
    await asyncio.sleep(1)
    
    # Conectarse a otros peers
    await node.connect_to_peers()
    
    # Mantener el programa corriendo
    await server_task

if __name__ == "__main__":
    # Nota: Este script está pensado para ser importado y gestionado por el cerebro principal de Mea-Core,
    # no para ser ejecutado directamente de esta forma en producción.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Cerrando nodo de enjambre.")

