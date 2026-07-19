# Localização do entregador — GPS
from loguru import logger

from src.database.database import drivers
from src.database.database import serialize, deserialize
from src.infra.errors import NotFoundError
from math import radians, cos, sin, asin, sqrt


def update_location(driver_id, lat, lng):
    logger.info("update location: {did} lat={lat} lng={lng}", did=driver_id, lat=lat, lng=lng)
    d = drivers.get(driver_id)
    if not d:
        raise NotFoundError("Entregador não encontrado")
    drivers.update({"location": f"{lat},{lng}"}, id=driver_id)
    return {"message": "Localização atualizada", "lat": lat, "lng": lng}


def get_location(driver_id):
    d = drivers.get(driver_id)
    if not d:
        raise NotFoundError("Entregador não encontrado")
    d = deserialize(d)
    loc = d.get("location", "0.0,0.0")
    parts = loc.split(",")
    return {"lat": float(parts[0]) if parts else 0.0, "lng": float(parts[1]) if len(parts) > 1 else 0.0}


def get_nearby_drivers(lat, lng, radius_km=5.0):
    """Busca entregadores online próximos usando fórmula de Haversine."""
    all_drivers = drivers.find(is_online=True)
    result = []
    for d in all_drivers:
        d = deserialize(d)
        loc = d.get("location", "")
        if not loc or "," not in loc:
            continue
        parts = loc.split(",")
        d_lat, d_lng = float(parts[0]), float(parts[1])

        dist = _haversine(lat, lng, d_lat, d_lng)
        if dist <= radius_km:
            result.append({
                "id": str(d["id"]),
                "name": d.get("name", ""),
                "veiculo": d.get("veiculo", ""),
                "lat": d_lat,
                "lng": d_lng,
                "distance_km": round(dist, 2),
            })

    result.sort(key=lambda x: x["distance_km"])
    return result


def _haversine(lat1, lng1, lat2, lng2):
    """Distância em km entre dois pontos GPS."""
    R = 6371
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return R * 2 * asin(sqrt(a))
