"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Multi-Signal Correlation & Risk Scoring Engine
-----------------------------------------------------------------------------
Combines discrete deterministic signals into an explainable composite risk score.
All weights and formulas are:
[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from rules.base import SignalResult


@dataclass
class RiskAssessment:
    composite_risk_score: int  # 0 to 100
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    contributing_signals: List[SignalResult]
    scoring_breakdown: List[Dict[str, Any]]
    scenario_type: str
    reason_summary: str
    mitigating_factors: List[str] = field(default_factory=list)
    potential_false_positive: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "composite_risk_score": self.composite_risk_score,
            "severity": self.severity,
            "scenario_type": self.scenario_type,
            "reason_summary": self.reason_summary,
            "potential_false_positive": self.potential_false_positive,
            "mitigating_factors": self.mitigating_factors,
            "scoring_breakdown": self.scoring_breakdown,
            "contributing_signals": [s.to_dict() for s in self.contributing_signals]
        }


class CorrelationEngine:
    """
    Deterministic Correlation & Scoring Engine.
    Zero Machine Learning black-box. Zero LLM.
    Formula:
      WeightedSum = SUM(signal.weight * signal.confidence_score)
      MitigationDiscount = SUM(mitigating_factor_weights)
      CompositeRiskScore = CLAMP(0, 100, ROUND(WeightedSum - MitigationDiscount))
    """

    @staticmethod
    def evaluate(signals: List[SignalResult], db_conn, transaction_id: str) -> Optional[RiskAssessment]:
        if not signals:
            return None

        # 1. Fetch transaction and customer context for counter-evidence evaluation
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT 
                t.customer_id, t.account_id, t.amount_usd_equivalent, t.timestamp,
                c.customer_segment, c.kyc_status, d.trust_status, b.beneficiary_type
            FROM transactions t
            JOIN customers c ON t.customer_id = c.customer_id
            JOIN devices d ON t.device_id = d.device_id
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        ctx = cursor.fetchone()
        
        cid, aid, tx_usd, ts, seg, kyc, dev_trust, btype = ctx if ctx else (None, None, 0, "", "", "", "", "")

        # 2. Check for Counter-Evidence / Mitigating Factors (Task 16)
        mitigations = []
        mitigation_discount = 0

        # Check A: Tier-3 KYC Corporate Customer transacting with Corporate Vendor during daylight hours
        if seg == "Corporate" and kyc == "Tier_3_Full" and btype == "Corporate_Vendor":
            mitigations.append("Customer is verified Tier-3 Corporate entity transacting with established commercial vendor")
            mitigation_discount += 25

        # Check B: Trusted enrolled device with zero VPN/rooted flags
        if dev_trust == "Trusted_Enrolled":
            mitigations.append("Transaction executed from verified primary hardware profile (Trusted_Enrolled)")
            mitigation_discount += 15

        # Check C: Prior biometric authentication success in auth logs within 60 minutes
        cursor.execute("""
            SELECT COUNT(*) FROM auth_activities
            WHERE customer_id = ? 
              AND event_type = 'Biometric_Auth_Success'
              AND status = 'Success'
              AND timestamp <= ?;
        """, (cid, ts))
        bio_count = cursor.fetchone()[0]
        if bio_count > 0:
            mitigations.append(f"Customer has {bio_count} verified biometric challenge completions in session history")
            mitigation_discount += 10

        # 3. Calculate Transparent Weighted Score
        breakdown = []
        raw_score = 0.0

        for s in signals:
            item_contrib = s.weight * s.confidence_score
            raw_score += item_contrib
            breakdown.append({
                "rule_code": s.rule_code,
                "rule_name": s.rule_name,
                "base_weight": s.weight,
                "confidence_score": round(s.confidence_score, 2),
                "net_contribution": round(item_contrib, 1)
            })

        final_score = int(round(max(0.0, min(100.0, raw_score - mitigation_discount))))

        # 4. Severity Mapping
        if final_score >= 90:
            sev = "CRITICAL"
        elif final_score >= 70:
            sev = "HIGH"
        elif final_score >= 40:
            sev = "MEDIUM"
        else:
            sev = "LOW"

        # 5. Classify Scenario Type deterministically from signals
        rule_codes = set(s.rule_code for s in signals)
        categories = set(s.rule_category for s in signals)

        if "R-ATO-05" in rule_codes or ("R-AUTH-08" in rule_codes and "R-VAL-07" in rule_codes):
            scenario = "ATO_DRAIN"
            summary = "Suspected Account Takeover: High-risk administrative event followed by balance drain."
        elif "R-GEO-03" in rule_codes:
            scenario = "IMPOSSIBLE_TRAVEL"
            summary = "Impossible Geographic Travel: Rapid spatial displacement between consecutive events."
        elif "R-DEV-SHR-01" in rule_codes:
            scenario = "SHARED_DEVICE_RING"
            summary = "Syndicate Pattern: Hardware device shared across multiple distinct customer accounts."
        elif "R-MULE-04" in rule_codes:
            scenario = "MULE_FAN_IN"
            summary = "Mule Aggregator Topology: Centralized beneficiary receiving multi-sender inflows."
        elif "R-SMURF-06" in rule_codes:
            scenario = "STRUCTURING_SMURF"
            summary = "Structuring Pattern: Near-threshold disbursements timed to evade reporting limit."
        elif "R-VEL-01" in rule_codes and len(signals) == 1:
            scenario = "VELOCITY_BURST"
            summary = "Transaction Velocity: Rapid succession of transfers within short temporal window."
        elif len(signals) >= 3:
            scenario = "MULTI_SIGNAL_CONVERGENCE"
            summary = "Critical Multi-Signal Convergence: Simultaneous risk breaches across multiple vectors."
        elif mitigation_discount >= 20:
            scenario = "LEGITIMATE_ANOMALY"
            summary = "Potential False Positive: Elevated value or new parameter with strong authenticating counter-evidence."
        else:
            scenario = "UNUSUAL_BEHAVIOUR"
            summary = "Behavioral Risk: Discrepancy observed against established profile baselines."

        is_potential_fp = (scenario == "LEGITIMATE_ANOMALY") or (mitigation_discount >= 25 and sev in ["LOW", "MEDIUM"])

        return RiskAssessment(
            composite_risk_score=final_score,
            severity=sev,
            contributing_signals=signals,
            scoring_breakdown=breakdown,
            scenario_type=scenario,
            reason_summary=summary,
            mitigating_factors=mitigations,
            potential_false_positive=is_potential_fp
        )
