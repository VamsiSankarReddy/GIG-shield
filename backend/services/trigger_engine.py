import sqlite3
import datetime
from typing import Dict, Any
from mock_data.mock_services import MockExternalAPI
from services.claim_engine import execute_claim_payouts_for_zone

def is_current_time_between(start_hour: int, end_hour: int) -> bool:
    current_hour = datetime.datetime.now().hour
    return start_hour <= current_hour < end_hour

def is_current_time_peak_hours() -> bool:
    # Defining peak hours e.g. 11-14 (lunch) and 18-22 (dinner)
    current_hour = datetime.datetime.now().hour
    return (11 <= current_hour <= 14) or (18 <= current_hour <= 22)

def evaluate_zone_triggers(conn: sqlite3.Connection, zone: Dict[str, Any]):
    weather = MockExternalAPI.get_weather(zone['id'])
    status = MockExternalAPI.get_zone_status(zone['id'])
    activity = MockExternalAPI.get_delivery_activity(zone['id'])
    
    trigger_event = None
    payout_tier_modifier = 0.0
    event_severity = "Low"
    
    rain_threshold = 30 if zone['risk_type'] == 'FLOOD_PRONE' else 50
    heat_threshold = 38 if zone['risk_type'] == 'HEAT_HEAVY' else 40
    
    # --- Disruption Prediction Model ---
    if status['status'] == 'CLOSED':
        trigger_event = "ZONE_DISRUPTION"
        payout_tier_modifier = 1.0 
        event_severity = "Critical"
    elif weather['rainfall_mm'] > rain_threshold and weather['waterlogging']:
        trigger_event = "HEAVY_RAIN"
        payout_tier_modifier = 0.6 
        event_severity = "High" if weather['rainfall_mm'] > (rain_threshold + 20) else "Medium"
    elif weather['temperature_c'] > heat_threshold and is_current_time_between(12, 16):
        trigger_event = "EXTREME_HEAT"
        payout_tier_modifier = 0.3 
        event_severity = "Medium"
    elif weather['wind_speed_kmh'] > 70 or weather['alert'] == 'RED':
        trigger_event = "CYCLONE"
        payout_tier_modifier = 1.0 
        event_severity = "Critical"

    # --- Income Loss Estimator ---
    if trigger_event:
        normal_orders = max(1, activity.get('normal_orders_per_hour', 150))
        drop_ratio = activity.get('current_orders_per_hour', 150) / normal_orders
        
        if drop_ratio <= 0.5: 
            is_peak = is_current_time_peak_hours()
            validation_text = f"{(1-drop_ratio)*100:.0f}% drop in expected regional delivery activity"
            
            execute_claim_payouts_for_zone(
                conn=conn, 
                zone=zone, 
                event_type=trigger_event, 
                severity_label=event_severity, 
                validation_text=validation_text, 
                payout_tier_modifier=payout_tier_modifier, 
                is_peak_hour_event=is_peak
            )
