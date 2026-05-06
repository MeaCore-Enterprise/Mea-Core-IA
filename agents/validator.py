class ValidatorAgent:
    """
    Validator Agent - Fase de verificación y consolidación.
    En el sistema swarm, los Validators evalúan las soluciones propuestas
    por los Workers y aseguran consistencia.
    """
    def __init__(self, agent_id: str, llm_client=None):
        self.agent_id = agent_id
        self.role = "validator"
        self.llm_client = llm_client
        self.profile = {
            "ability": 0.5,
            "workload": 0.0,
            "context": "",
            "successful_tasks": 0,
            "failed_tasks": 0
        }

    async def validate(self, task: str, executions: list, context: dict = None) -> dict:
        """
        Validación: evaluar las soluciones de los Workers y consolidar el resultado.
        """
        prompt = self._build_validate_prompt(task, executions, context)
        
        if self.llm_client:
            response = await self.llm_client.generate(prompt)
            evaluation = self._parse_evaluation(response)
        else:
            evaluation = self._mock_validate(task, executions)
        
        self.profile["workload"] += 1
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "evaluation": evaluation,
            "executions": executions,
            "task": task
        }

    def _build_validate_prompt(self, task: str, executions: list, context: dict = None) -> str:
        executions_str = "\n".join([
            f"- {e.get('agent_id', 'unknown')}: {e.get('execution', {}).get('output', '')}"
            for e in executions
        ])
        return f"""<|system|>
Eres un Validator Agent en un sistema de swarm intelligence.
Tu rol es evaluar las soluciones propuestas por Workers y consolidar el resultado final.
Selecciona la mejor opción o combina elementos de múltiples soluciones.
</s>
<|user|
Task: {task}
Ejecuciones:\n{executions_str}
Contexto: {context or "Sin contexto adicional"}
</s>
<|assistant|
"""

    def _parse_evaluation(self, response: str) -> dict:
        return {
            "approved": True,
            "consolidated_output": response.strip(),
            "confidence": 0.8,
            "reasoning": "Consolidado por Validator"
        }

    def _mock_validate(self, task: str, executions: list) -> dict:
        best = max(executions, key=lambda e: e.get("execution", {}).get("confidence", 0))
        return {
            "approved": True,
            "consolidated_output": best.get("execution", {}).get("output", ""),
            "confidence": 0.6,
            "reasoning": "Mejor opción seleccionada"
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