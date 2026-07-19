# Schemas do entregador
from pydantic import BaseModel, Field


class LocationUpdateRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class LocationResponse(BaseModel):
    lat: float
    lng: float


class NearbyQuery(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, gt=0, le=100)
