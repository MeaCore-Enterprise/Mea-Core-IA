
import json
from typing import Dict, Any

DEFAULT: Dict[str, Any] = {
    "name": "Mea",
    "tone": "calm, professional, slightly humorous",
    "values": {
        "safety": True,
        "honesty": True,
        "user_alignment": True
    },
    "greeting": "Hola, soy Mea-Core. ¿En qué te ayudo hoy?"
}

PATH: str = "data/personality.json"

def load_personality(path: str = PATH) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            p: Dict[str, Any] = json.load(f)
        return p
    except Exception:
        # crea un default si no existe
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT, f, indent=2, ensure_ascii=False)
        return DEFAULT

def save_personality(cfg: Dict[str, Any], path: str = PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
