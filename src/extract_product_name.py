# src/extract_product_name.py
import re

def extract_product_name(reply: str) -> str:
    """
    Extrae el nombre del primer producto Castrol listado en una tabla.
    Soporta respuestas en formato markdown o texto plano.
    """
    # Buscar línea que empiece con "Producto Castrol" o similar
    lines = reply.splitlines()
    for line in lines:
        # Formato: Producto Castrol | Tipo | Viscosidad | Justificación
        if re.search(r"(?i)castrol", line):
            parts = [part.strip() for part in re.split(r"\||:", line)]
            for part in parts:
                if "castrol" in part.lower():
                    return part
    return "el producto recomendado"