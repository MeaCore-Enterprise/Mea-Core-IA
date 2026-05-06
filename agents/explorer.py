class ExplorerAgent:
    """
    Explorer Agent - Fase de exploración y generación de hipótesis.
    En el sistema swarm, los Explorers expanden el espacio de búsqueda
    proponiendo nuevas direcciones y sub-objetivos.
    """
    def __init__(self, agent_id: str, llm_client=None):
        self.agent_id = agent_id
        self.role = "explorer"
        self.llm_client = llm_client
        self.profile = {
            "ability": 0.5,
            "workload": 0.0,
            "context": "",
            "successful_tasks": 0,
            "failed_tasks": 0
        }

    async def explore(self, task: str, context: dict = None) -> dict:
        """Exploración: analizar el task y generar hipótesis/sub-goals."""
        prompt = self._build_explore_prompt(task, context)
        
        if self.llm_client:
            response = await self.llm_client.generate(prompt)
            hypotheses = self._parse_hypotheses(response)
        else:
            hypotheses = self._mock_explore(task)
        
        self.profile["workload"] += 1
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "hypotheses": hypotheses,
            "task": task
        }

    def _build_explore_prompt(self, task: str, context: dict = None) -> str:
        return f"""<|system|>
Eres un Explorer Agent en un sistema de swarm intelligence.
Tu rol es explorar el espacio de soluciones para un task dado, generando múltiples hipótesis o sub-objetivos.
Analiza el problema desde diferentes ángulos y propón direcciones de solución.
</s>
<|user|
Task: {task}
Contexto: {context or "Sin contexto adicional"}
</s>
<|assistant|
"""

    def _parse_hypotheses(self, response: str) -> list:
        lines = [l.strip() for l in response.split("\n") if l.strip()]
        return [{"id": i, "hypothesis": h} for i, h in enumerate(lines[:5])]

    def _mock_explore(self, task: str) -> list:
        return [
            {"id": 0, "hypothesis": f"Approach 1: {task}"},
            {"id": 1, "hypothesis": f"Approach 2: Refine {task}"},
            {"id": 2, "hypothesis": f"Approach 3: Expand {task}"}
        ]

    def update_profile(self, success: bool):
        if success:
            self.profile["successful_tasks"] += 1
            self.profile["ability"] = min(1.0, self.profile["ability"] + 0.01)
        else:
            self.profile["failed_tasks"] += 1
            self.profile["ability"] = max(0.1, self.profile["ability"] - 0.01)
        self.profile["workload"] = max(0.0, self.profile["workload"] - 0.1)

    def get_embedding(self) -> list:
        return [self.profile["ability"], self.profile["workload"]]