from typing import Dict, List, Optional


class EvolutionEvaluator:
    """
    Evalúa el progreso del sistema y determina si hay mejora.
    Implementa métricas de auto-evolución.
    """
    def __init__(self):
        self.metrics_history: List[Dict] = []
        self.baseline: Optional[Dict] = None
        
    def set_baseline(self, metrics: Dict):
        """Fija el baseline inicial."""
        self.baseline = metrics
        self.metrics_history.append({
            "type": "baseline",
            "metrics": metrics
        })
        
    def evaluate(self, current_metrics: Dict, goals: List[str]) -> Dict:
        """
        Evalúa el progreso contra el baseline y goals.
        """
        if not self.baseline:
            self.set_baseline(current_metrics)
            return {
                "status": "baseline_set",
                "improvement": 0.0,
                "goals_met": []
            }
        
        improvements = {}
        goals_met = []
        
        for key in current_metrics:
            if key in self.baseline:
                baseline_val = self.baseline[key]
                current_val = current_metrics[key]
                
                if baseline_val > 0:
                    improvement = (current_val - baseline_val) / baseline_val
                    improvements[key] = improvement
                    
                    if improvement > 0:
                        goals_met.append(key)
        
        avg_improvement = sum(improvements.values()) / len(improvements) if improvements else 0
        
        self.metrics_history.append({
            "type": "evaluation",
            "metrics": current_metrics,
            "improvement": avg_improvement,
            "goals_met": goals_met
        })
        
        return {
            "status": "evaluated",
            "improvement": avg_improvement,
            "improvements": improvements,
            "goals_met": goals_met,
            "goals_progress": f"{len(goals_met)}/{len(goals)}"
        }
    
    def get_history(self) -> List[Dict]:
        """Retorna historial de evaluaciones."""
        return self.metrics_history