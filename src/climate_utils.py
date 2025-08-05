def infer_climate_from_location(lat: float, lon: float) -> str:
    """Retorna zona climática aproximada en Argentina"""
    if lat < -40:
        return "frío"
    elif lat < -30:
        return "templado"
    else:
        return "cálido"