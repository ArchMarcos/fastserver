# Tracking de localização do entregador - esqueleto
from src.database.database import drivers
from loguru import logger


def update_location(driver_id, lat, lng):
    logger.info("localização atualizada: {driver_id} lat: {lat} lng: {lng}", driver_id=driver_id, lat=lat, lng=lng)
    return "localização atualizada"


def get_location(driver_id):
    return {"lat": 0.0, "lng": 0.0}


def get_nearby_drivers(lat, lng, radius_km=5.0):
    return []
