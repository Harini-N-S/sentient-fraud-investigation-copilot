"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Conversation Context Manager
-----------------------------------------------------------------------------
Lightweight, controlled investigation session manager for multi-turn context.
Resolves anaphora and contextual references (e.g., "What happened before that?",
"Who else uses this device?") without unbounded autonomous state.
Maintains strict evidence grounding across conversational turns.
"""

import time
import re
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    question: str
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    summary_snippet: Optional[str] = None


class InvestigationSession(BaseModel):
    session_id: str
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)
    last_entity_type: Optional[str] = None
    last_entity_id: Optional[str] = None
    last_customer_id: Optional[str] = None
    last_transaction_id: Optional[str] = None
    last_alert_id: Optional[str] = None
    last_device_id: Optional[str] = None
    turns: List[ConversationTurn] = Field(default_factory=list)


class ConversationContextManager:
    """
    Manages in-memory conversational sessions with automatic TTL expiration.
    Keeps context lightweight and bounded (max 5 turns per session).
    """

    MAX_SESSIONS = 500
    SESSION_TTL_SECONDS = 3600  # 1 hour
    MAX_TURNS_PER_SESSION = 5

    def __init__(self):
        self._sessions: Dict[str, InvestigationSession] = {}

    def get_or_create_session(self, session_id: str) -> InvestigationSession:
        """Retrieves an existing session or creates a new one, purging expired sessions."""
        self._cleanup_expired()
        if session_id not in self._sessions:
            if len(self._sessions) >= self.MAX_SESSIONS:
                # Evict oldest session
                oldest_id = min(self._sessions.keys(), key=lambda k: self._sessions[k].last_active)
                del self._sessions[oldest_id]
            self._sessions[session_id] = InvestigationSession(session_id=session_id)
        session = self._sessions[session_id]
        session.last_active = time.time()
        return session

    def resolve_contextual_query(
        self,
        session_id: Optional[str],
        query: str
    ) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
        """
        Inspects query for contextual pronouns/references ('that', 'this device', 'the customer').
        Returns:
            (resolved_query, entity_type_override, entity_id_override, context_summary)
        """
        if not session_id or session_id not in self._sessions:
            return query, None, None, None

        session = self._sessions[session_id]
        q_lower = query.lower().strip()

        entity_type: Optional[str] = None
        entity_id: Optional[str] = None
        augmented_query = query

        # Detect pronouns and contextual phrases
        refers_to_device = any(p in q_lower for p in ["this device", "that device", "the device", "same device"])
        refers_to_previous_event = any(p in q_lower for p in ["before that", "after that", "prior to that", "what happened before", "what happened after", "prior to this"])
        refers_to_customer = any(p in q_lower for p in ["this customer", "that customer", "the customer", "for him", "for her"])
        refers_to_alert = any(p in q_lower for p in ["this alert", "that alert", "the alert", "why was it flagged"])

        if refers_to_device and session.last_device_id:
            entity_type = "device"
            entity_id = session.last_device_id
            augmented_query = f"{query} (referencing device {session.last_device_id})"
        elif refers_to_previous_event:
            if session.last_transaction_id:
                entity_type = "transaction"
                entity_id = session.last_transaction_id
                augmented_query = f"What events and authentication occurred before transaction {session.last_transaction_id}?"
            elif session.last_alert_id:
                entity_type = "alert"
                entity_id = session.last_alert_id
                augmented_query = f"What events and transactions preceded alert {session.last_alert_id}?"
            elif session.last_customer_id:
                entity_type = "customer"
                entity_id = session.last_customer_id
                augmented_query = f"What events preceded the recent suspicious activity for customer {session.last_customer_id}?"
        elif refers_to_customer and session.last_customer_id:
            entity_type = "customer"
            entity_id = session.last_customer_id
            augmented_query = f"{query} (referencing customer {session.last_customer_id})"
        elif refers_to_alert and session.last_alert_id:
            entity_type = "alert"
            entity_id = session.last_alert_id
            augmented_query = f"{query} (referencing alert {session.last_alert_id})"
        elif ("that" in q_lower or "it" in q_lower) and session.last_entity_id:
            entity_type = session.last_entity_type
            entity_id = session.last_entity_id
            augmented_query = f"{query} (referencing {session.last_entity_type} {session.last_entity_id})"

        # Build context narrative summary for the prompt
        context_summary = None
        if session.turns:
            recent_turns = session.turns[-2:]
            summaries = [f"Q: '{t.question}' -> Entity: {t.target_entity_type} {t.target_entity_id}" for t in recent_turns]
            context_summary = "Previous investigation steps in this session:\n" + "\n".join(summaries)

        return augmented_query, entity_type, entity_id, context_summary

    def record_turn(
        self,
        session_id: str,
        question: str,
        entity_type: Optional[str],
        entity_id: Optional[str],
        summary: str
    ):
        """Updates session state with the completed investigation turn."""
        session = self.get_or_create_session(session_id)
        if entity_type and entity_id:
            session.last_entity_type = entity_type
            session.last_entity_id = entity_id
            if entity_type == "customer":
                session.last_customer_id = entity_id
            elif entity_type == "transaction":
                session.last_transaction_id = entity_id
            elif entity_type == "alert":
                session.last_alert_id = entity_id
            elif entity_type == "device":
                session.last_device_id = entity_id

        # Auto-extract IDs from summary or question if not explicitly set
        if not session.last_device_id:
            dev_match = re.search(r"DEV-\d{5}", question + " " + summary)
            if dev_match:
                session.last_device_id = dev_match.group(0)

        if not session.last_transaction_id:
            txn_match = re.search(r"TXN-\d{5}", question + " " + summary)
            if txn_match:
                session.last_transaction_id = txn_match.group(0)

        if not session.last_customer_id:
            cus_match = re.search(r"CUS-\d{5}", question + " " + summary)
            if cus_match:
                session.last_customer_id = cus_match.group(0)

        if not session.last_alert_id:
            alt_match = re.search(r"ALT-\d{5}", question + " " + summary)
            if alt_match:
                session.last_alert_id = alt_match.group(0)

        turn = ConversationTurn(
            question=question,
            target_entity_type=entity_type or session.last_entity_type,
            target_entity_id=entity_id or session.last_entity_id,
            summary_snippet=summary[:200]
        )
        session.turns.append(turn)
        if len(session.turns) > self.MAX_TURNS_PER_SESSION:
            session.turns.pop(0)

    def _cleanup_expired(self):
        """Removes sessions older than SESSION_TTL_SECONDS."""
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now - s.last_active > self.SESSION_TTL_SECONDS]
        for sid in expired:
            del self._sessions[sid]


context_manager = ConversationContextManager()
