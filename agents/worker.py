class WorkerAgent:
    """
    Worker Agent - Fase de ejecución y refinamiento.
    En el sistema swarm, los Workers intentan ejecutar sub-tareas
    y generar soluciones parciales.
    """
    def __init__(self, agent_id: str, llm_client=None):
        self.agent_id = agent_id
        self.role = "worker"
        self.llm_client = llm_client
        self.profile = {
            "ability": 0.5,
            "workload": 0.0,
            "context": "",
            "successful_tasks": 0,
            "failed_tasks": 0
        }

    async def execute(self, task: str, hypothesis: dict, context: dict = None) -> dict:
        """
        Ejecución: intentar resolver el task basándose en una hipótesis.
        """
        prompt = self._build_execute_prompt(task, hypothesis, context)
        
        if self.llm_client:
            result = await self.llm_client.generate(prompt)
            execution = self._parse_result(result)
        else:
            execution = self._mock_execute(task, hypothesis)
        
        self.profile["workload"] += 1
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "execution": execution,
            "hypothesis": hypothesis,
            "task": task
        }

    def _build_execute_prompt(self, task: str, hypothesis: dict, context: dict = None) -> str:
        return f"""<|system|>
Eres un Worker Agent en un sistema de swarm intelligence.
Tu rol es ejecutar tareas específicas basadas en hipótesis generadas por Explorer agents.
Intenta resolver el problema y proporciona una solución parcial o completa.
</s>
<|user|
Task: {task}
Hipótesis: {hypothesis.get('hypothesis', '')}
Contexto: {context or "Sin contexto adicional"}
</s>
<|assistant|
"""

    def _parse_result(self, response: str) -> dict:
        return {
            "success": True,
            "output": response.strip(),
            "confidence": 0.7
        }

    def _mock_execute(self, task: str, hypothesis: dict) -> dict:
        return {
            "success": True,
            "output": f"Ejecutado: {task} -> {hypothesis.get('hypothesis', '')}",
            "confidence": 0.5
        }

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