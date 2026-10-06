import React, { useState, useEffect } from 'react';
import { Network, ArrowRight, User, Smartphone, Building, ReceiptText, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';
import { RelationshipItem } from '../types';

interface RelationshipTreeProps {
  entityType: string;
  entityId: string;
  onSelectEntity?: (type: string, id: string) => void;
}

export const RelationshipTree: React.FC<RelationshipTreeProps> = ({
  entityType,
  entityId,
  onSelectEntity,
}) => {
  const [relationships, setRelationships] = useState<RelationshipItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadRelationships = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const resp = await api.getEntityRelationships(entityType, entityId, 2, 25);
        if (isMounted) {
          setRelationships(resp.relationships || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load network relationships');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadRelationships();
    return () => {
      isMounted = false;
    };
  }, [entityType, entityId]);

  if (isLoading) {
    return (
      <div className="panel" style={{ padding: '24px', textAlign: 'center' }}>
        <div className="spinner" style={{ margin: '0 auto 12px auto' }} />
        <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
          Mapping 2-Hop Relationship Network...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel" style={{ padding: '16px', color: 'var(--sev-critical-text)', fontSize: '12px' }}>
        {error}
      </div>
    );
  }

  const hop1 = relationships.filter((r) => r.hop_depth === 1);
  const hop2 = relationships.filter((r) => r.hop_depth === 2);

  const getEntityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'customer':
        return <User size={13} color="var(--color-gold)" />;
      case 'device':
        return <Smartphone size={13} color="var(--sev-medium-text)" />;
      case 'beneficiary':
        return <Building size={13} color="var(--sev-safe-text)" />;
      case 'transaction':
        return <ReceiptText size={13} color="var(--sev-low-text)" />;
      case 'alert':
        return <ShieldAlert size={13} color="var(--sev-critical-text)" />;
      default:
        return <Network size={13} color="var(--text-secondary)" />;
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Network size={16} color="var(--color-gold)" />
          <span>Forensic Relationship Network ({relationships.length} Links)</span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Bounded Max Depth: 2</span>
      </div>

      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Hop 1: Direct Connections */}
        <div>
          <div
            style={{
              fontSize: '11px',
              fontWeight: 600,
              textTransform: 'uppercase',
              color: 'var(--color-gold)',
              letterSpacing: '0.04em',
              marginBottom: '8px',
            }}
          >
            Direct 1-Hop Connections ({hop1.length})
          </div>

          {hop1.length === 0 ? (
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
              No direct connections recorded.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '8px' }}>
              {hop1.map((rel, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectEntity?.(rel.entity_type, rel.entity_id)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    cursor: onSelectEntity ? 'pointer' : 'default',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    transition: 'border-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--color-gold)')}
                  onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getEntityIcon(rel.entity_type)}
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {rel.entity_id}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
                        {rel.relationship}
                      </div>
                    </div>
                  </div>
                  <ArrowRight size={13} color="var(--text-muted)" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Hop 2: Extended Connections */}
        {hop2.length > 0 && (
          <div>
            <div
              style={{
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                color: 'var(--text-secondary)',
                letterSpacing: '0.04em',
                marginBottom: '8px',
              }}
            >
              Extended 2-Hop Network ({hop2.length})
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '8px' }}>
              {hop2.map((rel, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectEntity?.(rel.entity_type, rel.entity_id)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px dashed var(--border-default)',
                    cursor: onSelectEntity ? 'pointer' : 'default',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--color-gold)')}
                  onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-default)')}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getEntityIcon(rel.entity_type)}
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-primary)' }}>
                        {rel.entity_id}
                      </div>
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                        {rel.relationship} (Hop 2)
                      </div>
                    </div>
                  </div>
                  <ArrowRight size={13} color="var(--text-muted)" />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
