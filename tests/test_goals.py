import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.objetivos import GoalManager
from core.memoria import MemoryStore

class TestGoalManager(unittest.TestCase):

    def setUp(self):
        """Crea una instancia de MemoryStore en memoria y un GoalManager para cada prueba."""
        self.memory = MemoryStore() # Usa :memory: por defecto si no hay settings
        self.goal_manager = GoalManager(self.memory)
        self.memory.clear_all_memory_for_testing()

    def tearDown(self):
        """Cierra la conexión a la base de datos."""
        self.memory.close_db()

    def test_add_and_get_goal(self):
        """Prueba que se puede añadir y recuperar una meta correctamente."""
        result = self.goal_manager.add_goal("Test Goal", "A simple test goal", ["task1", "task2"])
        self.assertTrue(result)

        goal_info = self.goal_manager.get_goal("Test Goal")
        self.assertIsNotNone(goal_info)
        goal, _ = goal_info
        self.assertEqual(goal['name'], "Test Goal")
        self.assertEqual(goal['status'], "active")
        self.assertEqual(len(goal['tasks']), 2)

    def test_add_duplicate_goal(self):
        """Prueba que no se puede añadir una meta con un nombre duplicado."""
        self.goal_manager.add_goal("Duplicate Goal", "First goal", ["taskA"])
        result = self.goal_manager.add_goal("Duplicate Goal", "Second goal", ["taskB"])
        self.assertFalse(result)

    def test_get_nonexistent_goal(self):
        """Prueba que al buscar una meta inexistente devuelve None."""
        goal_info = self.goal_manager.get_goal("Nonexistent Goal")
        self.assertIsNone(goal_info)

    def test_list_goals_by_status(self):
        """Prueba que se pueden listar las metas según su estado."""
        self.goal_manager.add_goal("Active Goal", "...", ["t1"])
        self.goal_manager.add_goal("Completed Goal", "...", ["t2"])
        self.goal_manager.complete_task("Completed Goal", "t2")

        active_goals = self.goal_manager.list_goals(status="active")
        completed_goals = self.goal_manager.list_goals(status="completed")

        self.assertEqual(len(active_goals), 1)
        self.assertEqual(active_goals[0]['name'], "Active Goal")
        self.assertEqual(len(completed_goals), 1)
        self.assertEqual(completed_goals[0]['name'], "Completed Goal")

    def test_complete_task_and_progress(self):
        """Prueba que completar una tarea actualiza el progreso de la meta."""
        self.goal_manager.add_goal("Progress Goal", "...", ["task1", "task2"])
        
        # Completar la primera tarea
        result = self.goal_manager.complete_task("Progress Goal", "task1")
        self.assertTrue(result)

        goal, _ = self.goal_manager.get_goal("Progress Goal")
        self.assertEqual(goal['tasks']['task1'], 'completed')
        self.assertEqual(goal['progress'], 50.0)

        # Completar la segunda tarea
        result2 = self.goal_manager.complete_task("Progress Goal", "task2")
        self.assertTrue(result2)

        goal2, _ = self.goal_manager.get_goal("Progress Goal")
        self.assertEqual(goal2['progress'], 100.0)

    def test_complete_all_tasks_updates_goal_status(self):
        """Prueba que el estado de la meta cambia a 'completed' al finalizar todas las tareas."""
        self.goal_manager.add_goal("Final Goal", "...", ["task_final"])
        self.goal_manager.complete_task("Final Goal", "task_final")
        
        goal, _ = self.goal_manager.get_goal("Final Goal")
        self.assertEqual(goal['status'], "completed")

    def test_complete_nonexistent_task(self):
        """Prueba que intentar completar una tarea que no existe falla."""
        self.goal_manager.add_goal("Task Goal", "...", ["real_task"])
        result = self.goal_manager.complete_task("Task Goal", "fake_task")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()