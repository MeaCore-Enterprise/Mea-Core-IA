


from core.personality import load_personality
from core.memory import MemoryStore
from core.ethics import EthicsCore
from core.curiosity import CuriosityModule
from typing import Any, List
import random



def main_loop() -> None:
    persona: dict[str, Any] = load_personality()
    mem: MemoryStore = MemoryStore()
    ethics = EthicsCore()
    curiosity = CuriosityModule()
    context: List[str] = []  # Guarda las últimas 5 interacciones
    saludos = [
        "¡Hola! ¿Cómo estás?",
        "¡Buen día! ¿En qué puedo ayudarte?",
        "¡Saludos! ¿Qué te gustaría saber hoy?"
    ]
    despedidas = [
        "¡Hasta luego!",
        "Adiós, que tengas un gran día.",
        "Nos vemos pronto."
    ]
    plantillas = [
        "Interesante lo que mencionas sobre '{input}'.",
        "Nunca había pensado en '{input}', cuéntame más.",
        "¿Por qué te interesa '{input}'?",
        "Eso suena importante: '{input}'."
    ]
    print(persona.get("greeting", random.choice(saludos)))
    while True:
        try:
            q: str = input("> ").strip()
            if not q:
                continue
            if q.lower() in {"exit", "quit"}:
                print(random.choice(despedidas))
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

            # Aprendizaje: guarda cada mensaje y su respuesta asociada
            respuesta = mem.get(f"aprendido:{q}")
            if respuesta:
                print(f"[{persona.get('name')}] (aprendido) → {respuesta}")
            else:
                # Curiosidad: recompensa por preguntas nuevas
                reward = curiosity.intrinsic_reward(q)
                if reward > 0.5:
                    print(f"[Curiosidad] ¡Gracias por una pregunta interesante!")

                # Motor de respuesta con contexto y variaciones
                # Usa contexto para respuestas más naturales
                contexto = " | ".join(context[-3:]) if context else ""
                if contexto:
                    plantilla = random.choice(plantillas)
                    respuesta_auto = plantilla.format(input=q) + f" (Contexto: {contexto})"
                else:
                    respuesta_auto = random.choice(plantillas).format(input=q)
                print(f"[{persona.get('name')}] → {respuesta_auto}")

                # Pregunta al usuario cómo debería responder la próxima vez
                nueva = input(f"¿Cómo debería responder a '{q}' en el futuro? (deja vacío para no aprender): ").strip()
                if nueva:
                    mem.set(f"aprendido:{q}", nueva)
                    print(f"[Aprendizaje] ¡He aprendido a responder '{q}'!")

            # Actualiza el contexto
            context.append(q)
            if len(context) > 5:
                context.pop(0)
        except KeyboardInterrupt:
            print("\nInterrumpido. Saliendo.")
            break

if __name__ == "__main__":
    main_loop()
