"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - LLM Module Exports
-----------------------------------------------------------------------------
"""

from backend.app.llm.schemas import (
    CopilotInvestigateRequest,
    CopilotExplainEntityRequest,
    CopilotInvestigationResponse,
    RiskAssessment,
    EvidenceReference,
    InvestigationEvidenceItem,
    InvestigationCounterEvidenceItem,
    InvestigationGapItem
)
from backend.app.llm.client import (
    GroqClient,
    GroqConfigurationError,
    GroqAPIError,
    GroqTimeoutError
)
from backend.app.llm.mock_adapter import MockLLMAdapter
from backend.app.llm.context_manager import context_manager, ConversationContextManager
from backend.app.llm.service import CopilotService, copilot_service

__all__ = [
    "CopilotInvestigateRequest",
    "CopilotExplainEntityRequest",
    "CopilotInvestigationResponse",
    "RiskAssessment",
    "EvidenceReference",
    "InvestigationEvidenceItem",
    "InvestigationCounterEvidenceItem",
    "InvestigationGapItem",
    "GroqClient",
    "GroqConfigurationError",
    "GroqAPIError",
    "GroqTimeoutError",
    "MockLLMAdapter",
    "context_manager",
    "ConversationContextManager",
    "CopilotService",
    "copilot_service"
]
