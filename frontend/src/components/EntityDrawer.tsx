import React, { useEffect, useState } from 'react';
import {
  X,
  ExternalLink,
  ShieldAlert,
  CreditCard,
  User,
  Smartphone,
  Building,
  Sparkles,
  AlertTriangle,
  CheckCircle,
  Clock,
  Layers,
  Network,
} from 'lucide-react';
import { api } from '../services/api';
import {
  Alert,
  Transaction,
  Customer,
  Device,
  Beneficiary,
  StandardEvidencePacket,
  SeverityLevel,
} from '../types';
import { EvidenceDossier } from './EvidenceDossier';
import { RelationshipTree } from './RelationshipTree';

interface EntityDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  entityType: string;
  entityId: string;
  onSelectEntity?: (type: string, id: string) => void;
  onInvestigateCopilot?: (question: string, entityType: string, entityId: string) => void;
}

export const EntityDrawer: React.FC<EntityDrawerProps> = ({
  isOpen,
  onClose,
  entityType,
  entityId,
  onSelectEntity,
  onInvestigateCopilot,
}) => {
  const [activeTab, setActiveTab] = useState<'details' | 'evidence' | 'relationships'>('details');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Entity States
  const [alertData, setAlertData] = useState<Alert | null>(null);
  const [transactionData, setTransactionData] = useState<Transaction | null>(null);
  const [customerData, setCustomerData] = useState<Customer | null>(null);
  const [deviceData, setDeviceData] = useState<Device | null>(null);
  const [beneficiaryData, setBeneficiaryData] = useState<Beneficiary | null>(null);

  // Evidence Packet State
  const [evidencePacket, setEvidencePacket] = useState<StandardEvidencePacket | null>(null);
  const [evidenceLoading, setEvidenceLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || !entityId) return;

    let isMounted = true;
    setLoading(true);
    setError(null);
    setEvidencePacket(null);

    // Reset entity states
    setAlertData(null);
    setTransactionData(null);
    setCustomerData(null);
    setDeviceData(null);
    setBeneficiaryData(null);

    const normType = entityType.toLowerCase();

    async function fetchEntity() {
      try {
        if (normType.includes('alert')) {
          const res = await api.getAlert(entityId);
          if (isMounted) setAlertData(res);
        } else if (normType.includes('transaction')) {
          const res = await api.getTransaction(entityId);
          if (isMounted) setTransactionData(res);
        } else if (normType.includes('customer')) {
          const res = await api.getCustomer(entityId);
          if (isMounted) setCustomerData(res);
        } else if (normType.includes('device')) {
          const res = await api.getDevice(entityId);
          if (isMounted) setDeviceData(res);
        } else if (normType.includes('beneficiary')) {
          const res = await api.getBeneficiary(entityId);
          if (isMounted) setBeneficiaryData(res);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load entity details');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchEntity();

    return () => {
      isMounted = false;
    };
  }, [isOpen, entityType, entityId]);

  // Load evidence on tab click or if supported
  useEffect(() => {
    if (!isOpen || !entityId) return;
    if (activeTab !== 'evidence') return;
    if (evidencePacket) return;

    const normType = entityType.toLowerCase();
    if (!['alert', 'transaction', 'customer'].some((t) => normType.includes(t))) {
      return;
    }

    let isMounted = true;
    setEvidenceLoading(true);

    async function fetchEvidence() {
      try {
        let packet: StandardEvidencePacket | null = null;
        if (normType.includes('alert')) {
          packet = await api.getAlertEvidence(entityId);
        } else if (normType.includes('transaction')) {
          packet = await api.getTransactionEvidence(entityId);
        } else if (normType.includes('customer')) {
          packet = await api.getCustomerEvidence(entityId);
        }
        if (isMounted) setEvidencePacket(packet);
      } catch (err) {
        // Evidence not found or error
      } finally {
        if (isMounted) setEvidenceLoading(false);
      }
    }

    fetchEvidence();

    return () => {
      isMounted = false;
    };
  }, [isOpen, entityType, entityId, activeTab, evidencePacket]);

  if (!isOpen) return null;

  const getSeverityBadge = (severity: SeverityLevel) => {
    switch (severity) {
      case 'CRITICAL':
        return 'badge-critical';
      case 'HIGH':
        return 'badge-high';
      case 'MEDIUM':
        return 'badge-medium';
      case 'LOW':
        return 'badge-low';
      default:
        return 'badge-neutral';
    }
  };

  const getEntityIcon = () => {
    const t = entityType.toLowerCase();
    if (t.includes('alert')) return <ShieldAlert className="w-5 h-5 text-accent-red" />;
    if (t.includes('transaction')) return <CreditCard className="w-5 h-5 text-accent-cyan" />;
    if (t.includes('customer')) return <User className="w-5 h-5 text-accent-blue" />;
    if (t.includes('device')) return <Smartphone className="w-5 h-5 text-accent-orange" />;
    if (t.includes('beneficiary')) return <Building className="w-5 h-5 text-accent-gold" />;
    return <Layers className="w-5 h-5 text-text-muted" />;
  };

  const handleCopilotLaunch = () => {
    if (!onInvestigateCopilot) return;
    const t = entityType.toLowerCase();
    let q = `Investigate ${entityType.toUpperCase()} ${entityId}`;
    if (t.includes('alert')) {
      q = `Why was alert ${entityId} triggered?`;
    } else if (t.includes('transaction')) {
      q = `Why is transaction ${entityId} suspicious?`;
    } else if (t.includes('customer')) {
      q = `Investigate customer ${entityId}`;
    }
    onInvestigateCopilot(q, entityType, entityId);
    onClose();
  };

  const canShowEvidence = ['alert', 'transaction', 'customer'].some((t) =>
    entityType.toLowerCase().includes(t)
  );

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-fade-in">
      <div
        className="w-full max-w-2xl bg-bg-card border-l border-border-medium h-full flex flex-col shadow-2xl animate-slide-left"
        role="dialog"
        aria-modal="true"
        aria-label={`${entityType} detail`}
      >
        {/* Drawer Header */}
        <div className="px-6 py-4 border-b border-border-light bg-bg-panel/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-bg-surface rounded-lg border border-border-medium">
              {getEntityIcon()}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase tracking-wider font-mono text-text-muted">
                  {entityType}
                </span>
                <span className="text-base font-bold font-mono text-text-primary">
                  {entityId}
                </span>
              </div>
              <div className="text-xs text-text-secondary mt-0.5">
                Synthetic Banking Environment
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopilotLaunch}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-gold/15 hover:bg-accent-gold/25 border border-accent-gold/40 text-accent-gold rounded text-xs font-semibold transition-colors"
              title="Launch Sentient Fraud Investigation Copilot"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Investigate</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-text-muted hover:text-text-primary hover:bg-bg-surface rounded transition-colors"
              aria-label="Close panel"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex border-b border-border-light bg-bg-panel/40 px-6 gap-6">
          <button
            onClick={() => setActiveTab('details')}
            className={`py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === 'details'
                ? 'border-accent-gold text-accent-gold'
                : 'border-transparent text-text-muted hover:text-text-secondary'
            }`}
          >
            <span>Overview & Attributes</span>
          </button>

          {canShowEvidence && (
            <button
              onClick={() => setActiveTab('evidence')}
              className={`py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors ${
                activeTab === 'evidence'
                  ? 'border-accent-gold text-accent-gold'
                  : 'border-transparent text-text-muted hover:text-text-secondary'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Evidence Packet</span>
            </button>
          )}

          <button
            onClick={() => setActiveTab('relationships')}
            className={`py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === 'relationships'
                ? 'border-accent-gold text-accent-gold'
                : 'border-transparent text-text-muted hover:text-text-secondary'
            }`}
          >
            <Network className="w-3.5 h-3.5" />
            <span>Relationship Network</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 text-text-muted">
              <Clock className="w-8 h-8 animate-spin text-accent-gold mb-3" />
              <p className="text-sm">Retrieving entity records from synthetic bank database...</p>
            </div>
          )}

          {error && !loading && (
            <div className="p-4 rounded border border-accent-red/30 bg-accent-red/10 text-accent-red text-sm flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold">Unable to Load Entity</div>
                <div className="text-xs text-accent-red/80 mt-1">{error}</div>
              </div>
            </div>
          )}

          {!loading && !error && activeTab === 'details' && (
            <div className="space-y-6">
              {/* Alert View */}
              {alertData && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Deterministic Severity</span>
                      <div className="mt-1">
                        <span className={getSeverityBadge(alertData.severity)}>
                          {alertData.severity}
                        </span>
                      </div>
                    </div>
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Composite Risk Score</span>
                      <div className="mt-1 text-xl font-bold font-mono text-accent-gold">
                        {alertData.composite_risk_score}
                        <span className="text-xs font-normal text-text-muted"> / 100</span>
                      </div>
                    </div>
                  </div>

                  <div className="card p-4 space-y-3">
                    <h4 className="text-xs uppercase tracking-wider font-mono text-text-muted">
                      Triggered Scenario
                    </h4>
                    <p className="text-sm font-semibold text-text-primary">
                      {alertData.scenario_type.replace(/_/g, ' ')}
                    </p>
                    <div className="p-3 bg-bg-surface rounded border border-border-light text-xs text-text-secondary font-mono leading-relaxed">
                      {alertData.reason_summary}
                    </div>
                  </div>

                  <div className="card p-4 space-y-3">
                    <h4 className="text-xs uppercase tracking-wider font-mono text-text-muted">
                      Entity Provenance Links
                    </h4>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-text-muted block">Transaction</span>
                        <button
                          onClick={() => onSelectEntity?.('transaction', alertData.transaction_id)}
                          className="font-mono text-accent-cyan hover:underline flex items-center gap-1 mt-0.5"
                        >
                          {alertData.transaction_id}
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                      <div>
                        <span className="text-text-muted block">Customer</span>
                        <button
                          onClick={() => onSelectEntity?.('customer', alertData.customer_id)}
                          className="font-mono text-accent-blue hover:underline flex items-center gap-1 mt-0.5"
                        >
                          {alertData.customer_id}
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                      <div>
                        <span className="text-text-muted block">Account</span>
                        <span className="font-mono text-text-secondary mt-0.5 block">
                          {alertData.account_id}
                        </span>
                      </div>
                      <div>
                        <span className="text-text-muted block">Timestamp</span>
                        <span className="font-mono text-text-secondary mt-0.5 block">
                          {new Date(alertData.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Transaction View */}
              {transactionData && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Transaction Amount</span>
                      <div className="mt-1 text-lg font-bold font-mono text-text-primary">
                        {transactionData.currency}{' '}
                        {transactionData.amount.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                        })}
                      </div>
                      <div className="text-xs text-text-muted mt-0.5">
                        ≈ ${transactionData.amount_usd_equivalent.toLocaleString()} USD
                      </div>
                    </div>
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Status / Channel</span>
                      <div className="mt-1">
                        <span
                          className={`badge ${
                            transactionData.status === 'COMPLETED'
                              ? 'badge-safe'
                              : transactionData.status === 'FLAGGED'
                              ? 'badge-high'
                              : 'badge-neutral'
                          }`}
                        >
                          {transactionData.status}
                        </span>
                      </div>
                      <div className="text-xs text-text-secondary mt-1 font-mono uppercase">
                        {transactionData.channel} • {transactionData.transaction_type}
                      </div>
                    </div>
                  </div>

                  <div className="card p-4 space-y-3">
                    <h4 className="text-xs uppercase tracking-wider font-mono text-text-muted">
                      Transaction Context
                    </h4>
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-text-muted block">Sender Customer</span>
                        <button
                          onClick={() => onSelectEntity?.('customer', transactionData.customer_id)}
                          className="font-mono text-accent-blue hover:underline flex items-center gap-1 mt-0.5"
                        >
                          {transactionData.customer_id}
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                      <div>
                        <span className="text-text-muted block">Beneficiary</span>
                        <button
                          onClick={() =>
                            onSelectEntity?.('beneficiary', transactionData.beneficiary_id)
                          }
                          className="font-mono text-accent-gold hover:underline flex items-center gap-1 mt-0.5"
                        >
                          {transactionData.beneficiary_id}
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                      <div>
                        <span className="text-text-muted block">Initiating Device</span>
                        <button
                          onClick={() => onSelectEntity?.('device', transactionData.device_id)}
                          className="font-mono text-accent-orange hover:underline flex items-center gap-1 mt-0.5"
                        >
                          {transactionData.device_id}
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                      <div>
                        <span className="text-text-muted block">Origin City</span>
                        <span className="font-mono text-text-primary mt-0.5 block">
                          {transactionData.location_city}
                        </span>
                      </div>
                      <div className="col-span-2">
                        <span className="text-text-muted block">Execution Time</span>
                        <span className="font-mono text-text-secondary mt-0.5 block">
                          {new Date(transactionData.timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Customer View */}
              {customerData && (
                <div className="space-y-4">
                  <div className="card p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-text-primary">
                          {customerData.full_name}
                        </h3>
                        <p className="text-xs font-mono text-text-muted mt-0.5">
                          ID: {customerData.customer_id} • Registered: {customerData.registered_city}
                        </p>
                      </div>
                      <span
                        className={`badge ${
                          customerData.is_active ? 'badge-safe' : 'badge-neutral'
                        }`}
                      >
                        {customerData.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Segment</span>
                      <div className="text-sm font-semibold text-text-primary mt-1">
                        {customerData.customer_segment}
                      </div>
                    </div>
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">KYC Status</span>
                      <div className="text-sm font-semibold text-text-primary mt-1">
                        {customerData.kyc_status}
                      </div>
                    </div>
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Risk Category</span>
                      <div className="mt-1">
                        <span
                          className={`badge ${
                            customerData.risk_category === 'HIGH'
                              ? 'badge-high'
                              : customerData.risk_category === 'MEDIUM'
                              ? 'badge-medium'
                              : 'badge-low'
                          }`}
                        >
                          {customerData.risk_category}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Device View */}
              {deviceData && (
                <div className="space-y-4">
                  <div className="card p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-base font-bold text-text-primary">
                          {deviceData.device_model}
                        </h3>
                        <p className="text-xs font-mono text-text-muted mt-0.5">
                          OS: {deviceData.operating_system}
                        </p>
                      </div>
                      <span
                        className={`badge ${
                          deviceData.is_trusted ? 'badge-safe' : 'badge-high'
                        }`}
                      >
                        {deviceData.is_trusted ? 'TRUSTED DEVICE' : 'UNTRUSTED / UNKNOWN'}
                      </span>
                    </div>
                  </div>

                  <div className="card p-4 space-y-2 text-xs">
                    <div>
                      <span className="text-text-muted block">Fingerprint Hash</span>
                      <span className="font-mono text-text-secondary break-all">
                        {deviceData.fingerprint_hash}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 pt-2">
                      <div>
                        <span className="text-text-muted block">First Seen</span>
                        <span className="font-mono text-text-secondary">
                          {new Date(deviceData.first_seen_timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-text-muted block">Last Used</span>
                        <span className="font-mono text-text-secondary">
                          {new Date(deviceData.last_used_timestamp).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Beneficiary View */}
              {beneficiaryData && (
                <div className="space-y-4">
                  <div className="card p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-base font-bold text-text-primary">
                          {beneficiaryData.beneficiary_name}
                        </h3>
                        <p className="text-xs font-mono text-text-muted mt-0.5">
                          Target: {beneficiaryData.account_or_msisdn}
                        </p>
                      </div>
                      <span
                        className={`badge ${
                          beneficiaryData.risk_flag === 'HIGH' ||
                          beneficiaryData.risk_flag === 'MULE_SUSPECT'
                            ? 'badge-critical'
                            : 'badge-neutral'
                        }`}
                      >
                        {beneficiaryData.risk_flag || 'STANDARD'}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Destination Institution</span>
                      <div className="text-sm font-semibold text-text-primary mt-1 font-mono">
                        {beneficiaryData.destination_institution}
                      </div>
                    </div>
                    <div className="card p-3">
                      <span className="text-xs text-text-muted">Routing Channel</span>
                      <div className="text-sm font-semibold text-text-primary mt-1 font-mono">
                        {beneficiaryData.routing_channel}
                      </div>
                    </div>
                    <div className="card p-3 col-span-2">
                      <span className="text-xs text-text-muted">Historical Aggregated Volume</span>
                      <div className="text-base font-bold text-accent-gold mt-1 font-mono">
                        ${beneficiaryData.historical_volume_usd?.toLocaleString() || 0} USD
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {!loading && !error && activeTab === 'evidence' && (
            <div>
              {evidenceLoading ? (
                <div className="flex flex-col items-center justify-center py-12 text-text-muted">
                  <Clock className="w-7 h-7 animate-spin text-accent-gold mb-2" />
                  <p className="text-xs">Compiling four-tier evidence packet...</p>
                </div>
              ) : evidencePacket ? (
                <EvidenceDossier
                  packet={evidencePacket}
                  onSelectSource={(table: string, id: string) => onSelectEntity?.(table, id)}
                />
              ) : (
                <div className="text-center py-12 text-text-muted text-xs">
                  No evidence packet available for this entity.
                </div>
              )}
            </div>
          )}

          {!loading && !error && activeTab === 'relationships' && (
            <div>
              <RelationshipTree
                entityType={entityType}
                entityId={entityId}
                onSelectEntity={(type, id) => onSelectEntity?.(type, id)}
              />
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="px-6 py-3 border-t border-border-light bg-bg-panel/90 flex items-center justify-between text-xs text-text-muted">
          <span>Evidence Before Intelligence</span>
          <span className="font-mono">DRC Banking Context</span>
        </div>
      </div>
    </div>
  );
};
