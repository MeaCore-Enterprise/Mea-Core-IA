# Guía de Desarrollo de Plugins para Mea-Core

## Introducción

El sistema de plugins de Mea-Core permite extender sus capacidades con nuevas funcionalidades y comandos de forma dinámica. Cualquier persona puede crear un plugin para conectar Mea-Core con APIs externas, herramientas de sistema o cualquier otra fuente de datos.

## Estructura de un Plugin

Un plugin es un simple archivo de Python (`.py`) ubicado en el directorio `/plugins`.

Para que el `PluginManager` lo reconozca, un plugin debe cumplir dos requisitos:

1.  Ser un archivo Python válido.
2.  Contener una variable global llamada `COMMANDS`.

### La Variable `COMMANDS`

`COMMANDS` es un diccionario que mapea el nombre de un comando (que se usará para invocarlo) a una función de Python que lo ejecuta.

- **Clave (key)**: Un `string` con el nombre del comando. Debe ser único y descriptivo. E.g., `"get_weather"`.
- **Valor (value)**: El objeto de la función que se ejecutará. E.g., `get_weather_forecast`.

---

## Ejemplo: Creando un Plugin `hello_world.py`

Vamos a crear un plugin simple que saluda a un usuario.

**1. Crear el archivo:**

Crea un nuevo archivo en `plugins/hello_world.py`.

**2. Escribir el código:**

```python
# plugins/hello_world.py

# --- Funciones del Plugin ---

def say_hello(name: str = "mundo") -> str:
    """Genera un saludo simple."""
    return f"Hola, {name}!"

# --- Registro de Comandos ---
# El PluginManager buscará esta variable.

COMMANDS = {
    "saludar": say_hello,
}
```

**3. ¡Eso es todo!**

La próxima vez que Mea-Core se inicie, el `PluginManager` descubrirá automáticamente `hello_world.py`, cargará el módulo y registrará el comando `"saludar"`. A partir de ese momento, se podrá invocar el comando a través del cerebro de la IA o directamente desde el `PluginManager`.

---

## Buenas Prácticas

- **Manejo de Dependencias**: Si tu plugin requiere librerías externas (como `requests` o `psutil`), asegúrate de documentarlo. En un futuro, el sistema de plugins podría manejar la instalación automática de dependencias.
- **Manejo de Errores**: Envuelve las llamadas a APIs externas o código propenso a fallos en bloques `try...except` para evitar que un plugin defectuoso detenga el sistema.
- **Documentación**: Usa docstrings en tus funciones para explicar qué hacen, qué argumentos reciben y qué devuelven. Esto es útil para la introspección automática.
- **Actualiza el `plugins-index.json`**: Si desarrollas un plugin para la comunidad, añade su descripción al archivo `plugins/plugins-index.json` para que otros puedan descubrirlo.
