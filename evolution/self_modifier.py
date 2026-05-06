"""
MEA-Core V3 Auto-Evolution Module
Permite que el sistema modifique su propio harness (como SICA).
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional


class SelfModifier:
    """
    Permite que el agente modifique su propio código y configuración.
    Implementa el patrón SICA (Self-Improving Coding Agent).
    """
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.history: List[Dict] = []
        self.improvements_archive = self.base_path / "evolution" / "archive"
        self.improvements_archive.mkdir(parents=True, exist_ok=True)
        
    async def analyze_and_modify(
        self,
        task_result: dict,
        goals: List[str],
        llm_client=None
    ) -> dict:
        """
        Analiza resultados y propone modificaciones al harness.
        """
        analysis = await self._analyze_results(task_result, goals, llm_client)
        
        if analysis.get("should_modify"):
            modifications = await self._generate_modifications(
                analysis, llm_client
            )
            await self._apply_modifications(modifications)
            
        return {
            "analysis": analysis,
            "modifications_applied": len(modifications) if analysis.get("should_modify") else 0
        }
    
    async def _analyze_results(
        self,
        task_result: dict,
        goals: List[str],
        llm_client=None
    ) -> dict:
        """Analiza si el harness necesita modificaciones."""
        if not llm_client:
            return {"should_modify": False, "reason": "No LLM available"}
        
        prompt = f"""<|system|>
Eres el sistema de análisis de MEA-Core.
Analiza los resultados de una tarea y determina si el harness necesita modificación.
</s>
<|user|
Resultados de tarea:
{task_result}

Goals:
{goals}

Evalúa:
1. ¿El resultado cumple los goals?
2. ¿Hay patrones de errores reconocibles?
3. ¿El harness necesita mejoras?
</s>
<|assistant|
"""
        response = await llm_client.generate(prompt)
        
        return {
            "should_modify": "sí" in response.lower() or "yes" in response.lower(),
            "analysis": response,
            "goals": goals
        }
    
    async def _generate_modifications(
        self,
        analysis: dict,
        llm_client=None
    ) -> List[dict]:
        """Genera propuestas de modificación."""
        if not llm_client:
            return []
        
        prompt = f"""<|system|>
Basándote en el análisis,.propón modificaciones específicas al código del harness.
Devuelve JSON con: file_path, modification_type, description
</s>
<|user|
Análisis: {analysis.get('analysis', '')}
</s>
<|assistant|
"""
        response = await llm_client.generate(prompt)
        
        try:
            mods = json.loads(response)
            return mods if isinstance(mods, list) else [mods]
        except:
            return [{"description": response, "file_path": "agents/swarm.py"}]
    
    async def _apply_modifications(self, modifications: List[dict]):
        """Aplica las modificaciones (en modo simulado por seguridad)."""
        for mod in modifications:
            self.history.append({
                "modification": mod,
                "applied": True
            })
            
    def get_history(self) -> List[Dict]:
        """Retorna historial de modificaciones."""
        return self.history