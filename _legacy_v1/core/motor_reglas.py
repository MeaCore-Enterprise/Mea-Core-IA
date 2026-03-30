# rules_engine.py
"""
Motor de reglas dinámicas para MEA-Core-IA.
Permite definir reglas tipo if-condición-then-acción y aplicarlas a entradas.
"""
from typing import List, Dict

class Rule:
    def __init__(self, condition: str, action: str):
        self.condition = condition.lower()
        self.action = action

    def matches(self, text: str) -> bool:
        return self.condition in text.lower()

class RulesEngine:
    def __init__(self):
        self.rules: List[Rule] = []

    def add_rule(self, condition: str, action: str):
        self.rules.append(Rule(condition, action))

    def remove_rule(self, condition: str):
        self.rules = [r for r in self.rules if r.condition != condition.lower()]

    def apply(self, text: str) -> str:
        for rule in self.rules:
            if rule.matches(text):
                return rule.action
        return "No hay regla que aplique."

    def list_rules(self) -> List[Dict[str, str]]:
        return [{"condition": r.condition, "action": r.action} for r in self.rules]
