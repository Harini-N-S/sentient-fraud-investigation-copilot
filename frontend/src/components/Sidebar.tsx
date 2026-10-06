import React from 'react';
import {
  Bot,
  Sparkles,
  ShieldAlert,
  Network,
  Compass,
  AlertTriangle,
  UserCheck,
  Smartphone,
  Layers,
} from 'lucide-react';

export interface InvestigationTemplate {
  id: string;
  title: string;
  category: string;
  question: string;
  entityType?: string;
  entityId?: string;
}

export const COPILOT_TEMPLATES: InvestigationTemplate[] = [
  {
    id: 'alt-account-takeover',
    title: 'Account Takeover Drill-Down',
    category: 'CRITICAL ALERT',
    question: 'Why was alert ALT-00001 triggered for account takeover?',
    entityType: 'alert',
    entityId: 'ALT-00001',
  },
  {
    id: 'alt-mule-dispersion',
    title: 'Mule Funnel Rapid Dispersion',
    category: 'MULE NETWORK',
    question: 'Investigate alert ALT-00002 for mule account rapid dispersion.',
    entityType: 'alert',
    entityId: 'ALT-00002',
  },
  {
    id: 'alt-structuring',
    title: 'Structuring & Smurfing Pattern',
    category: 'AML COMPLIANCE',
    question: 'Analyze structuring pattern in alert ALT-00003.',
    entityType: 'alert',
    entityId: 'ALT-00003',
  },
  {
    id: 'alt-impossible-travel',
    title: 'Impossible Travel Anomaly',
    category: 'GEO FRAUD',
    question: 'Explain geographical anomaly in alert ALT-00004 between Kinshasa and Paris.',
    entityType: 'alert',
    entityId: 'ALT-00004',
  },
  {
    id: 'cus-dormant-revival',
    title: 'Dormant Account High-Value Spike',
    category: 'BEHAVIORAL',
    question: 'Analyze customer CUS-00014 baseline deviation and recent transactions.',
    entityType: 'customer',
    entityId: 'CUS-00014',
  },
  {
    id: 'dev-device-sharing',
    title: 'Shared Device Fraud Ring',
    category: 'DEVICE HYGIENE',
    question: 'Investigate device DEV-00125 and its associated accounts.',
    entityType: 'device',
    entityId: 'DEV-00125',
  },
];

interface SidebarProps {
  onSelectPrompt: (question: string, entityType?: string, entityId?: string) => void;
  activePromptId?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  onSelectPrompt,
  activePromptId,
}) => {
  return (
    <aside
      style={{
        width: '260px',
        backgroundColor: 'var(--bg-panel)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        flexShrink: 0,
      }}
    >
      {/* Primary Navigation & Case Scenarios */}
      <div style={{ padding: '16px 12px', overflowY: 'auto' }}>
        {/* Workspace Mode Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 12px',
            backgroundColor: 'var(--color-gold-fill)',
            border: '1px solid var(--color-gold-border)',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '16px',
          }}
        >
          <Bot size={18} color="var(--rawbank-yellow)" />
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--rawbank-yellow)', letterSpacing: '0.04em' }}>
              COPILOT WORKSPACE
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
              Evidence-Grounded Reasoning
            </div>
          </div>
        </div>

        <div
          style={{
            fontSize: '10px',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: 'var(--text-muted)',
            padding: '0 8px 8px 8px',
            fontWeight: 600,
          }}
        >
          FORENSIC CASE TEMPLATES
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {COPILOT_TEMPLATES.map((tmpl) => {
            const isActive = activePromptId === tmpl.id;
            return (
              <button
                key={tmpl.id}
                onClick={() => onSelectPrompt(tmpl.question, tmpl.entityType, tmpl.entityId)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  padding: '9px 12px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: isActive ? 'var(--bg-active)' : 'transparent',
                  border: isActive ? '1px solid var(--border-active)' : '1px solid transparent',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  width: '100%',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'var(--bg-hover)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '3px' }}>
                  <span
                    style={{
                      fontSize: '9px',
                      fontWeight: 700,
                      color: 'var(--rawbank-yellow)',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {tmpl.category}
                  </span>
                  {tmpl.entityId && (
                    <span style={{ fontSize: '9px', fontFamily: 'monospace', color: 'var(--text-muted)' }}>
                      {tmpl.entityId}
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', lineHeight: '1.3' }}>
                  {tmpl.title}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer Info / Protocol */}
      <div
        style={{
          padding: '14px 16px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-base)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
          <Network size={14} color="var(--rawbank-yellow)" />
          <span style={{ fontSize: '10.5px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '0.04em' }}>
            EVIDENCE-GROUNDED AI
          </span>
        </div>
        <div style={{ fontSize: '10px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
          Strict citation verification • Zero LLM hallucination • 4-Tier Forensic Dossiers
        </div>
      </div>
    </aside>
  );
};
