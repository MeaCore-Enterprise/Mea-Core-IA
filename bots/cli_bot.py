

from core.personality import load_personality
from core.memory import MemoryStore
from core.ethics import EthicsCore
from core.curiosity import CuriosityModule
from typing import Any

def main_loop() -> None:
    persona: dict[str, Any] = load_personality()
    mem: MemoryStore = MemoryStore()
    ethics = EthicsCore()
    curiosity = CuriosityModule()
    print(persona.get("greeting", "Hola."))
    while True:
        try:
            q: str = input("> ").strip()
            if not q:
                continue
            if q.lower() in {"exit", "quit"}:
                print("Adiós.")
                break
            # comandos básicos para debug
            if q.startswith("!set "):
                _, key, *rest = q.split()
                val = " ".join(rest)
                mem.set(key, val)
                print(f"[mem] {key} = {val}")
                continue
            if q.startswith("!get "):
                _, key = q.split()
                print(mem.get(key))
                continue

            # Ética: verifica si la acción es permitida
            if not ethics.check_action(q):
                print(f"[Ética] {ethics.explain_decision(q)}")
                continue

            # Curiosidad: recompensa por preguntas nuevas
            reward = curiosity.intrinsic_reward(q)
            if reward > 0.5:
                print(f"[Curiosidad] ¡Gracias por una pregunta interesante!")

            # Respuesta personalizada
            tone: str = str(persona.get("tone", ""))
            print(f"[{persona.get('name')}] ({tone}) → He recibido: {q}")
        except KeyboardInterrupt:
            print("\nInterrumpido. Saliendo.")
            break

if __name__ == "__main__":
    main_loop()
