"""
Módulo para la simulación de una red de enjambre virtual.

Este módulo no realiza comunicaciones de red reales, sino que simula el
comportamiento de una red de nodos, incluyendo topología, replicación de datos,
latencia y fallos aleatorios. Es útil para visualizaciones o para probar
la lógica de coordinación del enjambre sin una red real.
"""
import random

class SwarmNode:
    """Representa un nodo virtual en la red de enjambre simulada."""
    def __init__(self, node_id, lan_device, priority=1, bandwidth=None):
        """Inicializa un nodo virtual con atributos simulados."""
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
        """Representación de cadena del nodo."""
        return f"<SwarmNode {self.id} ({self.lan_device}) {self.status}>"

class SwarmNetwork:
    """Gestiona la red virtual de enjambre, incluyendo sus nodos y topología.

    Simula la replicación de datos, la latencia de red, los fallos de nodos
    y la reconexión.
    """
    LAN_DEVICES = ['Servidor','PC','Laptop','Tablet','RaspberryPi','NAS','Router','IoT']

    def __init__(self, node_count=15):
        """Inicializa la red simulada con un número determinado de nodos."""
        self.nodes = []
        self.replication_history = []
        self.alerts = []
        self._create_nodes(node_count)
        self._build_topology()

    def _create_nodes(self, node_count):
        """(Privado) Crea los nodos virtuales de la red."""
        for i in range(node_count):
            dev = random.choice(self.LAN_DEVICES)
            priority = {'Servidor':5,'PC':4,'Laptop':3,'NAS':4,'Router':2}.get(dev,1)
            node = SwarmNode(f"Nodo-{i+1}", dev, priority)
            self.nodes.append(node)

    def _build_topology(self):
        """(Privado) Construye una topología de red simple (hub-and-spoke)."""
        hubs = [n for n in self.nodes if n.priority >= 4]
        if not hubs: # Asegurarse de que haya al menos un hub
            hubs = self.nodes
        for n in self.nodes:
            if n not in hubs:
                hub = random.choice(hubs)
                hub.children.append(n)

    def replicate(self, node1, node2):
        """Simula la replicación de datos entre dos nodos."""
        if node1.status == 'replicando' or node2.status == 'replicando':
            return
        # Simula pérdida de paquetes
        if random.random() < 0.05:
            self.alerts.append(f"Paquete perdido entre {node1.id} y {node2.id}")
            return
        # Simula latencia y saturación
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
        
        # Simula el fin de la replicación
        node1.status = node2.status = 'activo'
        node1.cpu += random.uniform(0,5)
        node2.cpu += random.uniform(0,5)
        node1.memory += random.uniform(0,5)
        node2.memory += random.uniform(0,5)
        node1.network_load = max(0, node1.network_load-0.3)
        node2.network_load = max(0, node2.network_load-0.3)

    def step(self, replication_speed=0.03):
        """Simula un paso de tiempo en la red."""
        # Simula fallos y reconexiones
        for node in self.nodes:
            if random.random() < node.fail_chance:
                node.status = 'offline'
            if node.status == 'offline' and random.random() < 0.02:
                node.status = 'activo'
        
        # Simula replicación
        active_nodes = [n for n in self.nodes if n.status == 'activo' and n.network_load < 1]
        for i, n1 in enumerate(active_nodes):
            for n2 in active_nodes[i+1:]:
                if random.random() < replication_speed:
                    self.replicate(n1, n2)

    def get_status(self):
        """Devuelve un resumen del estado de todos los nodos."""
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
        """Devuelve el historial reciente de replicaciones."""
        return self.replication_history[-limit:][::-1]

    def get_alerts(self, limit=10):
        """Devuelve las alertas recientes de la red."""
        return self.alerts[-limit:][::-1]
