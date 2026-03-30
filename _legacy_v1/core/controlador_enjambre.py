# SwarmController: Sincronización y replicación avanzada entre instancias
import threading
import time
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

class SwarmController:
    def __init__(self, node_id: str, db_path: str = 'data/swarm_sync.db', json_path: str = 'data/swarm_sync.json', replication_enabled: bool = True):
        self.node_id = node_id
        self.db_path = db_path
        self.json_path = json_path
        self.lock = threading.Lock()
        self.version = 0
        self.last_sync = time.time()
        self.replication_enabled = replication_enabled
        self._init_db()

    def enable_replication(self):
        self.replication_enabled = True

    def disable_replication(self):
        self.replication_enabled = False

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS sync_data (
                key TEXT PRIMARY KEY,
                value TEXT,
                version INTEGER,
                updated_at REAL
            )''')
            conn.commit()

    def sync_memory(self, key: str, value: Any, version: Optional[int] = None):
        """Sincroniza un fragmento de memoria con versionado y manejo de conflictos."""
        with self.lock, sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT version FROM sync_data WHERE key=?', (key,))
            row = c.fetchone()
            current_version = row[0] if row else 0
            new_version = version if version is not None else current_version + 1
            if version is not None and version <= current_version:
                # Conflicto: mantener el valor con mayor version
                return False
            c.execute('REPLACE INTO sync_data (key, value, version, updated_at) VALUES (?, ?, ?, ?)',
                      (key, json.dumps(value), new_version, time.time()))
            conn.commit()
            self.version = max(self.version, new_version)
            return True

    def get_memory(self, key: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT value, version FROM sync_data WHERE key=?', (key,))
            row = c.fetchone()
            if row:
                return {'value': json.loads(row[0]), 'version': row[1]}
            return None

    def export_json(self):
        """Exporta toda la memoria sincronizada a un archivo JSON versionado."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT key, value, version FROM sync_data')
            data = [{'key': k, 'value': json.loads(v), 'version': ver} for k, v, ver in c.fetchall()]
        with open(self.json_path, 'w') as f:
            json.dump({'version': self.version, 'data': data}, f, indent=2)

    def import_json(self):
        """Importa memoria desde un archivo JSON, resolviendo conflictos por version."""
        if not Path(self.json_path).exists():
            return
        with open(self.json_path) as f:
            data = json.load(f)
        for item in data.get('data', []):
            self.sync_memory(item['key'], item['value'], item['version'])

    def periodic_sync(self, interval: int = 10):
        """Ejecuta sincronización periódica (puede usarse en un hilo)."""
        def sync_loop():
            while True:
                self.export_json()
                self.import_json()
                time.sleep(interval)
        t = threading.Thread(target=sync_loop, daemon=True)
        t.start()
