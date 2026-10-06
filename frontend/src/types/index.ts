/**
 * Rawbank Sentient Fraud Intelligence Platform
 * Phase 7 Frontend - TypeScript Domain Models & API Contracts
 */

export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE' | 'SAFE';

export interface SystemMetrics {
  total_customers: number;
  total_accounts: number;
  total_transactions: number;
  total_devices: number;
  total_beneficiaries: number;
  total_alerts: number;
  total_signals: number;
  total_volume_usd: number;
}

export interface Alert {
  alert_id: string;
  transaction_id: string;
  customer_id: string;
  account_id: string;
  severity: SeverityLevel;
  composite_risk_score: number;
  scenario_type: string;
  status: string;
  reason_summary: string;
  created_at: string;
  resolved_at?: string | null;
  assignee?: string | null;
}

export interface OverviewResponse {
  service: string;
  environment: string;
  metrics: SystemMetrics;
  alerts_by_severity: Record<string, number>;
  alerts_by_scenario: Record<string, number>;
  top_mule_beneficiaries: Array<{
    beneficiary_id: string;
    beneficiary_name: string;
    routing_channel: string;
    unique_senders: number;
    aggregated_volume_usd: number;
  }>;
  recent_critical_alerts: Alert[];
  timestamp: string;
}

export interface Transaction {
  transaction_id: string;
  customer_id: string;
  account_id: string;
  beneficiary_id: string;
  device_id: string;
  amount: number;
  currency: 'CDF' | 'USD';
  amount_usd_equivalent: number;
  channel: string;
  transaction_type: string;
  location_city: string;
  status: string;
  timestamp: string;
}

export interface Customer {
  customer_id: string;
  full_name: string;
  customer_segment: string;
  kyc_status: string;
  risk_category: string;
  registered_city: string;
  registration_date?: string;
  created_at?: string;
  is_active?: boolean;
  primary_phone?: string;
  email?: string;
  account_count?: number;
  total_balance_usd?: number;
}

export interface Device {
  device_id: string;
  customer_id: string;
  device_model: string;
  operating_system: string;
  fingerprint_hash: string;
  first_seen_timestamp: string;
  last_used_timestamp: string;
  is_trusted: boolean;
}

export interface Beneficiary {
  beneficiary_id: string;
  beneficiary_name: string;
  account_or_msisdn: string;
  destination_institution: string;
  routing_channel: string;
  risk_flag: string;
  historical_volume_usd: number;
}

export interface EvidenceItem {
  type: 'EXACT_DATA' | 'CALCULATED' | 'RETRIEVED_EVIDENCE' | 'COUNTER_EVIDENCE';
  source_table: string;
  source_id: string;
  field: string;
  value: any;
  description: string;
  timestamp?: string | null;
  provenance?: Record<string, any>;
}

export interface EvidenceGap {
  gap_type: string;
  description: string;
  impact: string;
  missing_sources?: string[];
}

export interface StandardEvidencePacket {
  query: string;
  generated_at: string;
  target_entity?: Record<string, any> | null;
  resolved_entities?: Array<{
    entity_type: string;
    canonical_id: string;
    confidence: number;
    is_ambiguous: boolean;
    candidates?: any[];
  }>;
  exact_data: EvidenceItem[];
  calculated_information: EvidenceItem[];
  retrieved_evidence: EvidenceItem[];
  counter_evidence: EvidenceItem[];
  relationships: Array<Record<string, any>>;
  evidence_gaps: EvidenceGap[];
  source_references: Array<{
    id?: string;
    source_id?: string;
    table?: string;
    source_table?: string;
    description?: string;
  }>;
  deterministic_summary?: string | null;
}

export interface RiskAssessment {
  severity: SeverityLevel;
  risk_score: number;
  confidence: number;
}

export interface InvestigationEvidenceItem {
  source_id: string;
  source_table: string;
  statement: string;
  citation: string;
}

export interface InvestigationGapItem {
  gap_type: string;
  description: string;
  impact: string;
}

export interface EvidenceReference {
  source_id: string;
  source_table: string;
  field?: string | null;
  description?: string | null;
}

export interface CopilotInvestigationResponse {
  question: string;
  session_id?: string | null;
  resolved_entities: Array<Record<string, any>>;
  summary: string;
  risk_assessment: RiskAssessment;
  supporting_evidence: InvestigationEvidenceItem[];
  counter_evidence: InvestigationEvidenceItem[];
  behavioural_deviation: string[];
  related_activity: string[];
  evidence_gaps: InvestigationGapItem[];
  investigation_next_steps: string[];
  escalation_recommendation: string;
  source_references: EvidenceReference[];
  provenance_validated: boolean;
  invalid_citations_removed: string[];
  ambiguity_detected: boolean;
  unknown_entity_detected: boolean;
  insufficient_evidence_detected: boolean;
  model_used: string;
  processing_time_ms: number;
  created_at?: string;
}

export interface SearchMatch {
  entity_type: string;
  entity_id: string;
  title: string;
  subtitle?: string;
  details?: Record<string, any>;
  relevance?: number;
}

export interface SearchResponse {
  query: string;
  total_matches: number;
  results: SearchMatch[];
}

export interface RelationshipItem {
  entity_type: string;
  entity_id: string;
  relationship: string;
  hop_depth: number;
  details?: Record<string, any>;
}

export interface RelationshipResponse {
  target_entity_type: string;
  target_entity_id: string;
  max_depth: number;
  total_connections: number;
  relationships: RelationshipItem[];
}

export interface PaginationMetadata {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMetadata;
}
