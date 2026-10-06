# System Scope — Sentient Fraud Investigation Copilot

## 1. Primary Boundary

The **Sentient Fraud Investigation Copilot** represents the analytical and investigative tier of the fraud platform. It provides forensic investigators, anti-money laundering (AML) compliance officers, and tier-2 escalation specialists with an AI-assisted environment to conduct deep natural-language inquiries, correlate complex evidence, evaluate counter-evidence, and formulate formal case escalations.

---

## 2. What Belongs to This System

| Component / Layer | Retained Features & Capabilities |
| :--- | :--- |
| **Frontend UI** | • Copilot Investigation Workspace (`CopilotPage.tsx`)<br>• Pre-configured Forensic Case Templates (`Sidebar.tsx`)<br>• Slide-over Entity & Evidence Drawer (`EntityDrawer.tsx`)<br>• 3-Tier Evidence Dossier (`EvidenceDossier.tsx`)<br>• Interactive Graph Relationship Network (`RelationshipTree.tsx`)<br>• Global Entity Search Modal (`GlobalSearchModal.tsx`) |
| **Backend APIs** | • `/api/copilot/investigate`: Multi-turn natural language investigation<br>• `/api/copilot/explain-alert/{id}`: Grounded alert explanation<br>• `/api/copilot/explain-transaction/{id}`: Grounded transaction audit<br>• `/api/copilot/explain-customer/{id}`: Grounded customer risk review<br>• `/api/retrieval/query`: Semantic retrieval and evidence assembly<br>• `/api/evidence`: 3-Tier forensic dossier generation<br>• `/api/entities`: Entity relationships and multi-hop graph nodes<br>• `/api/alerts`: Alert record and evidence packet lookup<br>• `/api/transactions`: Transaction record and evidence packet lookup<br>• `/api/customers`: Customer profile lookup<br>• `/api/devices`: Device profile lookup<br>• `/api/beneficiaries`: Beneficiary profile lookup<br>• `/api/search`: Multi-entity search |
| **Retrieval & Evidence Engine** | • Entity Resolver (`entity_resolver.py`): Maps queries to canonical IDs<br>• Evidence Builder (`evidence_builder.py`): Assembles 3-tier grounded evidence dossiers<br>• Retriever (`retriever.py`) & Indexer (`indexer.py`): Vector & keyword evidence ranking |
| **LLM & Reasoning Engine** | • Groq Client (`client.py`): Fast inference with low temperature (0.1)<br>• Deterministic Mock Adapter (`mock_adapter.py`): Fully offline fallback<br>• Grounded Prompts (`prompts.py`): Strict system prompt enforcing schema and evidence grounding<br>• Context Manager (`context_manager.py`): Session state and turn pruning<br>• Citation Validator (`service.py`): Strips hallucinated entity IDs |

---

## 3. What Belongs to the Sibling System (Command Centre)

The following capabilities are **explicitly excluded** from the Copilot repository and belong exclusively to the **Sentient Command Centre**:
* Operational Command Centre executive dashboard (`CommandCentrePage.tsx`)
* KPI metric cards and aggregate telemetry summaries (`/api/overview`)
* Alerts triage queue management and bulk status filtering (`AlertsPage.tsx`)
* High-density synthetic transaction ledger table (`TransactionsPage.tsx`)
* High-density customer surveillance registry table (`CustomersPage.tsx`)
* Raw fraud signal stream table (`/api/signals`)
* Ad-hoc manual rule evaluation tool (`/api/evaluate`)
