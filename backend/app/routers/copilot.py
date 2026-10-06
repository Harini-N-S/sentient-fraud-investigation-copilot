"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - API Router
-----------------------------------------------------------------------------
Provides endpoints for AI-assisted fraud investigations grounded in
retrieved forensic evidence.
The LLM is NOT the database. All facts originate from synthetic_bank.db.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Body

from backend.app.llm import (
    CopilotInvestigateRequest,
    CopilotExplainEntityRequest,
    CopilotInvestigationResponse,
    copilot_service,
    GroqConfigurationError,
    GroqAPIError,
    GroqTimeoutError
)

router = APIRouter(prefix="/api/copilot", tags=["Investigation Copilot"])


@router.post(
    "/investigate",
    response_model=CopilotInvestigationResponse,
    summary="Conduct Grounded Fraud Investigation",
    description="""
Executes the full 12-step Sentient Copilot investigation pipeline for an analyst question.
- **Pipeline:** Question -> Context Resolution -> Entity Resolution -> Evidence Packet -> Validation -> LLM -> Citation Validation.
- Preserves official Phase 3 deterministic risk scores.
- Rejects ungrounded citations.
- Explicitly handles unknown entities, ambiguity, and insufficient evidence.
"""
)
def investigate(request: CopilotInvestigateRequest):
    try:
        return copilot_service.investigate(request)
    except GroqConfigurationError as gce:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(gce)
        )
    except GroqTimeoutError as gte:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(gte)
        )
    except GroqAPIError as gae:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(gae)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation copilot error: {str(exc)}"
        )


@router.post(
    "/explain-alert/{alert_id}",
    response_model=CopilotInvestigationResponse,
    summary="Explain Alert Findings & Contributing Evidence",
    description="Generates an evidence-grounded explanation of why a specific alert was triggered and whether escalation is warranted."
)
def explain_alert(
    alert_id: str,
    session_id: Optional[str] = Query(None, description="Optional conversational session ID"),
    use_mock: Optional[bool] = Query(None, description="Force use mock adapter")
):
    try:
        return copilot_service.explain_alert(
            alert_id=alert_id,
            session_id=session_id,
            use_mock=use_mock
        )
    except GroqConfigurationError as gce:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(gce)
        )
    except GroqTimeoutError as gte:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(gte)
        )
    except GroqAPIError as gae:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(gae)
        )


@router.post(
    "/explain-transaction/{transaction_id}",
    response_model=CopilotInvestigationResponse,
    summary="Explain Transaction Suspicion & Preceding Events",
    description="Generates a grounded forensic narrative of preceding authentications, novel device flags, and baseline deviations for a transaction."
)
def explain_transaction(
    transaction_id: str,
    session_id: Optional[str] = Query(None, description="Optional conversational session ID"),
    use_mock: Optional[bool] = Query(None, description="Force use mock adapter")
):
    try:
        return copilot_service.explain_transaction(
            transaction_id=transaction_id,
            session_id=session_id,
            use_mock=use_mock
        )
    except GroqConfigurationError as gce:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(gce)
        )
    except GroqTimeoutError as gte:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(gte)
        )
    except GroqAPIError as gae:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(gae)
        )


@router.post(
    "/explain-customer/{customer_id}",
    response_model=CopilotInvestigationResponse,
    summary="Explain Customer Risk Profile & Incident History",
    description="Generates an evidence-grounded review of a customer's linked accounts, associated alerts, device sharing, and counter-evidence."
)
def explain_customer(
    customer_id: str,
    session_id: Optional[str] = Query(None, description="Optional conversational session ID"),
    use_mock: Optional[bool] = Query(None, description="Force use mock adapter")
):
    try:
        return copilot_service.explain_customer(
            customer_id=customer_id,
            session_id=session_id,
            use_mock=use_mock
        )
    except GroqConfigurationError as gce:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(gce)
        )
    except GroqTimeoutError as gte:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(gte)
        )
    except GroqAPIError as gae:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(gae)
        )
