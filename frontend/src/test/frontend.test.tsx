import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';

import { CopilotPage } from '../pages/CopilotPage';
import { EntityDrawer } from '../components/EntityDrawer';
import { GlobalSearchModal } from '../components/GlobalSearchModal';
import { RawbankLogo } from '../components/RawbankLogo';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';

import { api } from '../services/api';
import {
  CopilotInvestigationResponse,
  SearchResponse,
} from '../types';

// Mock API layer
vi.mock('../services/api', () => {
  return {
    api: {
      investigateCopilot: vi.fn(),
      explainAlertCopilot: vi.fn(),
      explainTransactionCopilot: vi.fn(),
      explainCustomerCopilot: vi.fn(),
      search: vi.fn(),
      getAlert: vi.fn(),
      getTransaction: vi.fn(),
      getCustomer: vi.fn(),
      getDevice: vi.fn(),
      getBeneficiary: vi.fn(),
      getAlertEvidence: vi.fn(),
      getTransactionEvidence: vi.fn(),
      getCustomerEvidence: vi.fn(),
      getEntityEvidence: vi.fn(),
      getEntityGraph: vi.fn(),
    },
    ApiError: class ApiError extends Error {
      status: number;
      errorCode?: string;
      constructor(msg: string, status = 500) {
        super(msg);
        this.status = status;
      }
    },
  };
});

beforeEach(() => {
  vi.clearAllMocks();
});

const mockCopilotResponse: CopilotInvestigationResponse = {
  question: 'Why was alert ALT-00001 triggered?',
  session_id: 'sess-8899-aabb',
  resolved_entities: [{ entity_type: 'alert', canonical_id: 'ALT-00001' }],
  summary:
    'Alert ALT-00001 triggered due to account takeover indicators: a brand new device initiated a $4,800 USD transfer shortly after anomalous authentication.',
  risk_assessment: {
    severity: 'CRITICAL',
    risk_score: 94,
    confidence: 0.92,
  },
  supporting_evidence: [
    {
      source_id: 'TXN-00801',
      source_table: 'transactions',
      statement: 'Transfer of $4,800 USD exceeds 90-day daily velocity by 4.8x.',
      citation: '[Source: TXN-00801]',
    },
    {
      source_id: 'AUTH-00389',
      source_table: 'auth_logs',
      statement: 'Authentication from previously unseen device DEV-00125.',
      citation: '[Source: AUTH-00389]',
    },
  ],
  counter_evidence: [
    {
      source_id: 'CUS-00014',
      source_table: 'customers',
      statement: 'Customer holds FULL KYC status and long tenure at Rawbank.',
      citation: '[Source: CUS-00014]',
    },
  ],
  behavioural_deviation: [
    'Amount $4,800 USD exceeds median monthly transaction volume ($650 USD).',
    'Transaction initiated at 03:15 AM outside customer standard operating window.',
  ],
  related_activity: [
    'Device DEV-00125 was also linked to beneficiary BEN-00088 funnel.',
  ],
  evidence_gaps: [
    {
      gap_type: 'IP_GEO_MISMATCH',
      description: 'ISP routing coordinates could not be resolved.',
      impact: 'Cannot definitively confirm physical proxy usage.',
    },
  ],
  investigation_next_steps: [
    'Immediately contact customer CUS-00014 via registered mobile phone.',
    'Temporarily place outbound debit hold on account ACC-00014.',
    'Review other transactions originating from device DEV-00125.',
  ],
  escalation_recommendation:
    'ESCALATE_TO_SENIOR_FRAUD_ANALYST: Urgent Account Takeover Verification',
  source_references: [
    { source_id: 'TXN-00801', source_table: 'transactions' },
    { source_id: 'AUTH-00389', source_table: 'auth_logs' },
    { source_id: 'CUS-00014', source_table: 'customers' },
  ],
  provenance_validated: true,
  invalid_citations_removed: [],
  ambiguity_detected: false,
  unknown_entity_detected: false,
  insufficient_evidence_detected: false,
  model_used: 'llama-3.3-70b-versatile',
  processing_time_ms: 124,
  created_at: '2026-09-28T10:05:00Z',
};

const mockSearchResponse: SearchResponse = {
  query: 'CUS-00014',
  total_matches: 1,
  results: [
    {
      entity_type: 'customer',
      entity_id: 'CUS-00014',
      title: 'Christelle Mutombo',
      details: { segment: 'VIP', city: 'Kolwezi' },
    },
  ],
};

describe('Rawbank Sentient Fraud Investigation Copilot - Frontend Suite', () => {
  // 1. Copilot Console Initial Render
  it('1. Copilot investigation console renders with suggested scenarios', () => {
    render(<CopilotPage onSelectEntity={vi.fn()} />);

    expect(screen.getByText('Sentient Fraud Investigation Copilot')).toBeInTheDocument();
    expect(screen.getByText('Why was alert ALT-00001 triggered?')).toBeInTheDocument();
    expect(screen.getByText('Why is transaction TXN-00801 suspicious?')).toBeInTheDocument();
  });

  // 2. Copilot Question Submits
  it('2. Copilot question submits to POST /api/copilot/investigate', async () => {
    vi.mocked(api.investigateCopilot).mockResolvedValueOnce(mockCopilotResponse);
    render(<CopilotPage onSelectEntity={vi.fn()} />);

    const input = screen.getByPlaceholderText(/Ask Copilot a question/i);
    fireEvent.change(input, { target: { value: 'Why was alert ALT-00001 triggered?' } });
    fireEvent.submit(input.closest('form')!);

    await waitFor(() => {
      expect(api.investigateCopilot).toHaveBeenCalledWith(
        expect.objectContaining({
          question: 'Why was alert ALT-00001 triggered?',
        })
      );
    });
  });

  // 3. Structured Sections Render
  it('3. Copilot renders separate structured investigation sections', async () => {
    vi.mocked(api.investigateCopilot).mockResolvedValueOnce(mockCopilotResponse);
    render(<CopilotPage onSelectEntity={vi.fn()} />);

    const input = screen.getByPlaceholderText(/Ask Copilot a question/i);
    fireEvent.change(input, { target: { value: 'Why was alert ALT-00001 triggered?' } });
    fireEvent.submit(input.closest('form')!);

    await waitFor(() => {
      expect(screen.getByText('Executive Investigation Summary')).toBeInTheDocument();
      expect(
        screen.getByText(/Alert ALT-00001 triggered due to account takeover/i)
      ).toBeInTheDocument();
      expect(screen.getByText('CRITICAL')).toBeInTheDocument();
      expect(
        screen.getByText(/ESCALATE_TO_SENIOR_FRAUD_ANALYST/i)
      ).toBeInTheDocument();
    });
  });

  // 4. Source References Clickable
  it('4. Clickable source references [Source: ID] render in Copilot response', async () => {
    vi.mocked(api.investigateCopilot).mockResolvedValueOnce(mockCopilotResponse);
    const mockSelect = vi.fn();
    render(<CopilotPage onSelectEntity={mockSelect} />);

    const input = screen.getByPlaceholderText(/Ask Copilot a question/i);
    fireEvent.change(input, { target: { value: 'Why was alert ALT-00001 triggered?' } });
    fireEvent.submit(input.closest('form')!);

    await waitFor(() => {
      const sourceBtn = screen.getByText('[Source: TXN-00801]');
      expect(sourceBtn).toBeInTheDocument();
      fireEvent.click(sourceBtn);
      expect(mockSelect).toHaveBeenCalledWith('transactions', 'TXN-00801');
    });
  });

  // 5. Evidence Gaps Render
  it('5. Evidence gaps are rendered clearly to expose uncertainties', async () => {
    vi.mocked(api.investigateCopilot).mockResolvedValueOnce(mockCopilotResponse);
    render(<CopilotPage onSelectEntity={vi.fn()} />);

    const input = screen.getByPlaceholderText(/Ask Copilot a question/i);
    fireEvent.change(input, { target: { value: 'Why was alert ALT-00001 triggered?' } });
    fireEvent.submit(input.closest('form')!);

    await waitFor(() => {
      expect(screen.getByText('Evidence Gaps & Data Blindspots')).toBeInTheDocument();
      expect(screen.getByText('IP_GEO_MISMATCH')).toBeInTheDocument();
      expect(screen.getByText(/ISP routing coordinates could not be resolved/i)).toBeInTheDocument();
    });
  });

  // 6. Counter-Evidence Render
  it('6. Counter-evidence is visually distinct from supporting evidence', async () => {
    vi.mocked(api.investigateCopilot).mockResolvedValueOnce(mockCopilotResponse);
    render(<CopilotPage onSelectEntity={vi.fn()} />);

    const input = screen.getByPlaceholderText(/Ask Copilot a question/i);
    fireEvent.change(input, { target: { value: 'Why was alert ALT-00001 triggered?' } });
    fireEvent.submit(input.closest('form')!);

    await waitFor(() => {
      expect(screen.getByText(/Counter-Evidence \(Mitigating Context\)/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Customer holds FULL KYC status and long tenure/i)
      ).toBeInTheDocument();
    });
  });

  // 7. Multi-Turn Session Preservation
  it('7. Follow-up inquiries preserve the same session ID', async () => {
    vi.mocked(api.investigateCopilot)
      .mockResolvedValueOnce(mockCopilotResponse)
      .mockResolvedValueOnce({
        ...mockCopilotResponse,
        question: 'What happened before that?',
        summary: 'Prior to the transfer, password was changed from Lubumbashi IP.',
      });

    render(<CopilotPage onSelectEntity={vi.fn()} />);

    const input = screen.getByPlaceholderText(/Ask Copilot a question/i);
    fireEvent.change(input, { target: { value: 'Why was alert ALT-00001 triggered?' } });
    fireEvent.submit(input.closest('form')!);

    await waitFor(() => {
      expect(screen.getByText(/Session:\s*sess-889/i)).toBeInTheDocument();
    });

    fireEvent.change(input, { target: { value: 'What happened before that?' } });
    fireEvent.submit(input.closest('form')!);

    await waitFor(() => {
      expect(api.investigateCopilot).toHaveBeenLastCalledWith(
        expect.objectContaining({
          session_id: 'sess-8899-aabb',
          question: 'What happened before that?',
        })
      );
    });
  });

  // 8. Global Search
  it('8. Global search queries backend and renders matching entities', async () => {
    vi.mocked(api.search).mockResolvedValueOnce(mockSearchResponse);
    const mockSelect = vi.fn();
    render(
      <GlobalSearchModal
        isOpen={true}
        onClose={vi.fn()}
        onSelectEntity={mockSelect}
      />
    );

    const input = screen.getByPlaceholderText(/Search by ID/i);
    fireEvent.change(input, { target: { value: 'CUS-00014' } });

    await waitFor(() => {
      expect(api.search).toHaveBeenCalledWith('CUS-00014', expect.any(Number));
      expect(screen.getByText('Christelle Mutombo')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Christelle Mutombo'));
    expect(mockSelect).toHaveBeenCalledWith('customer', 'CUS-00014');
  });

  // 9. EntityDrawer renders entity detail
  it('9. EntityDrawer renders entity details and evidence attributes', async () => {
    vi.mocked(api.getTransaction).mockResolvedValueOnce({
      customer_id: 'CUS-00014',
      beneficiary_id: 'BEN-00088',
      device_id: 'DEV-00125',
      transaction_type: 'TRANSFER',
      location_city: 'Kinshasa',
      transaction_id: 'TXN-00801',
      account_id: 'ACC-00014',
      amount: 4800,
      amount_usd_equivalent: 4800,
      currency: 'USD',
      channel: 'MOBILE_APP',
      status: 'COMPLETED',
      timestamp: '2026-09-28T09:59:00Z',
    });

    render(
      <EntityDrawer
        isOpen={true}
        onClose={vi.fn()}
        entityType="transaction"
        entityId="TXN-00801"
        onSelectEntity={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getAllByText('TXN-00801')[0]).toBeInTheDocument();
      expect(screen.getAllByText(/4,800/)[0]).toBeInTheDocument();
      expect(screen.getByText(/MOBILE_APP/i)).toBeInTheDocument();
    });
  });

  // 10. Leopard Emblem
  it('10. Rawbank Leopard Emblem renders in logo lockup with official styling', () => {
    render(<RawbankLogo size="md" showSubtitle={true} showBadge={true} />);
    expect(screen.getByText('RAWBANK')).toBeInTheDocument();
    expect(screen.getByText('SENTIENT')).toBeInTheDocument();
    expect(screen.getByText(/Fraud Operations & Forensic Intelligence/i)).toBeInTheDocument();
  });

  // 11. Disclaimer
  it('11. Synthetic banking environment disclaimer renders prominently', () => {
    render(<Navbar onOpenSearch={vi.fn()} />);
    expect(
      screen.getByText(/Synthetic banking environment/i)
    ).toBeInTheDocument();
  });

  // 12. Sidebar Templates
  it('12. Sidebar forensic case templates pass prompt to Copilot', () => {
    const mockSelect = vi.fn();
    render(<Sidebar onSelectPrompt={mockSelect} />);
    expect(screen.getByText(/Account Takeover Drill-Down/i)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Account Takeover Drill-Down/i));
    expect(mockSelect).toHaveBeenCalledWith(
      'Why was alert ALT-00001 triggered for account takeover?',
      'alert',
      'ALT-00001'
    );
  });
});
