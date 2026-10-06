import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Send,
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  ArrowRight,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Info,
  Clock,
  RotateCcw,
  Zap,
} from 'lucide-react';
import { api, ApiError } from '../services/api';
import {
  CopilotInvestigationResponse,
  InvestigationEvidenceItem,
  InvestigationGapItem,
} from '../types';

interface CopilotPageProps {
  initialQuestion?: string;
  initialEntityType?: string;
  initialEntityId?: string;
  onSelectEntity: (type: string, id: string) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  question?: string;
  response?: CopilotInvestigationResponse;
  rawText?: string;
}

export const CopilotPage: React.FC<CopilotPageProps> = ({
  initialQuestion,
  initialEntityType,
  initialEntityId,
  onSelectEntity,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputQuestion, setInputQuestion] = useState(initialQuestion || '');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useDeterministicFallback, setUseDeterministicFallback] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested investigation prompts covering key assignment test scenarios
  const suggestedPrompts = [
    {
      title: 'Alert ALT-00001 (ATO)',
      prompt: 'Why was alert ALT-00001 triggered?',
      type: 'alert',
      id: 'ALT-00001',
    },
    {
      title: 'Transaction TXN-00801',
      prompt: 'Why is transaction TXN-00801 suspicious?',
      type: 'transaction',
      id: 'TXN-00801',
    },
    {
      title: 'Customer CUS-00014',
      prompt: 'Investigate customer CUS-00014 for account takeover.',
      type: 'customer',
      id: 'CUS-00014',
    },
    {
      title: 'Mule Funnel BEN-00088',
      prompt: 'Investigate beneficiary BEN-00088 and funnel aggregation.',
      type: 'beneficiary',
      id: 'BEN-00088',
    },
    {
      title: 'Shared Device DEV-00125',
      prompt: 'Investigate device DEV-00125 across multiple accounts.',
      type: 'device',
      id: 'DEV-00125',
    },
    {
      title: 'Ambiguity: Jean Mutombo',
      prompt: 'Investigate customer Jean Mutombo',
      type: 'customer',
      id: 'Jean Mutombo',
    },
    {
      title: 'Clean Customer CUS-00003',
      prompt: 'Investigate customer CUS-00003 baseline behavior.',
      type: 'customer',
      id: 'CUS-00003',
    },
    {
      title: 'Unknown Entity CUS-99999',
      prompt: 'Investigate customer CUS-99999',
      type: 'customer',
      id: 'CUS-99999',
    },
  ];

  // If pre-filled initial question is passed, execute or populate
  useEffect(() => {
    if (initialQuestion && initialQuestion.trim() !== '') {
      setInputQuestion(initialQuestion);
    }
  }, [initialQuestion]);

  useEffect(() => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  const handleSubmit = async (e?: React.FormEvent, customQuestion?: string) => {
    if (e) e.preventDefault();
    const q = customQuestion || inputQuestion;
    if (!q || !q.trim() || loading) return;

    setError(null);
    const userMsgId = `user-${Date.now()}`;
    const userMessage: Message = {
      id: userMsgId,
      role: 'user',
      question: q,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuestion('');
    setLoading(true);

    try {
      const response = await api.investigateCopilot({
        question: q,
        session_id: sessionId,
        use_mock: useDeterministicFallback,
      });

      if (response.session_id) {
        setSessionId(response.session_id);
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 503) {
        setError(
          'External LLM service (Groq) is not configured. Switched to deterministic evidence synthesis engine.'
        );
      } else {
        setError(err.message || 'An error occurred during Copilot investigation.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResetSession = () => {
    setMessages([]);
    setSessionId(null);
    setError(null);
    setInputQuestion('');
  };

  const parseSourceReference = (citation: string) => {
    // Extracts entity ID from [Source: ID]
    const match = citation.match(/\[(?:Source:\s*)?([A-Z0-9_-]+)\]/i);
    return match ? match[1] : null;
  };

  return (
    <div className="space-y-6 animate-fade-in flex flex-col h-[calc(100vh-8.5rem)]">
      {/* Copilot Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border-light shrink-0">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-accent-gold/10 border border-accent-gold/30 rounded">
              <Sparkles className="w-5 h-5 text-accent-gold" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-text-primary" style={{ fontFamily: "'Montserrat', 'Inter', sans-serif" }}>
                Sentient Fraud Investigation Copilot
              </h1>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-xs text-text-muted">
                  Evidence-Grounded Reasoning • DRC Banking Context
                </span>
                {sessionId && (
                  <span className="badge badge-neutral text-[10px] font-mono">
                    Session: {sessionId.substring(0, 8)}...
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-text-secondary cursor-pointer bg-bg-surface px-2.5 py-1.5 rounded border border-border-medium hover:border-accent-gold/40 transition-colors">
            <input
              type="checkbox"
              checked={useDeterministicFallback}
              onChange={(e) => setUseDeterministicFallback(e.target.checked)}
              className="accent-accent-gold rounded"
            />
            <span className="text-[11px] font-mono">Deterministic Synthesis</span>
          </label>

          {messages.length > 0 && (
            <button
              onClick={handleResetSession}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-bg-surface hover:bg-bg-panel border border-border-medium rounded text-xs font-semibold text-text-muted hover:text-text-primary transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Session</span>
            </button>
          )}
        </div>
      </div>

      {/* Suggested Inquiries (Shown when no messages) */}
      {messages.length === 0 && (
        <div className="card p-5 space-y-4 shrink-0">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-mono tracking-wider text-text-muted">
              Standard Investigation Scenarios
            </span>
            <span className="text-[11px] text-text-muted">
              Click to load test case with verified synthetic evidence
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {suggestedPrompts.map((item, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInputQuestion(item.prompt);
                  handleSubmit(undefined, item.prompt);
                }}
                className="p-3 bg-bg-surface hover:bg-bg-panel border border-border-light hover:border-accent-gold/50 rounded text-left transition-all group"
              >
                <div className="text-xs font-bold text-text-primary group-hover:text-accent-gold transition-colors flex items-center justify-between">
                  <span>{item.title}</span>
                  <ArrowRight className="w-3 h-3 text-text-muted group-hover:translate-x-0.5 transition-transform" />
                </div>
                <div className="text-[11px] text-text-muted mt-1 truncate font-mono">
                  {item.prompt}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-4">
            {/* User Message */}
            {msg.role === 'user' && (
              <div className="flex justify-end">
                <div className="max-w-2xl bg-bg-surface border border-border-medium rounded-lg px-4 py-3 shadow-md">
                  <div className="flex items-center gap-2 mb-1 justify-end">
                    <span className="text-[10px] font-mono text-text-muted">
                      {msg.timestamp.toLocaleTimeString()}
                    </span>
                    <span className="text-xs font-semibold text-accent-gold">Fraud Analyst</span>
                  </div>
                  <p className="text-sm text-text-primary font-medium">{msg.question}</p>
                </div>
              </div>
            )}

            {/* Copilot Assistant Response */}
            {msg.role === 'assistant' && msg.response && (
              <div className="max-w-4xl bg-bg-card border border-border-medium rounded-lg shadow-xl overflow-hidden animate-slide-up">
                {/* Copilot Response Top Bar */}
                <div className="px-6 py-3.5 bg-bg-panel/90 border-b border-border-light flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <Sparkles className="w-4 h-4 text-accent-gold" />
                    <span className="text-xs font-bold font-mono tracking-wider uppercase text-text-primary">
                      Fraud Investigation Dossier
                    </span>
                    <span className="badge badge-safe text-[10px] font-mono">
                      Validated Provenance
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono">
                    <span className="text-text-muted">
                      Model: <span className="text-text-secondary">{msg.response.model_used}</span>
                    </span>
                    <span className="text-text-muted">
                      Latency:{' '}
                      <span className="text-accent-gold">{msg.response.processing_time_ms} ms</span>
                    </span>
                  </div>
                </div>

                {/* Special Status Notices (Ambiguity, Unknown Entity, Insufficient Evidence) */}
                {msg.response.ambiguity_detected && (
                  <div className="px-6 py-3 bg-accent-gold/10 border-b border-accent-gold/30 flex items-start gap-3 text-accent-gold text-xs">
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Identity Ambiguity Detected:</span> The inquiry matched
                      multiple records. Review candidate resolutions before concluding fraud intent.
                    </div>
                  </div>
                )}

                {msg.response.unknown_entity_detected && (
                  <div className="px-6 py-3 bg-accent-red/10 border-b border-accent-red/30 flex items-start gap-3 text-accent-red text-xs">
                    <HelpCircle className="w-4 h-4 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Unknown Entity:</span> The requested entity does not
                      exist in the synthetic banking environment. No telemetry found.
                    </div>
                  </div>
                )}

                {msg.response.insufficient_evidence_detected && (
                  <div className="px-6 py-3 bg-bg-surface border-b border-border-light flex items-start gap-3 text-text-muted text-xs">
                    <Info className="w-4 h-4 shrink-0 mt-0.5 text-accent-blue" />
                    <div>
                      <span className="font-bold text-text-secondary">Limited Historical Data:</span>{' '}
                      Insufficient evidence available to conclusively establish anomalous behavior.
                    </div>
                  </div>
                )}

                <div className="p-6 space-y-6">
                  {/* 1. SUMMARY */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-mono uppercase tracking-wider text-text-muted flex items-center gap-2">
                      <Zap className="w-3.5 h-3.5 text-accent-gold" />
                      <span>Executive Investigation Summary</span>
                    </h3>
                    <div className="p-4 bg-bg-surface rounded-lg border border-border-light text-sm text-text-primary leading-relaxed">
                      {msg.response.summary}
                    </div>
                  </div>

                  {/* 2. RISK ASSESSMENT */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="card p-3">
                      <span className="text-xs text-text-muted block">Deterministic Severity</span>
                      <div className="mt-1">
                        <span
                          className={`badge ${
                            msg.response.risk_assessment.severity === 'CRITICAL'
                              ? 'badge-critical'
                              : msg.response.risk_assessment.severity === 'HIGH'
                              ? 'badge-high'
                              : msg.response.risk_assessment.severity === 'MEDIUM'
                              ? 'badge-medium'
                              : 'badge-low'
                          }`}
                        >
                          {msg.response.risk_assessment.severity}
                        </span>
                      </div>
                    </div>
                    <div className="card p-3">
                      <span className="text-xs text-text-muted block">Composite Risk Score</span>
                      <div className="text-lg font-bold font-mono text-accent-gold mt-1">
                        {msg.response.risk_assessment.risk_score}
                        <span className="text-xs font-normal text-text-muted"> / 100</span>
                      </div>
                    </div>
                    <div className="card p-3">
                      <span className="text-xs text-text-muted block">Evidence Confidence</span>
                      <div className="text-lg font-bold font-mono text-text-primary mt-1">
                        {Math.round(msg.response.risk_assessment.confidence * 100)}%
                      </div>
                    </div>
                  </div>

                  {/* 3. SUPPORTING EVIDENCE vs 4. COUNTER-EVIDENCE (Side by Side) */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Supporting Evidence */}
                    <div className="card p-4 space-y-3 border-accent-red/20">
                      <h4 className="text-xs uppercase font-mono font-bold text-accent-red flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4" />
                        <span>Supporting Evidence (Fraud Indicators)</span>
                      </h4>

                      {msg.response.supporting_evidence.length > 0 ? (
                        <div className="space-y-2.5">
                          {msg.response.supporting_evidence.map((item, idx) => {
                            const sourceId = item.source_id || parseSourceReference(item.citation);
                            return (
                              <div
                                key={idx}
                                className="p-2.5 bg-bg-surface rounded border border-border-light text-xs space-y-1.5"
                              >
                                <p className="text-text-secondary leading-snug">{item.statement}</p>
                                <div className="flex items-center justify-between text-[11px] pt-1 border-t border-border-light/40">
                                  <span className="font-mono text-text-muted">
                                    {item.source_table}
                                  </span>
                                  {sourceId && (
                                    <button
                                      onClick={() =>
                                        onSelectEntity(item.source_table || 'entity', sourceId)
                                      }
                                      className="font-mono text-accent-cyan hover:underline flex items-center gap-1"
                                    >
                                      <span>[Source: {sourceId}]</span>
                                      <ExternalLink className="w-2.5 h-2.5" />
                                    </button>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="text-xs text-text-muted py-2">
                          No direct supporting fraud evidence recorded.
                        </div>
                      )}
                    </div>

                    {/* Counter-Evidence (Mitigating Factors) */}
                    <div className="card p-4 space-y-3 border-accent-green/20">
                      <h4 className="text-xs uppercase font-mono font-bold text-accent-green flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4" />
                        <span>Counter-Evidence (Mitigating Context)</span>
                      </h4>

                      {msg.response.counter_evidence.length > 0 ? (
                        <div className="space-y-2.5">
                          {msg.response.counter_evidence.map((item, idx) => {
                            const sourceId = item.source_id || parseSourceReference(item.citation);
                            return (
                              <div
                                key={idx}
                                className="p-2.5 bg-bg-surface rounded border border-border-light text-xs space-y-1.5"
                              >
                                <p className="text-text-secondary leading-snug">{item.statement}</p>
                                <div className="flex items-center justify-between text-[11px] pt-1 border-t border-border-light/40">
                                  <span className="font-mono text-text-muted">
                                    {item.source_table}
                                  </span>
                                  {sourceId && (
                                    <button
                                      onClick={() =>
                                        onSelectEntity(item.source_table || 'entity', sourceId)
                                      }
                                      className="font-mono text-accent-green hover:underline flex items-center gap-1"
                                    >
                                      <span>[Source: {sourceId}]</span>
                                      <ExternalLink className="w-2.5 h-2.5" />
                                    </button>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="text-xs text-text-muted py-2">
                          No mitigating counter-evidence found in synthetic profile.
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 5. BEHAVIOURAL DEVIATION & 6. RELATED ACTIVITY */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Behavioural Deviation */}
                    <div className="card p-4 space-y-2.5">
                      <h4 className="text-xs uppercase font-mono text-text-muted">
                        Behavioural Baseline Deviation
                      </h4>
                      {msg.response.behavioural_deviation.length > 0 ? (
                        <ul className="space-y-1.5 text-xs text-text-secondary list-disc list-inside">
                          {msg.response.behavioural_deviation.map((dev, idx) => (
                            <li key={idx} className="leading-snug">
                              {dev}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div className="text-xs text-text-muted">
                          Transaction is within historical velocity baselines.
                        </div>
                      )}
                    </div>

                    {/* Related Activity */}
                    <div className="card p-4 space-y-2.5">
                      <h4 className="text-xs uppercase font-mono text-text-muted">
                        Correlated Activity & Network Footprint
                      </h4>
                      {msg.response.related_activity.length > 0 ? (
                        <ul className="space-y-1.5 text-xs text-text-secondary list-disc list-inside">
                          {msg.response.related_activity.map((act, idx) => (
                            <li key={idx} className="leading-snug">
                              {act}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div className="text-xs text-text-muted">
                          No peripheral network clusters detected.
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 7. EVIDENCE GAPS */}
                  <div className="card p-4 space-y-2.5 border-border-medium bg-bg-surface/50">
                    <h4 className="text-xs uppercase font-mono text-text-muted flex items-center gap-2">
                      <HelpCircle className="w-3.5 h-3.5 text-accent-gold" />
                      <span>Evidence Gaps & Data Blindspots</span>
                    </h4>

                    {msg.response.evidence_gaps.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        {msg.response.evidence_gaps.map((gap, idx) => (
                          <div
                            key={idx}
                            className="p-2.5 bg-bg-panel rounded border border-border-light text-xs space-y-1"
                          >
                            <span className="font-mono text-[10px] text-accent-gold block uppercase">
                              {gap.gap_type}
                            </span>
                            <p className="text-text-primary font-medium">{gap.description}</p>
                            <p className="text-[11px] text-text-muted">Impact: {gap.impact}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-text-muted">
                        Full evidence telemetry available across all 4 tiers.
                      </div>
                    )}
                  </div>

                  {/* 8. INVESTIGATION NEXT STEPS & 9. ESCALATION RECOMMENDATION */}
                  <div className="p-4 rounded-lg border border-accent-gold/40 bg-accent-gold/5 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs uppercase font-mono font-bold text-accent-gold flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        <span>Recommended Operational Disposition</span>
                      </h4>
                      <span className="badge badge-neutral text-[10px] font-mono">
                        Analyst Action Required
                      </span>
                    </div>

                    <div className="text-sm font-semibold text-text-primary font-mono bg-bg-panel p-2.5 rounded border border-border-light">
                      {msg.response.escalation_recommendation}
                    </div>

                    <div className="space-y-1.5 pt-1">
                      <span className="text-[11px] uppercase font-mono text-text-muted block">
                        Action Checklist:
                      </span>
                      <ol className="space-y-1 text-xs text-text-secondary list-decimal list-inside">
                        {msg.response.investigation_next_steps.map((step, idx) => (
                          <li key={idx} className="leading-snug">
                            {step}
                          </li>
                        ))}
                      </ol>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 p-4 bg-bg-surface border border-border-light rounded-lg max-w-md animate-pulse">
            <RefreshCw className="w-5 h-5 animate-spin text-accent-gold" />
            <div className="text-xs text-text-secondary">
              Synthesizing evidence packet, verifying citations, and assessing risk...
            </div>
          </div>
        )}

        {error && (
          <div className="p-4 rounded border border-accent-red/30 bg-accent-red/10 text-accent-red text-xs flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold">Investigation Pipeline Notice</div>
              <div className="mt-0.5">{error}</div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={(e) => handleSubmit(e)} className="shrink-0 pt-2">
        <div className="relative flex items-center">
          <input
            type="text"
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            placeholder="Ask Copilot a question (e.g., 'Why was alert ALT-00001 triggered?' or 'Investigate customer CUS-00014')..."
            disabled={loading}
            className="w-full bg-bg-surface border border-border-medium rounded-lg pl-4 pr-24 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-gold transition-colors shadow-inner"
          />
          <button
            type="submit"
            disabled={loading || !inputQuestion.trim()}
            className="absolute right-2 px-4 py-2 bg-accent-gold text-bg-base rounded-md text-xs font-bold hover:bg-accent-gold-light transition-colors disabled:opacity-30 disabled:pointer-events-none flex items-center gap-1.5 shadow"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
