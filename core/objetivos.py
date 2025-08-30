import json
from typing import Any, Dict, List, Optional, Tuple

# Importa la clase correcta desde el módulo correcto
from core.memoria import MemoryStore

class GoalManager:
    """Gestiona la creación, seguimiento y estado de metas a largo plazo."""

    def __init__(self, memory_store: MemoryStore):
        """Inicializa el gestor de metas."""
        self.mem = memory_store

    def add_goal(self, name: str, description: str, tasks: List[str]) -> bool:
        """Añade una nueva meta a la memoria episódica."""
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
        
        self.mem.log_episode(type='goal', source='goal_manager', data=goal_data)
        print(f"[GoalManager] Meta '{name}' añadida.")
        return True

    def get_goal(self, name: str) -> Optional[Tuple[Dict[str, Any], str]]:
        """Recupera los datos y el ID de una meta de la memoria."""
        for memory_item in self.mem.long_term:
            if memory_item.get('type') == 'goal' and memory_item.get('data', {}).get('name') == name:
                return memory_item['data'], memory_item['id']
        return None

    def list_goals(self, status: str = "active") -> List[Dict[str, Any]]:
        """Lista todas las metas con un estado específico."""
        goals = []
        for memory_item in self.mem.long_term:
            if memory_item.get('type') == 'goal':
                goal_data = memory_item.get('data', {})
                if goal_data.get('status') == status:
                    goals.append(goal_data)
        return goals

    def complete_task(self, goal_name: str, task_name: str) -> bool:
        """Marca una tarea de una meta como completada y actualiza el progreso."""
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
            self.mem.delete_episode(memory_id)
            self.mem.log_episode(type='goal', source='goal_manager', data=goal)
            
            print(f"[GoalManager] Tarea '{task_name}' de la meta '{goal_name}' completada. Progreso: {goal['progress']:.0f}%")
            return True
        
        print(f"[GoalManager] La tarea '{task_name}' no existe o ya está completada en la meta '{goal_name}'.")
        return False