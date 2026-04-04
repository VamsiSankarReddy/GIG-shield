import sqlite3
from typing import Dict, Any

def get_zone_claims_count(cursor: sqlite3.Cursor, zone_id: int, days: int) -> int:
    cursor.execute("""
        SELECT COUNT(*) as count FROM claims c 
        JOIN policies p ON c.policy_id = p.id
        WHERE p.zone_id = ? AND c.processed_at >= datetime('now', ?)
    """, (zone_id, f"-{days} days"))
    row = cursor.fetchone()
    return row['count'] if row else 0

def get_user_claims_count(cursor: sqlite3.Cursor, user_id: str, days: int) -> int:
    cursor.execute("""
        SELECT COUNT(*) as count FROM claims 
        WHERE user_id = ? AND processed_at >= datetime('now', ?)
    """, (user_id, f"-{days} days"))
    row = cursor.fetchone()
    return row['count'] if row else 0

def calculate_weekly_premium(cursor: sqlite3.Cursor, user: Dict[str, Any], zone: Dict[str, Any], forecast_api_data: Dict[str, Any]) -> float:
    # 1. Base Zone Risk & Zone-Level Adaptive Learning
    base_risk = zone.get('base_risk_score', 5.0)
    
    zone_claims_last_week = get_zone_claims_count(cursor, zone['id'], days=7)
    zone_risk_modifier = 1.0
    if zone_claims_last_week >= 50:  # High regional claim volume threshold
        zone_risk_modifier = 1.10
        
    adjusted_zone_risk = base_risk * zone_risk_modifier
    
    # 2. Predictive Element (Forecast next 24h)
    predictive_multiplier = 1.0
    if forecast_api_data.get('disruption_probability') == 'HIGH':
        predictive_multiplier = 1.25
    elif forecast_api_data.get('disruption_probability') == 'MEDIUM':
        predictive_multiplier = 1.10
    
    # 3. User-Level Factors
    user_risk_modifier = 1.0
    if user.get('works_peak_hours'): 
        user_risk_modifier += 0.20 
    if user.get('dependency_on_peak_income') == 'HIGH': 
        user_risk_modifier += 0.10 
    
    activity_penalty = (10 - user.get('activity_consistency_score', 8)) * 0.05
    user_risk_modifier += activity_penalty
    
    # 4. User-Level Adaptive Risk Learning
    last_week_claims = get_user_claims_count(cursor, user['id'], days=7)
    if last_week_claims >= 2:
        user_risk_modifier += 0.10
    
    # Final Risk Model
    total_risk_score = (adjusted_zone_risk * 0.7) * predictive_multiplier * user_risk_modifier
    
    if total_risk_score >= 8.5: return 60.0 # High
    elif total_risk_score >= 5.0: return 40.0 # Medium
    else: return 25.0 # Low
