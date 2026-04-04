import sqlite3
import uuid
from typing import Dict, Any

def execute_claim_payouts_for_zone(conn: sqlite3.Connection, zone: Dict[str, Any], event_type: str, severity_label: str, validation_text: str, payout_tier_modifier: float, is_peak_hour_event: bool):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM policies WHERE zone_id = ? AND status = 'ACTIVE'", (zone['id'],))
    active_policies = [dict(row) for row in cursor.fetchall()]
    
    for policy in active_policies:
        cursor.execute("SELECT * FROM users WHERE id = ?", (policy['user_id'],))
        user_row = cursor.fetchone()
        if not user_row:
            continue
        user = dict(user_row)
            
        # FRAUD VALIDATION LAYER
        cursor.execute("SELECT COUNT(*) as count FROM claims WHERE user_id = ? AND processed_at >= datetime('now', '-30 days')", (user['id'],))
        recent_claims = cursor.fetchone()['count']
        
        is_fraud_flagged = False
        if recent_claims >= 5: is_fraud_flagged = True
        if user['activity_consistency_score'] <= 3: is_fraud_flagged = True
        
        if is_fraud_flagged:
            # Create flagged claim
            claim_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO claims (id, policy_id, user_id, trigger_type, payout_amount, trigger_reason, fraud_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (claim_id, policy['id'], user['id'], event_type, 0.0, "Flagged for manual review (abnormal frequency or consistency)", 1))
            continue
            
        # CALCULATE PAYOUT
        max_daily_income = user['daily_working_hours'] * float(user['hourly_income_rate'])
        peak_adjustment = 1.20 if (is_peak_hour_event and user['works_peak_hours']) else 1.0
        calculated_payout = max_daily_income * payout_tier_modifier * peak_adjustment
        
        # MULTIPLE CLAIMS CAP ENFORCEMENT
        available_cap = float(policy['max_payout_cap']) - float(policy['current_payout_total'])
        if available_cap <= 0:
            continue  # Policy maxed out
            
        final_payout = min(calculated_payout, available_cap)
        
        # STRUCTURED EXPLANATION LAYER
        peak_text = "+20% peak-hour severity adjustment" if peak_adjustment > 1.0 else "None"
        cap_text = " | Cap Notice: Payout reduced due to remaining weekly policy cap." if final_payout < calculated_payout else ""
        
        payout_reason = (f"Trigger: {event_type} | Severity: {severity_label} | "
                         f"Zone Context: {zone['name']} | Income Validation: {validation_text} | "
                         f"Adjustments: {peak_text}{cap_text}")
                         
        claim_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO claims (id, policy_id, user_id, trigger_type, payout_amount, trigger_reason, fraud_flag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, policy['id'], user['id'], event_type, final_payout, payout_reason, 0))
        
        new_total = float(policy['current_payout_total']) + final_payout
        
        status = 'ACTIVE'
        if new_total >= float(policy['max_payout_cap']):
            status = 'MAX_CAPPED'
            
        cursor.execute("""
            UPDATE policies SET current_payout_total = ?, status = ? WHERE id = ?
        """, (new_total, status, policy['id']))
        
    conn.commit()
