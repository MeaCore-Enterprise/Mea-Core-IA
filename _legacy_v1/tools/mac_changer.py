"""
Herramienta para cambiar la dirección MAC de una interfaz de red.

Este script utiliza comandos del sistema (`ifconfig`) para modificar la dirección MAC
de una interfaz de red especificada. Requiere permisos de administrador para ejecutarse.

Uso:
    python tools/mac_changer.py --interface <interfaz> --mac <nueva_mac>
"""

import subprocess
import argparse
import re

def change_mac(interface: str, new_mac: str):
    """
    Cambia la dirección MAC de la interfaz especificada.

    Args:
        interface (str): El nombre de la interfaz de red (ej. eth0, wlan0).
        new_mac (str): La nueva dirección MAC a asignar.

    Returns:
        bool: True si el cambio fue exitoso, False en caso contrario.
    """
    print(f"[*] Cambiando la dirección MAC de {interface} a {new_mac}")
    try:
        # Desactivar la interfaz
        subprocess.call(["ifconfig", interface, "down"])
        # Cambiar la MAC
        subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
        # Activar la interfaz
        subprocess.call(["ifconfig", interface, "up"])
        return True
    except Exception as e:
        print(f"[!] Error al cambiar la dirección MAC: {e}")
        return False

def get_current_mac(interface: str) -> str | None:
    """
    Obtiene la dirección MAC actual de una interfaz.

    Args:
        interface (str): La interfaz de la cual leer la MAC.

    Returns:
        str | None: La dirección MAC actual o None si no se pudo leer.
    """
    try:
        ifconfig_result = subprocess.check_output(["ifconfig", interface])
        mac_address_search_result = re.search(r"(\w\w:){5}\w\w", ifconfig_result.decode("utf-8"))
        if mac_address_search_result:
            return mac_address_search_result.group(0)
        else:
            print("[!] No se pudo leer la dirección MAC.")
            return None
    except subprocess.CalledProcessError:
        print(f"[!] Error: No se pudo encontrar la interfaz '{interface}'.")
        return None
    except Exception as e:
        print(f"[!] Error inesperado al obtener la MAC: {e}")
        return None

def main():
    """Función principal para parsear argumentos y ejecutar el cambio de MAC."""
    parser = argparse.ArgumentParser(description="Cambia la dirección MAC de una interfaz de red.")
    parser.add_argument("-i", "--interface", dest="interface", help="Interfaz de red a modificar (ej. eth0)")
    parser.add_argument("-m", "--mac", dest="new_mac", help="Nueva dirección MAC (ej. 00:11:22:33:44:55)")
    args = parser.parse_args()

    if not args.interface or not args.new_mac:
        parser.print_help()
        return

    current_mac = get_current_mac(args.interface)
    if current_mac:
        print(f"[*] MAC actual de {args.interface}: {current_mac}")

    if change_mac(args.interface, args.new_mac):
        new_mac_read = get_current_mac(args.interface)
        if new_mac_read == args.new_mac.lower():
            print(f"[+] La dirección MAC fue cambiada exitosamente a {new_mac_read}")
        else:
            print(f"[!] No se pudo confirmar el cambio de MAC. MAC actual: {new_mac_read}")

if __name__ == "__main__":
    main()
