# src/extract_product_name.py
import re

def extract_product_name(reply: str) -> str:
    """
    Extrae el nombre del primer producto Castrol listado en una tabla.
    Soporta respuestas en formato markdown o texto plano.
    """
    # Buscar el nombre del producto Castrol en respuestas coloquiales y tabulares
    # 1. Buscar en formato tabular
    lines = reply.splitlines()
    for line in lines:
        if re.search(r"(?i)castrol", line):
            parts = [part.strip() for part in re.split(r"\||:", line)]
            for part in parts:
                if "castrol" in part.lower():
                    # Solo devolver el nombre del producto, no la frase completa
                    match = re.search(r"Castrol[ A-Za-z0-9\-]+", part)
                    if match:
                        return match.group(0).strip()
                    return part

    # 2. Buscar en frases coloquiales
    # Ejemplo: "te recomendaría el Castrol EDGE 5W-30 LL."
    match = re.search(r"te recomendar[íi]a (el|la)? ([A-Za-z0-9 \-]+Castrol[ A-Za-z0-9\-]*)", reply, re.IGNORECASE)
    if match:
        producto = match.group(2).strip()
        match_prod = re.search(r"Castrol[ A-Za-z0-9\-]+", producto)
        if match_prod:
            return match_prod.group(0).strip()
        return producto

    # Ejemplo: "te recomiendo el Castrol EDGE Turbo Diesel"
    match = re.search(r"te recomiendo (el|la)? ([A-Za-z0-9 \-]+Castrol[ A-Za-z0-9\-]*)", reply, re.IGNORECASE)
    if match:
        producto = match.group(2).strip()
        match_prod = re.search(r"Castrol[ A-Za-z0-9\-]+", producto)
        if match_prod:
            return match_prod.group(0).strip()
        return producto

    # Ejemplo: "el aceite Castrol EDGE 5W-30 LL"
    match = re.search(r"aceite ([A-Za-z0-9 \-]+Castrol[ A-Za-z0-9\-]*)", reply, re.IGNORECASE)
    if match:
        producto = match.group(1).strip()
        match_prod = re.search(r"Castrol[ A-Za-z0-9\-]+", producto)
        if match_prod:
            return match_prod.group(0).strip()
        return producto

    # Ejemplo: "Castrol EDGE 5W-30 LL" en cualquier parte
    match = re.search(r"Castrol[ A-Za-z0-9\-]+", reply)
    if match:
        return match.group(0).strip()

    return "el producto recomendado"