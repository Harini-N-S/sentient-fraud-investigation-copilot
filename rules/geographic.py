"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rule: Geographic & Impossible Travel Detection
-----------------------------------------------------------------------------
Rule Code: R-GEO-03
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from rules.base import BaseRule, SignalResult

# Pairwise geodesic highway/flight distance matrix between DRC commercial centers (in Kilometers)
# Grounded in official geographical data for the Democratic Republic of Congo
DRC_CITY_DISTANCES_KM = {
    ("Kinshasa", "Kinshasa"): 0.0,
    ("Kinshasa", "Lubumbashi"): 1560.0,
    ("Kinshasa", "Kolwezi"): 1350.0,
    ("Kinshasa", "Goma"): 1570.0,
    ("Kinshasa", "Matadi"): 260.0,
    ("Kinshasa", "Bukavu"): 1500.0,

    ("Lubumbashi", "Lubumbashi"): 0.0,
    ("Lubumbashi", "Kolwezi"): 250.0,
    ("Lubumbashi", "Goma"): 1100.0,
    ("Lubumbashi", "Matadi"): 1750.0,
    ("Lubumbashi", "Bukavu"): 1050.0,

    ("Kolwezi", "Kolwezi"): 0.0,
    ("Kolwezi", "Goma"): 1050.0,
    ("Kolwezi", "Matadi"): 1550.0,
    ("Kolwezi", "Bukavu"): 1000.0,

    ("Goma", "Goma"): 0.0,
    ("Goma", "Matadi"): 1800.0,
    ("Goma", "Bukavu"): 100.0,

    ("Matadi", "Matadi"): 0.0,
    ("Matadi", "Bukavu"): 1750.0,

    ("Bukavu", "Bukavu"): 0.0
}


def get_city_distance_km(city1: str, city2: str) -> float:
    if city1 == city2:
        return 0.0
    pair = (city1, city2)
    rev_pair = (city2, city1)
    if pair in DRC_CITY_DISTANCES_KM:
        return DRC_CITY_DISTANCES_KM[pair]
    if rev_pair in DRC_CITY_DISTANCES_KM:
        return DRC_CITY_DISTANCES_KM[rev_pair]
    return 1000.0  # Generic inter-provincial estimate fallback


class GeographicVelocityRule(BaseRule):
    """
    R-GEO-03: Impossible Geographic Travel Velocity
    Calculates physical travel feasibility between a customer's consecutive events (transactions or logins).
    Threshold: Implied transit speed > 600.0 km/h (exceeding standard passenger commercial flight turnaround limits).
    """
    rule_code = "R-GEO-03"
    rule_name = "Impossible Geographic Travel Velocity"
    rule_category = "Geographic_Travel"
    default_weight = 35
    default_severity = "CRITICAL"

    def __init__(self, max_plausible_speed_kmh: float = 600.0):
        self.max_plausible_speed_kmh = max_plausible_speed_kmh

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        # 1. Fetch current transaction details
        cursor.execute("""
            SELECT transaction_id, customer_id, location_city, timestamp, channel
            FROM transactions
            WHERE transaction_id = ?;
        """, (transaction_id,))
        curr = cursor.fetchone()
        if not curr:
            return []

        tid, cid, curr_city, curr_ts_str, curr_chan = curr
        curr_dt = datetime.fromisoformat(curr_ts_str)

        # 2. Find the immediately preceding transaction or authentication event for this customer
        # Check prior transactions
        cursor.execute("""
            SELECT 'TRANSACTION', transaction_id, location_city, timestamp, channel
            FROM transactions
            WHERE customer_id = ? AND timestamp < ?
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (cid, curr_ts_str))
        prior_txn = cursor.fetchone()

        # Check prior authentication logs
        cursor.execute("""
            SELECT 'AUTH', activity_id, ip_city, timestamp, channel
            FROM auth_activities
            WHERE customer_id = ? AND timestamp < ?
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (cid, curr_ts_str))
        prior_auth = cursor.fetchone()

        # Pick the most recent preceding event
        candidates = [c for c in [prior_txn, prior_auth] if c is not None]
        if not candidates:
            return []

        candidates.sort(key=lambda x: datetime.fromisoformat(x[3]), reverse=True)
        most_recent_prior = candidates[0]

        ev_type, prior_ref, prior_city, prior_ts_str, prior_chan = most_recent_prior
        prior_dt = datetime.fromisoformat(prior_ts_str)

        # If cities are identical, distance is 0 km -> normal
        if prior_city == curr_city:
            return []

        distance_km = get_city_distance_km(prior_city, curr_city)
        elapsed_seconds = (curr_dt - prior_dt).total_seconds()

        # Avoid zero or negative elapsed time
        if elapsed_seconds <= 0:
            elapsed_seconds = 60.0

        elapsed_hours = elapsed_seconds / 3600.0
        implied_speed_kmh = distance_km / elapsed_hours

        if implied_speed_kmh > self.max_plausible_speed_kmh:
            elapsed_minutes = round(elapsed_seconds / 60.0, 1)

            # Ultra high speed (> 1500 km/h) = CRITICAL (weight 35)
            sev = "CRITICAL"
            weight = self.default_weight
            conf = min(0.99, 0.85 + (implied_speed_kmh / 5000.0))

            desc = (
                f"Impossible geographic travel detected: Activity occurred in {curr_city} just "
                f"{elapsed_minutes} minutes after prior activity in {prior_city}. "
                f"Distance: {distance_km:,.1f} km. Implied speed: {implied_speed_kmh:,.1f} km/h "
                f"(plausibility threshold: {self.max_plausible_speed_kmh} km/h)."
            )

            evidence = {
                "customer_id": cid,
                "current_transaction_id": tid,
                "current_location": curr_city,
                "current_channel": curr_chan,
                "current_timestamp": curr_ts_str,
                "previous_event_type": ev_type,
                "previous_event_ref": prior_ref,
                "previous_location": prior_city,
                "previous_channel": prior_chan,
                "previous_timestamp": prior_ts_str,
                "elapsed_time_minutes": elapsed_minutes,
                "distance_km": distance_km,
                "implied_speed_kmh": round(implied_speed_kmh, 1),
                "speed_threshold_kmh": self.max_plausible_speed_kmh
            }

            return [SignalResult(
                rule_code=self.rule_code,
                rule_name=self.rule_name,
                rule_category=self.rule_category,
                severity=sev,
                confidence_score=conf,
                weight=weight,
                description=desc,
                evidence_data=evidence,
                timestamp=curr_ts_str
            )]

        return []
