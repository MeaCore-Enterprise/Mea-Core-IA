"""
Módulo para la comunicación en red de un enjambre de nodos MEA-Core.

Implementa una red real donde las instancias de la IA pueden descubrirse
en una red local (LAN) a través de broadcasts UDP y sincronizar archivos
(como bases de conocimiento) a través de TCP.
"""
import socket
import threading
import time

class SwarmNetworkNode:
    """Nodo de enjambre: anuncia su presencia y sincroniza conocimiento con otros.

    Este nodo realiza las siguientes acciones en hilos separados:
    - Emite un broadcast UDP para anunciar su presencia en la LAN.
    - Escucha broadcasts de otros nodos para descubrirlos.
    - Mantiene una lista de vecinos y la purga si no se reciben anuncios.
    - Escucha peticiones de sincronización TCP para compartir su archivo de conocimiento.
    """
    BROADCAST_PORT = 50505
    SYNC_PORT = 50506
    BROADCAST_INTERVAL = 5  # segundos
    TIMEOUT = 15  # segundos para considerar un nodo inactivo

    def __init__(self, node_id: str, knowledge_path: str):
        """Inicializa el nodo de red del enjambre.

        Args:
            node_id (str): Un identificador único para este nodo.
            knowledge_path (str): La ruta al archivo que se va a sincronizar (ej. 'config/responses.json').
        """
        self.node_id = node_id
        self.knowledge_path = knowledge_path
        self.neighbors = {}  # node_id: (ip, last_seen)
        self.running = False
        self._lock = threading.Lock()

    def start(self):
        """Inicia todos los hilos de fondo para la comunicación en red."""
        self.running = True
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        threading.Thread(target=self._listen_broadcasts, daemon=True).start()
        threading.Thread(target=self._listen_sync_requests, daemon=True).start()
        threading.Thread(target=self._prune_neighbors, daemon=True).start()

    def stop(self):
        """Detiene la ejecución de todos los hilos de fondo."""
        self.running = False

    def _broadcast_presence(self):
        """(Privado) Emite un mensaje de broadcast para anunciar la presencia del nodo."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = f"MEA-CORE-NODE:{self.node_id}"
        while self.running:
            s.sendto(msg.encode(), ("<broadcast>", self.BROADCAST_PORT))
            time.sleep(self.BROADCAST_INTERVAL)

    def _listen_broadcasts(self):
        """(Privado) Escucha broadcasts de otros nodos para actualizar la lista de vecinos."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", self.BROADCAST_PORT))
        while self.running:
            try:
                data, addr = s.recvfrom(1024)
                msg = data.decode()
                if msg.startswith("MEA-CORE-NODE:"):
                    node_id = msg.split(":",1)[1]
                    if node_id != self.node_id:
                        with self._lock:
                            self.neighbors[node_id] = (addr[0], time.time())
            except Exception:
                continue

    def _listen_sync_requests(self):
        """(Privado) Escucha conexiones TCP para atender peticiones de sincronización."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", self.SYNC_PORT))
        s.listen(5)
        while self.running:
            try:
                conn, addr = s.accept()
                threading.Thread(target=self._handle_sync, args=(conn,), daemon=True).start()
            except Exception:
                continue

    def _handle_sync(self, conn):
        """(Privado) Maneja una petición de sincronización enviando el archivo de conocimiento."""
        try:
            with open(self.knowledge_path, "rb") as f:
                data = f.read()
            conn.sendall(data)
        except Exception:
            pass
        finally:
            conn.close()

    def _prune_neighbors(self):
        """(Privado) Elimina periódicamente a los vecinos que no han anunciado su presencia recientemente."""
        while self.running:
            now = time.time()
            with self._lock:
                to_remove = [nid for nid,(_,last) in self.neighbors.items() if now-last > self.TIMEOUT]
                for nid in to_remove:
                    del self.neighbors[nid]
            time.sleep(5)

    def sync_with_neighbors(self):
        """Solicita el archivo de conocimiento a todos los vecinos y lo actualiza si es diferente."""
        for node_id, (ip, _) in list(self.neighbors.items()):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((ip, self.SYNC_PORT))
                data = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                s.close()
                # Guardar si es diferente (se podría mejorar con timestamps/versiones)
                with open(self.knowledge_path, "rb") as f:
                    local = f.read()
                if data and data != local:
                    with open(self.knowledge_path, "wb") as f:
                        f.write(data)
                    print(f"[SwarmNetwork] Sincronizado conocimiento desde {node_id} ({ip})")
            except Exception:
                continue
