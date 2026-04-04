import datetime
from typing import Dict, Any, Optional

class MockExternalAPI:
    """Mock external APIs as requested in the design."""
    
    # Store dynamic overrides for simulation purposes
    _weather_overrides: Dict[int, Dict[str, Any]] = {}
    _delivery_overrides: Dict[int, Dict[str, Any]] = {}
    _status_overrides: Dict[int, Dict[str, Any]] = {}

    @classmethod
    def set_weather_override(cls, zone_id: int, overrides: Dict[str, Any]):
        cls._weather_overrides[zone_id] = overrides

    @classmethod
    def set_delivery_override(cls, zone_id: int, overrides: Dict[str, Any]):
        cls._delivery_overrides[zone_id] = overrides

    @classmethod
    def set_status_override(cls, zone_id: int, overrides: Dict[str, Any]):
        cls._status_overrides[zone_id] = overrides
        
    @classmethod
    def clear_overrides(cls):
        cls._weather_overrides = {}
        cls._delivery_overrides = {}
        cls._status_overrides = {}

    @classmethod
    def get_weather(cls, zone_id: int) -> Dict[str, Any]:
        base_weather = {
            "zone_id": zone_id,
            "rainfall_mm": 5.0,
            "waterlogging": False,
            "temperature_c": 32.0,
            "wind_speed_kmh": 10.0,
            "alert": "NONE",
            "timestamp": datetime.datetime.now().isoformat()
        }
        if zone_id in cls._weather_overrides:
            base_weather.update(cls._weather_overrides[zone_id])
        return base_weather

    @classmethod
    def get_weather_forecast(cls, zone_id: int) -> Dict[str, Any]:
        # Usually returns a disruption probability (LOW, MEDIUM, HIGH)
        base_forecast = {
            "disruption_probability": "LOW"
        }
        if zone_id in cls._weather_overrides and "disruption_probability" in cls._weather_overrides[zone_id]:
             base_forecast["disruption_probability"] = cls._weather_overrides[zone_id]["disruption_probability"]
        return base_forecast

    @classmethod
    def get_zone_status(cls, zone_id: int) -> Dict[str, Any]:
        base_status = {
            "zone_id": zone_id,
            "status": "OPEN", # OPEN, CLOSED, RESTRICTED
            "road_closure_count": 0,
            "last_updated": datetime.datetime.now().isoformat()
        }
        if zone_id in cls._status_overrides:
            base_status.update(cls._status_overrides[zone_id])
        return base_status

    @classmethod
    def get_delivery_activity(cls, zone_id: int) -> Dict[str, Any]:
        base_activity = {
            "zone_id": zone_id,
            "normal_orders_per_hour": 150,
            "current_orders_per_hour": 140, # Normal activity
            "active_partners": 35,
            "surge_pricing_active": False
        }
        if zone_id in cls._delivery_overrides:
            base_activity.update(cls._delivery_overrides[zone_id])
        return base_activity
