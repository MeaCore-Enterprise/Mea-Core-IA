
import json
from typing import Any, Dict, List, Optional, Tuple

# Importa la clase correcta desde el módulo correcto
from core.memory_store import MemoryStore

class GoalManager:
    """Gestiona la creación, seguimiento y estado de metas a largo plazo.

    Utiliza un MemoryStore para persistir las metas como recuerdos especiales
    a largo plazo.
    """
    def __init__(self, memory_store: MemoryStore):
        """Inicializa el gestor de metas.

        Args:
            memory_store (MemoryStore): La instancia de MemoryStore a utilizar.
        """
        self.mem = memory_store

    def add_goal(self, name: str, description: str, tasks: List[str]) -> bool:
        """Añade una nueva meta a la memoria a largo plazo.

        Verifica primero si una meta con el mismo nombre ya existe.

        Args:
            name (str): El nombre único de la meta.
            description (str): Una descripción de la meta.
            tasks (List[str]): Una lista de tareas para completar la meta.

        Returns:
            bool: True si la meta se creó con éxito, False si ya existía.
        """
        if self.get_goal(name):
            print(f"[GoalManager] La meta '{name}' ya existe.")
            return False

        goal_data = {
            "name": name,
            "description": description,
            "status": "active",  # active, completed, failed
            "tasks": {task: "pending" for task in tasks},  # pending, completed
            "progress": 0.0
        }
        
        meta = {'type': 'goal', 'goal_name': name}
        self.mem.add_memory(content=json.dumps(goal_data), meta=meta, long_term=True)
        print(f"[GoalManager] Meta '{name}' añadida.")
        return True

    def get_goal(self, name: str) -> Optional[Tuple[Dict[str, Any], str]]:
        """Recupera los datos y el ID de una meta de la memoria.

        Busca en la memoria a largo plazo un recuerdo marcado como 'goal' con
        el nombre especificado.

        Args:
            name (str): El nombre de la meta a buscar.

        Returns:
            Optional[Tuple[Dict[str, Any], str]]: Una tupla con el diccionario de la meta
                                                 y el ID del recuerdo, o None si no se encuentra.
        """
        for memory_item in self.mem.long_term:
            meta = memory_item.get('meta', {})
            if meta.get('type') == 'goal' and meta.get('goal_name') == name:
                goal_data = json.loads(memory_item['content'])
                memory_id = memory_item['id']
                return goal_data, memory_id
        return None

    def list_goals(self, status: str = "active") -> List[Dict[str, Any]]:
        """Lista todas las metas con un estado específico.

        Args:
            status (str, optional): El estado de las metas a listar ('active',
                                  'completed', 'failed'). Defaults to "active".

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios, donde cada uno es una meta.
        """
        goals = []
        for memory_item in self.mem.long_term:
            meta = memory_item.get('meta', {})
            if meta.get('type') == 'goal':
                goal = json.loads(memory_item['content'])
                if goal.get('status') == status:
                    goals.append(goal)
        return goals

    def complete_task(self, goal_name: str, task_name: str) -> bool:
        """Marca una tarea de una meta como completada y actualiza el progreso.

        Para actualizar, se borra el recuerdo de la meta anterior y se crea uno
        nuevo con el progreso actualizado.

        Args:
            goal_name (str): El nombre de la meta a la que pertenece la tarea.
            task_name (str): El nombre de la tarea a marcar como completada.

        Returns:
            bool: True si la tarea se completó con éxito, False en caso contrario.
        """
        goal_info = self.get_goal(goal_name)
        if not goal_info:
            print(f"[GoalManager] No se encontró la meta '{goal_name}'.")
            return False
        
        goal, memory_id = goal_info
        
        if task_name in goal['tasks'] and goal['tasks'][task_name] == 'pending':
            goal['tasks'][task_name] = 'completed'
            
            completed_tasks = [t for t, s in goal['tasks'].items() if s == 'completed']
            goal['progress'] = (len(completed_tasks) / len(goal['tasks'])) * 100
            
            if all(s == 'completed' for s in goal['tasks'].values()):
                goal['status'] = 'completed'
            
            # Actualizar borrando el registro antiguo y añadiendo el nuevo
            self.mem.delete_memory(memory_id)
            
            meta = {'type': 'goal', 'goal_name': goal_name}
            self.mem.add_memory(content=json.dumps(goal), meta=meta, long_term=True)
            
            print(f"[GoalManager] Tarea '{task_name}' de la meta '{goal_name}' completada. Progreso: {goal['progress']:.0f}%")
            return True
        
        print(f"[GoalManager] La tarea '{task_name}' no existe o ya está completada en la meta '{goal_name}'.")
        return False
