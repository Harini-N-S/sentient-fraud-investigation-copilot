import React, { useState, useEffect } from 'react';
import { Shield, Search, Terminal, Activity, Clock } from 'lucide-react';

import { RawbankLogo } from './RawbankLogo';

interface NavbarProps {
  onOpenSearch: () => void;
  activeView?: string;
  systemStatus?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenSearch, activeView = 'command-centre', systemStatus = 'CONNECTED' }) => {
  const [timeKinshasa, setTimeKinshasa] = useState('');
  const [timeLubumbashi, setTimeLubumbashi] = useState('');

  useEffect(() => {
    const updateClocks = () => {
      const now = new Date();
      // Kinshasa is UTC+1 (WAT)
      const kinshasa = new Intl.DateTimeFormat('en-GB', {
        timeZone: 'Africa/Kinshasa',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      }).format(now);

      // Lubumbashi is UTC+2 (CAT)
      const lubumbashi = new Intl.DateTimeFormat('en-GB', {
        timeZone: 'Africa/Lubumbashi',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      }).format(now);

      setTimeKinshasa(kinshasa);
      setTimeLubumbashi(lubumbashi);
    };

    updateClocks();
    const interval = setInterval(updateClocks, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 20px',
        height: '56px',
        backgroundColor: 'var(--bg-panel)',
        borderBottom: '1px solid var(--border-subtle)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Official Rawbank Brand Lockup with Congolese Leopard Emblem */}
      <RawbankLogo size="md" showSubtitle={true} showBadge={true} />

      {/* Prominent Synthetic Environment Disclaimer Boundary */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '4px 12px',
          backgroundColor: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.28)',
          borderRadius: 'var(--radius-full)',
        }}
        title="Analytical safety boundary: 100% synthetic research dataset, zero actual customer records"
      >
        <span
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: 'var(--sev-safe-text)',
            boxShadow: '0 0 6px var(--sev-safe-text)',
          }}
        />
        <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--sev-safe-text)', letterSpacing: '0.02em' }}>
          Synthetic banking environment — No real customer data
        </span>
      </div>

      {/* Right Controls: Search, Clocks, Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Quick Search Trigger */}
        <button
          onClick={onOpenSearch}
          className="btn btn-secondary"
          style={{
            padding: '5px 12px',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            gap: '8px',
          }}
          title="Search Customers, Transactions, Alerts (Ctrl+K)"
        >
          <Search size={14} />
          <span>Quick Search</span>
          <kbd
            style={{
              padding: '1px 4px',
              fontSize: '10px',
              backgroundColor: 'var(--bg-base)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '2px',
            }}
          >
            ⌘K
          </kbd>
        </button>

        {/* DR Congo Clocks */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '11px',
            fontFamily: 'JetBrains Mono, monospace',
            color: 'var(--text-secondary)',
            borderLeft: '1px solid var(--border-subtle)',
            paddingLeft: '16px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={12} color="var(--color-gold)" />
            <span>KIN:</span>
            <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{timeKinshasa || '--:--:--'}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>FBM:</span>
            <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{timeLubumbashi || '--:--:--'}</span>
          </div>
        </div>

        {/* System Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            borderLeft: '1px solid var(--border-subtle)',
            paddingLeft: '16px',
          }}
        >
          <Activity size={14} color="var(--sev-safe-text)" />
          <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>ONLINE</span>
        </div>
      </div>
    </header>
  );
};
