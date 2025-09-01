import unittest
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.objetivos import GoalManager
from core.memoria import MemoryStore
from core import models

class TestGoalManager(unittest.TestCase):

    def setUp(self):
        """Crea una instancia de MemoryStore en memoria y un GoalManager para cada prueba."""
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db_session = Session()
        self.memory = MemoryStore()
        self.goal_manager = GoalManager(self.memory)

    def tearDown(self):
        """Cierra la conexión a la base de datos."""
        self.db_session.close()

    def test_add_and_get_goal(self):
        """Prueba que se puede añadir y recuperar una meta correctamente."""
        result = self.goal_manager.add_goal(self.db_session, "Test Goal", "A simple test goal", ["task1", "task2"])
        self.assertTrue(result)

        goal_info = self.goal_manager.get_goal(self.db_session, "Test Goal")
        self.assertIsNotNone(goal_info)
        goal, _ = goal_info
        self.assertEqual(goal['name'], "Test Goal")
        self.assertEqual(goal['status'], "active")
        self.assertEqual(len(goal['tasks']), 2)

    def test_add_duplicate_goal(self):
        """Prueba que no se puede añadir una meta con un nombre duplicado."""
        self.goal_manager.add_goal(self.db_session, "Duplicate Goal", "First goal", ["taskA"])
        result = self.goal_manager.add_goal(self.db_session, "Duplicate Goal", "Second goal", ["taskB"])
        self.assertFalse(result)

    def test_get_nonexistent_goal(self):
        """Prueba que al buscar una meta inexistente devuelve None."""
        goal_info = self.goal_manager.get_goal(self.db_session, "Nonexistent Goal")
        self.assertIsNone(goal_info)

    def test_list_goals_by_status(self):
        """Prueba que se pueden listar las metas según su estado."""
        self.goal_manager.add_goal(self.db_session, "Active Goal", "...", ["t1"])
        self.goal_manager.add_goal(self.db_session, "Completed Goal", "...", ["t2"])
        self.goal_manager.complete_task(self.db_session, "Completed Goal", "t2")

        active_goals = self.goal_manager.list_goals(self.db_session, status="active")
        completed_goals = self.goal_manager.list_goals(self.db_session, status="completed")

        self.assertEqual(len(active_goals), 1)
        self.assertEqual(active_goals[0]['name'], "Active Goal")
        self.assertEqual(len(completed_goals), 1)
        self.assertEqual(completed_goals[0]['name'], "Completed Goal")

    def test_complete_task_and_progress(self):
        """Prueba que completar una tarea actualiza el progreso de la meta."""
        self.goal_manager.add_goal(self.db_session, "Progress Goal", "...", ["task1", "task2"])
        
        # Completar la primera tarea
        result = self.goal_manager.complete_task(self.db_session, "Progress Goal", "task1")
        self.assertTrue(result)

        goal, _ = self.goal_manager.get_goal(self.db_session, "Progress Goal")
        self.assertEqual(goal['tasks']['task1'], 'completed')
        self.assertEqual(goal['progress'], 50.0)

        # Completar la segunda tarea
        result2 = self.goal_manager.complete_task(self.db_session, "Progress Goal", "task2")
        self.assertTrue(result2)

        goal2, _ = self.goal_manager.get_goal(self.db_session, "Progress Goal")
        self.assertEqual(goal2['progress'], 100.0)

    def test_complete_all_tasks_updates_goal_status(self):
        """Prueba que el estado de la meta cambia a 'completed' al finalizar todas las tareas."""
        self.goal_manager.add_goal(self.db_session, "Final Goal", "...", ["task_final"])
        self.goal_manager.complete_task(self.db_session, "Final Goal", "task_final")
        
        goal, _ = self.goal_manager.get_goal(self.db_session, "Final Goal")
        self.assertEqual(goal['status'], "completed")

    def test_complete_nonexistent_task(self):
        """Prueba que intentar completar una tarea que no existe falla."""
        self.goal_manager.add_goal(self.db_session, "Task Goal", "...", ["real_task"])
        result = self.goal_manager.complete_task(self.db_session, "Task Goal", "fake_task")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
