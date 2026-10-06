"""Routers Export - Sentient Fraud Investigation Copilot"""
from backend.app.routers.health import router as health_router
from backend.app.routers.copilot import router as copilot_router
from backend.app.routers.retrieval import router as retrieval_router
from backend.app.routers.evidence import router as evidence_router
from backend.app.routers.entities import router as entities_router
from backend.app.routers.alerts import router as alerts_router
from backend.app.routers.transactions import router as transactions_router
from backend.app.routers.customers import router as customers_router
from backend.app.routers.devices import router as devices_router
from backend.app.routers.beneficiaries import router as beneficiaries_router
from backend.app.routers.search import router as search_router

__all__ = [
    "health_router",
    "copilot_router",
    "retrieval_router",
    "evidence_router",
    "entities_router",
    "alerts_router",
    "transactions_router",
    "customers_router",
    "devices_router",
    "beneficiaries_router",
    "search_router"
]
