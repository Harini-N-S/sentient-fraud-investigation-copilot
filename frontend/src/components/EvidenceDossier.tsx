import React, { useState } from 'react';
import {
  Database,
  Calculator,
  History,
  ShieldCheck,
  AlertCircle,
  FileText,
  ChevronDown,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import { StandardEvidencePacket, EvidenceItem, EvidenceGap } from '../types';

interface EvidenceDossierProps {
  packet: StandardEvidencePacket;
  onSelectSource?: (table: string, id: string) => void;
}

export const EvidenceDossier: React.FC<EvidenceDossierProps> = ({ packet, onSelectSource }) => {
  const [openSection, setOpenSection] = useState<{ [key: string]: boolean }>({
    exact: true,
    calc: true,
    retrieved: true,
    counter: true,
    gaps: true,
  });

  const toggleSection = (key: string) => {
    setOpenSection((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSourceClick = (table: string, id: string) => {
    if (onSelectSource) {
      onSelectSource(table, id);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {/* Deterministic Summary Box if available */}
      {packet.deterministic_summary && (
        <div
          style={{
            padding: '12px 16px',
            backgroundColor: 'var(--bg-card)',
            borderLeft: '3px solid var(--color-gold)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '12px',
            lineHeight: '1.5',
            color: 'var(--text-primary)',
          }}
        >
          <div style={{ fontWeight: 600, color: 'var(--color-gold)', marginBottom: '4px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Deterministic Forensic Dossier Summary
          </div>
          <div>{packet.deterministic_summary}</div>
        </div>
      )}

      {/* COUNTER-EVIDENCE (Mandatory False-Positive / Mitigating Factors) */}
      {packet.counter_evidence && packet.counter_evidence.length > 0 && (
        <div
          className="panel"
          style={{
            borderColor: 'var(--sev-safe-border)',
            backgroundColor: 'rgba(16, 185, 129, 0.04)',
          }}
        >
          <div
            className="panel-header"
            onClick={() => toggleSection('counter')}
            style={{
              cursor: 'pointer',
              color: 'var(--sev-safe-text)',
              backgroundColor: 'rgba(16, 185, 129, 0.08)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={16} />
              <span>Counter-Evidence & Mitigating Facts ({packet.counter_evidence.length})</span>
            </div>
            {openSection.counter ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </div>

          {openSection.counter && (
            <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {packet.counter_evidence.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-panel)',
                    border: '1px solid var(--sev-safe-border)',
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-primary)', fontWeight: 500 }}>
                      {item.description}
                    </div>
                    {item.value !== undefined && item.value !== null && (
                      <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        Field: <span style={{ color: 'var(--text-mono)' }}>{item.field}</span> ={' '}
                        <span style={{ fontWeight: 600 }}>{String(item.value)}</span>
                      </div>
                    )}
                  </div>
                  <button
                    className="source-pill"
                    onClick={() => handleSourceClick(item.source_table, item.source_id)}
                    title={`Inspect ${item.source_table} record`}
                  >
                    <span>[Source: {item.source_id}]</span>
                    <ExternalLink size={10} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TIER 1: EXACT DATA (Immutable Database Ledger) */}
      <div className="panel">
        <div
          className="panel-header"
          onClick={() => toggleSection('exact')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={15} color="var(--sev-low-text)" />
            <span>Tier 1: Immutable Database Records ({packet.exact_data.length})</span>
          </div>
          {openSection.exact ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>

        {openSection.exact && (
          <div className="panel-body" style={{ padding: 0 }}>
            <div className="dense-table-wrapper">
              <table className="dense-table">
                <thead>
                  <tr>
                    <th>Source Table</th>
                    <th>Record ID</th>
                    <th>Field / Attribute</th>
                    <th>Verified Value</th>
                    <th>Inspect</th>
                  </tr>
                </thead>
                <tbody>
                  {packet.exact_data.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ color: 'var(--text-secondary)' }}>{item.source_table}</td>
                      <td style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--text-mono)' }}>
                        {item.source_id}
                      </td>
                      <td style={{ fontWeight: 500 }}>{item.field}</td>
                      <td style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                        {typeof item.value === 'number' ? item.value.toLocaleString() : String(item.value)}
                      </td>
                      <td>
                        <button
                          className="source-pill"
                          onClick={() => handleSourceClick(item.source_table, item.source_id)}
                        >
                          [Source: {item.source_id}]
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* TIER 2: CALCULATED INFORMATION (Formulas, Risk Scores, Deviation) */}
      <div className="panel">
        <div
          className="panel-header"
          onClick={() => toggleSection('calc')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Calculator size={15} color="var(--color-gold)" />
            <span>Tier 2: Calculated Indicators & Scores ({packet.calculated_information.length})</span>
          </div>
          {openSection.calc ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>

        {openSection.calc && (
          <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {packet.calculated_information.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '12px', color: 'var(--text-primary)' }}>
                    {item.field}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    {item.description}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span
                    style={{
                      fontFamily: 'JetBrains Mono, monospace',
                      fontSize: '13px',
                      fontWeight: 700,
                      color: item.field.includes('score') ? 'var(--color-gold)' : 'var(--text-primary)',
                    }}
                  >
                    {String(item.value)}
                  </span>
                  <button
                    className="source-pill"
                    onClick={() => handleSourceClick(item.source_table, item.source_id)}
                  >
                    [Source: {item.source_id}]
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* TIER 3: RETRIEVED EVIDENCE (Historical Baselines, Prior Alerts, Logs) */}
      <div className="panel">
        <div
          className="panel-header"
          onClick={() => toggleSection('retrieved')}
          style={{ cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History size={15} color="var(--sev-medium-text)" />
            <span>Tier 3: Contextual Evidence & Signals ({packet.retrieved_evidence.length})</span>
          </div>
          {openSection.retrieved ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>

        {openSection.retrieved && (
          <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {packet.retrieved_evidence.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
              >
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-primary)' }}>{item.description}</div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Origin: {item.source_table}
                  </div>
                </div>
                <button
                  className="source-pill"
                  onClick={() => handleSourceClick(item.source_table, item.source_id)}
                >
                  [Source: {item.source_id}]
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* EVIDENCE GAPS (Explicit Missing Data Points) */}
      {packet.evidence_gaps && packet.evidence_gaps.length > 0 && (
        <div
          className="panel"
          style={{
            borderColor: 'var(--sev-high-border)',
            backgroundColor: 'rgba(249, 115, 22, 0.04)',
          }}
        >
          <div
            className="panel-header"
            onClick={() => toggleSection('gaps')}
            style={{
              cursor: 'pointer',
              color: 'var(--sev-high-text)',
              backgroundColor: 'rgba(249, 115, 22, 0.08)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={16} />
              <span>Documented Evidence Gaps ({packet.evidence_gaps.length})</span>
            </div>
            {openSection.gaps ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </div>

          {openSection.gaps && (
            <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {packet.evidence_gaps.map((gap, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-panel)',
                    border: '1px solid var(--sev-high-border)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="badge badge-high" style={{ fontSize: '10px' }}>
                      {gap.gap_type}
                    </span>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {gap.description}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    Forensic Impact: {gap.impact}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
