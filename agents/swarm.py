import asyncio
import uuid
from typing import List, Optional

from .explorer import ExplorerAgent
from .worker import WorkerAgent
from .validator import ValidatorAgent


class SwarmOrchestrator:
    """
    Coordina múltiples agentes en un swarm auto-organizado.
    Implementa el patrón Explorer/Worker/Validator con pheromone-like profiles.
    """
    def __init__(self, llm_client=None, node=None):
        self.llm_client = llm_client
        self.node = node
        self.explorers: List[ExplorerAgent] = []
        self.workers: List[WorkerAgent] = []
        self.validators: List[ValidatorAgent] = []
        self.task_history: List[dict] = []
        
    def create_agents(self, n_explorers: int = 3, n_workers: int = 5, n_validators: int = 2):
        """Crea el pool de agentes del swarm."""
        self.explorers = [
            ExplorerAgent(f"explorer-{i}", self.llm_client)
            for i in range(n_explorers)
        ]
        self.workers = [
            WorkerAgent(f"worker-{i}", self.llm_client)
            for i in range(n_workers)
        ]
        self.validators = [
            ValidatorAgent(f"validator-{i}", self.llm_client)
            for i in range(n_validators)
        ]
        
    async def execute_task(self, task: str, context: dict = None) -> dict:
        """
        Ejecuta una tarea a través del swarm:
        1. Explorer genera hipótesis
        2. Workers ejecutan en paralelo
        3. Validator consolida resultado
        """
        task_id = str(uuid.uuid4())[:8]
        
        # Fase 1: Explorers generan hipótesis
        explorer_tasks = [
            explorer.explore(task, context)
            for explorer in self.explorers
        ]
        explorer_results = await asyncio.gather(*explorer_tasks)
        
        # Recolectar mejores hipótesis
        all_hypotheses = []
        for result in explorer_results:
            all_hypotheses.extend(result.get("hypotheses", []))
        
        # Fase 2: Workers ejecutan hipótesis
        worker_tasks = [
            worker.execute(task, hypothesis, context)
            for worker, hypothesis in zip(
                self.workers[:len(all_hypotheses)],
                all_hypotheses[:len(self.workers)]
            )
        ]
        worker_results = await asyncio.gather(*worker_tasks)
        
        # Fase 3: Validator consolida
        validator = self.validators[0]
        final_result = await validator.validate(task, worker_results, context)
        
        # Actualizar profiles con pheromone-like reinforcement
        self._update_profiles(worker_results, final_result)
        
        # Guardar en historial
        self.task_history.append({
            "task_id": task_id,
            "task": task,
            "result": final_result
        })
        
        return {
            "task_id": task_id,
            "status": "completed",
            "result": final_result.get("evaluation", {}).get("consolidated_output"),
            "confidence": final_result.get("evaluation", {}).get("confidence", 0),
            "agents_used": {
                "explorers": len(self.explorers),
                "workers": len(worker_results),
                "validators": len(self.validators)
            }
        }
    
    def _update_profiles(self, worker_results: list, final_result: dict):
        """Actualiza profiles de agentes basado en resultados (pheromone reinforcement)."""
        for worker_result in worker_results:
            agent_id = worker_result.get("agent_id")
            success = worker_result.get("execution", {}).get("success", False)
            
            for worker in self.workers:
                if worker.agent_id == agent_id:
                    worker.update_profile(success)
                    
    def get_swarm_stats(self) -> dict:
        """Retorna estadísticas del swarm."""
        return {
            "total_agents": len(self.explorers) + len(self.workers) + len(self.validators),
            "explorers": len(self.explorers),
            "workers": len(self.workers),
            "validators": len(self.validators),
            "tasks_completed": len(self.task_history),
            "explorer_profiles": [e.profile for e in self.explorers[:2]],
            "worker_profiles": [w.profile for w in self.workers[:2]],
            "validator_profiles": [v.profile for v in self.validators[:1]]
        }
    
    def get_best_worker(self) -> WorkerAgent:
        """Retorna el worker con mejor profile."""
        if not self.workers:
            return None
        return max(self.workers, key=lambda w: w.profile["ability"])
    
    def get_best_explorer(self) -> ExplorerAgent:
        """Retorna el explorer con mejor profile."""
        if not self.explorers:
            return None
        return max(self.explorers, key=lambda e: e.profile["ability"])