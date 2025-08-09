
from core.personality import load_personality
from core.memory import MemoryStore
from typing import Any

def main_loop() -> None:
    persona: dict[str, Any] = load_personality()
    mem: MemoryStore = MemoryStore()
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
            # respuesta simple: eco + personalidad
            tone: str = str(persona.get("tone", ""))
            print(f"[{persona.get('name')}] ({tone}) → He recibido: {q}")
        except KeyboardInterrupt:
            print("\nInterrumpido. Saliendo.")
            break

if __name__ == "__main__":
    main_loop()
