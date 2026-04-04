from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import datetime
import random
from typing import Optional

from database import init_db, get_db_connection
from mock_data.mock_services import MockExternalAPI
from services.risk_engine import calculate_weekly_premium
from services.trigger_engine import evaluate_zone_triggers

app = FastAPI(title="Parametric Insurance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()

class UserCreate(BaseModel):
    name: str
    zone_id: int
    daily_working_hours: Optional[int] = 8
    works_peak_hours: Optional[bool] = True

class PolicyCreate(BaseModel):
    user_id: str

@app.post("/user")
def create_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO users (id, name, zone_id, daily_working_hours, works_peak_hours)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, user.name, user.zone_id, user.daily_working_hours, user.works_peak_hours))
    conn.commit()
    conn.close()
    
    return {"id": user_id, "message": "User created successfully"}

@app.post("/policy")
def create_policy(policy_req: PolicyCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (policy_req.user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    user = dict(user_row)
    
    cursor.execute("SELECT * FROM zones WHERE id = ?", (user['zone_id'],))
    zone_row = cursor.fetchone()
    if not zone_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Zone not found")
    zone = dict(zone_row)
    
    forecast = MockExternalAPI.get_weather_forecast(zone['id'])
    
    premium = calculate_weekly_premium(cursor, user, zone, forecast)
    max_payout = (user['daily_working_hours'] * user['hourly_income_rate']) * 2.5
    
    policy_id = str(uuid.uuid4())
    valid_from = datetime.datetime.now()
    valid_until = valid_from + datetime.timedelta(days=7)
    
    cursor.execute("""
        INSERT INTO policies (id, user_id, zone_id, premium_amount, max_payout_cap, valid_from, valid_until)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (policy_id, user['id'], zone['id'], premium, max_payout, valid_from, valid_until))
    
    conn.commit()
    conn.close()
    
    risk_level = "High" if premium >= 60 else ("Medium" if premium >= 40 else "Low")
    
    return {
        "id": policy_id, 
        "premium": round(premium, 2), 
        "max_payout_cap": round(max_payout, 2),
        "risk_level": risk_level,
        "zone_name": zone['name'],
        "zone_risk_type": zone['risk_type'],
        "message": "Policy active"
    }

@app.get("/simulate-event")
def simulate_event(zone: str, type: str):
    import random
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zones WHERE name = ?", (zone,))
    zone_row = cursor.fetchone()
    if not zone_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Zone not found")
        
    zone_data = dict(zone_row)
    zone_id = zone_data['id']
    risk_type = zone_data['risk_type']
    
    MockExternalAPI.clear_overrides()
    
    # Determine zone-specific thresholds (same as trigger engine)
    rain_threshold = 30 if risk_type == 'FLOOD_PRONE' else 50
    heat_threshold = 38 if risk_type == 'HEAT_HEAVY' else 40

    claim_generated = False
    conditions = {}

    if type == "rain":
        # Randomized rainfall generation with probability tiers:
        #   ~30% chance: dry / light rain (0-20mm)  -> no disruption
        #   ~35% chance: moderate rain    (20-threshold) -> no claim
        #   ~35% chance: heavy rain       (threshold+10 to 100mm) -> claim possible
        roll = random.random()
        if roll < 0.30:
            rainfall = round(random.uniform(0, 20), 1)
            waterlogging = False
        elif roll < 0.65:
            rainfall = round(random.uniform(20, rain_threshold), 1)
            waterlogging = random.choice([True, False])
        else:
            rainfall = round(random.uniform(rain_threshold + 10, 100), 1)
            waterlogging = True

        # Delivery activity also randomized:
        # Heavy rain correlates with lower orders, but not always
        if rainfall > rain_threshold and waterlogging:
            orders = random.randint(5, 60)  # Could be 5-60 out of 150
        else:
            orders = random.randint(80, 150)  # Normal-ish activity

        MockExternalAPI.set_weather_override(zone_id, {
            "rainfall_mm": rainfall,
            "waterlogging": waterlogging
        })
        MockExternalAPI.set_delivery_override(zone_id, {
            "current_orders_per_hour": orders
        })

        conditions = {
            "rainfall_mm": rainfall,
            "waterlogging": waterlogging,
            "orders_per_hour": orders,
            "rain_threshold": rain_threshold,
        }

        # Determine if this will trigger
        if rainfall > rain_threshold and waterlogging and orders <= 75:
            evaluate_zone_triggers(conn, zone_data)
            claim_generated = True

    elif type == "heat":
        # Randomized temperature generation:
        #   ~30% chance: comfortable (28-36C)  -> no disruption
        #   ~35% chance: warm (36-threshold)   -> borderline, no claim
        #   ~35% chance: extreme (threshold+2 to 48C) -> claim possible
        roll = random.random()
        if roll < 0.30:
            temp = round(random.uniform(28, 36), 1)
        elif roll < 0.65:
            temp = round(random.uniform(36, heat_threshold), 1)
        else:
            temp = round(random.uniform(heat_threshold + 2, 48), 1)

        if temp > heat_threshold:
            orders = random.randint(10, 70)
        else:
            orders = random.randint(90, 150)

        MockExternalAPI.set_weather_override(zone_id, {
            "temperature_c": temp
        })
        MockExternalAPI.set_delivery_override(zone_id, {
            "current_orders_per_hour": orders
        })

        conditions = {
            "temperature_c": temp,
            "orders_per_hour": orders,
            "heat_threshold": heat_threshold,
        }

        if temp > heat_threshold and orders <= 75:
            evaluate_zone_triggers(conn, zone_data)
            claim_generated = True

    conn.close()

    # Return structured API-style response
    if claim_generated:
        return {
            "status": "triggered",
            "result": "Disruption confirmed — claim generated",
            "conditions": conditions,
            "zone": zone,
            "type": type,
        }
    else:
        return {
            "status": "checked",
            "result": "No significant disruption detected",
            "conditions": conditions,
            "zone": zone,
            "type": type,
        }

@app.get("/claims/{user_id}")
def view_claims(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims WHERE user_id = ? ORDER BY processed_at DESC", (user_id,))
    claims = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"claims": claims}
