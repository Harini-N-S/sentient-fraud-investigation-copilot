"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rules Package
-----------------------------------------------------------------------------
All rule definitions and scoring thresholds are:
[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from rules.base import BaseRule, SignalResult
from rules.velocity import VelocityRule
from rules.value_spike import ValueSpikeRule
from rules.device import NewDeviceRule, SharedDeviceRule
from rules.beneficiary import NewBeneficiaryRule, SharedBeneficiaryRule
from rules.geographic import GeographicVelocityRule
from rules.structuring import StructuringRule
from rules.authentication import AuthenticationAnomalyRule, ATOPatternRule
from rules.behavioural import BehaviouralDeviationRule
from rules.correlation import CorrelationEngine, RiskAssessment
from rules.evidence import EvidencePacketBuilder, EvidencePacket
from rules.engine import FraudIntelligenceEngine, TransactionEvaluationResult

__all__ = [
    "BaseRule",
    "SignalResult",
    "VelocityRule",
    "ValueSpikeRule",
    "NewDeviceRule",
    "SharedDeviceRule",
    "NewBeneficiaryRule",
    "SharedBeneficiaryRule",
    "GeographicVelocityRule",
    "StructuringRule",
    "AuthenticationAnomalyRule",
    "ATOPatternRule",
    "BehaviouralDeviationRule",
    "CorrelationEngine",
    "RiskAssessment",
    "EvidencePacketBuilder",
    "EvidencePacket",
    "FraudIntelligenceEngine",
    "TransactionEvaluationResult"
]
