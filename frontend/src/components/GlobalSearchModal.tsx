import React, { useState, useEffect, useRef } from 'react';
import { Search, X, User, ReceiptText, AlertTriangle, Smartphone, Building, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { SearchMatch } from '../types';

interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectEntity: (entityType: string, entityId: string) => void;
}

export const GlobalSearchModal: React.FC<GlobalSearchModalProps> = ({
  isOpen,
  onClose,
  onSelectEntity,
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchMatch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
      setResults([]);
      setError(null);
    }
  }, [isOpen]);

  // Handle Ctrl+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          // Open handled by parent, but we can trigger it if needed
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Debounced Search API call
  useEffect(() => {
    if (!query.trim() || query.trim().length < 2) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      setError(null);
      try {
        const resp = await api.search(query.trim(), 20);
        setResults(resp.results || []);
      } catch (err: any) {
        setError(err.message || 'Failed to search');
      } finally {
        setIsLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  const getEntityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'customer':
        return <User size={15} color="var(--color-gold)" />;
      case 'transaction':
        return <ReceiptText size={15} color="var(--sev-low-text)" />;
      case 'alert':
        return <AlertTriangle size={15} color="var(--sev-critical-text)" />;
      case 'device':
        return <Smartphone size={15} color="var(--sev-medium-text)" />;
      case 'beneficiary':
        return <Building size={15} color="var(--sev-safe-text)" />;
      default:
        return <Search size={15} color="var(--text-secondary)" />;
    }
  };

  const getBadgeClass = (type: string) => {
    switch (type.toLowerCase()) {
      case 'customer':
        return 'badge badge-gold';
      case 'transaction':
        return 'badge badge-low';
      case 'alert':
        return 'badge badge-critical';
      case 'device':
        return 'badge badge-medium';
      case 'beneficiary':
        return 'badge badge-safe';
      default:
        return 'badge badge-neutral';
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(3px)',
        zIndex: 200,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '12vh',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '640px',
          maxWidth: '92vw',
          backgroundColor: 'var(--bg-panel)',
          border: '1px solid var(--border-default)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '14px 18px',
            borderBottom: '1px solid var(--border-subtle)',
            backgroundColor: 'var(--bg-card)',
          }}
        >
          <Search size={18} color="var(--color-gold)" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Search by ID (CUS-, TXN-, ALT-, DEV-, BEN-), Name, or Keyword..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontFamily: 'inherit',
            }}
          />
          {isLoading && <div className="spinner" style={{ width: '16px', height: '16px' }} />}
          <button
            onClick={onClose}
            style={{
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              padding: '2px',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Quick Suggestion Pills */}
        <div
          style={{
            padding: '8px 18px',
            display: 'flex',
            gap: '8px',
            backgroundColor: 'var(--bg-base)',
            borderBottom: '1px solid var(--border-subtle)',
            fontSize: '11px',
            color: 'var(--text-muted)',
            overflowX: 'auto',
          }}
        >
          <span>Try:</span>
          {['CUS-00014', 'TXN-00801', 'ALT-00001', 'Jean Mutombo', 'DEV-00125', 'BEN-00088'].map((sug) => (
            <button
              key={sug}
              onClick={() => setQuery(sug)}
              style={{
                background: 'var(--bg-panel)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '1px 6px',
                cursor: 'pointer',
              }}
            >
              {sug}
            </button>
          ))}
        </div>

        {/* Results List */}
        <div style={{ maxHeight: '420px', overflowY: 'auto', padding: '8px' }}>
          {error && (
            <div style={{ padding: '16px', color: 'var(--sev-critical-text)', textAlign: 'center', fontSize: '12px' }}>
              {error}
            </div>
          )}

          {!isLoading && query.trim().length >= 2 && results.length === 0 && !error && (
            <div className="state-box" style={{ padding: '32px 16px' }}>
              <div>No matching entities found for "{query}".</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Verify identifier spelling or search by natural name.
              </div>
            </div>
          )}

          {results.map((res) => (
            <div
              key={`${res.entity_type}_${res.entity_id}`}
              onClick={() => {
                onSelectEntity(res.entity_type, res.entity_id);
                onClose();
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                transition: 'background 0.1s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-card)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  {getEntityIcon(res.entity_type)}
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
                      {res.title}
                    </span>
                    <span className={getBadgeClass(res.entity_type)} style={{ fontSize: '9px', padding: '1px 5px' }}>
                      {res.entity_type}
                    </span>
                    <span style={{ fontSize: '11px', fontFamily: 'JetBrains Mono, monospace', color: 'var(--text-mono)' }}>
                      {res.entity_id}
                    </span>
                  </div>
                  {res.subtitle && (
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      {res.subtitle}
                    </div>
                  )}
                </div>
              </div>

              <ArrowRight size={14} color="var(--text-muted)" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
