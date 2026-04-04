import sqlite3
from typing import Dict, Any, List

DB_PATH = "devtrails.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. ZONES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        risk_type VARCHAR(50) NOT NULL,
        base_risk_score FLOAT NOT NULL
    )
    """)

    # 2. USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        zone_id INTEGER REFERENCES zones(id),
        daily_working_hours INTEGER DEFAULT 8,
        hourly_income_rate DECIMAL(10, 2) DEFAULT 75.00,
        works_peak_hours BOOLEAN DEFAULT 1,             
        dependency_on_peak_income VARCHAR(50) DEFAULT 'HIGH', 
        activity_consistency_score INTEGER DEFAULT 8,          
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. POLICIES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) REFERENCES users(id),
        zone_id INTEGER REFERENCES zones(id),
        premium_amount DECIMAL(10, 2) NOT NULL,
        max_payout_cap DECIMAL(10, 2) NOT NULL, 
        current_payout_total DECIMAL(10, 2) DEFAULT 0.0, 
        status VARCHAR(50) DEFAULT 'ACTIVE', 
        valid_from TIMESTAMP,
        valid_until TIMESTAMP
    )
    """)

    # 4. CLAIMS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id VARCHAR(36) PRIMARY KEY,
        policy_id VARCHAR(36) REFERENCES policies(id),
        user_id VARCHAR(36) REFERENCES users(id),
        trigger_type VARCHAR(100), 
        payout_amount DECIMAL(10, 2),
        trigger_reason TEXT, 
        fraud_flag BOOLEAN DEFAULT 0, 
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    
    # Pre-populate some zones if empty
    cursor.execute("SELECT COUNT(*) as count FROM zones")
    if cursor.fetchone()['count'] == 0:
        zones_data = [
            (1, "Velachery", "FLOOD_PRONE", 8.0),
            (2, "Pallikaranai", "FLOOD_PRONE", 8.5),
            (3, "T Nagar", "HEAT_HEAVY", 7.0),
            (4, "Guindy", "HEAT_HEAVY", 6.5),
            (5, "Adyar", "MIXED", 5.0)
        ]
        cursor.executemany("INSERT INTO zones (id, name, risk_type, base_risk_score) VALUES (?, ?, ?, ?)", zones_data)
        conn.commit()
        
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
