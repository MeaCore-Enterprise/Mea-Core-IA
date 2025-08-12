
import json
from typing import Any, Dict, List, Optional

from core.memory import MemoryStore

GOAL_KEY_PREFIX = "goal_"

class GoalManager:
    """Gestiona la creación, seguimiento y estado de metas a largo plazo."""
    def __init__(self, memory_store: MemoryStore):
        self.mem = memory_store

    def add_goal(self, name: str, description: str, tasks: List[str]) -> bool:
        """Añade una nueva meta a la memoria."""
        if self.mem.get(f"{GOAL_KEY_PREFIX}{name}"):
            print(f"[GoalManager] La meta '{name}' ya existe.")
            return False
        
        goal_data = {
            "name": name,
            "description": description,
            "status": "active", # active, completed, failed
            "tasks": {task: "pending" for task in tasks}, # pending, completed
            "progress": 0
        }
        self.mem.set(f"{GOAL_KEY_PREFIX}{name}", json.dumps(goal_data))
        return True

    def get_goal(self, name: str) -> Optional[Dict[str, Any]]:
        """Recupera los datos de una meta."""
        goal_json = self.mem.get(f"{GOAL_KEY_PREFIX}{name}")
        return json.loads(goal_json) if goal_json else None

    def list_goals(self, status: str = "active") -> List[Dict[str, Any]]:
        """Lista todas las metas con un estado específico."""
        all_data = self.mem.dump_all()
        goals = []
        for key, value in all_data.items():
            if key.startswith(GOAL_KEY_PREFIX):
                goal = json.loads(value)
                if goal['status'] == status:
                    goals.append(goal)
        return goals

    def complete_task(self, goal_name: str, task_name: str) -> bool:
        """Marca una tarea de una meta como completada y actualiza el progreso."""
        goal = self.get_goal(goal_name)
        if not goal:
            return False
        
        if task_name in goal['tasks'] and goal['tasks'][task_name] == 'pending':
            goal['tasks'][task_name] = 'completed'
            
            completed_tasks = [t for t, s in goal['tasks'].items() if s == 'completed']
            goal['progress'] = len(completed_tasks) / len(goal['tasks']) * 100
            
            if all(s == 'completed' for s in goal['tasks'].values()):
                goal['status'] = 'completed'
            
            self.mem.set(f"{GOAL_KEY_PREFIX}{goal_name}", json.dumps(goal))
            return True
        return False
