import React from 'react';

interface RawbankLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showSubtitle?: boolean;
  showBadge?: boolean;
}

export const RawbankLogo: React.FC<RawbankLogoProps> = ({
  size = 'md',
  showSubtitle = true,
  showBadge = true,
}) => {
  const iconSize = size === 'sm' ? 26 : size === 'lg' ? 40 : 32;
  const titleSize = size === 'sm' ? '13px' : size === 'lg' ? '18px' : '15px';
  const badgeSize = size === 'sm' ? '10px' : '11px';

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', userSelect: 'none' }}>
      {/* Official Congolese Leopard Emblem Shield */}
      <div
        style={{
          width: `${iconSize}px`,
          height: `${iconSize}px`,
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <svg
          viewBox="0 0 48 48"
          width={iconSize}
          height={iconSize}
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Obsidian Base Plate */}
          <rect width="48" height="48" rx="10" fill="#0E131B" />
          <rect
            x="1"
            y="1"
            width="46"
            height="46"
            rx="9"
            stroke="#FCB900"
            strokeOpacity="0.45"
            strokeWidth="1.5"
          />

          {/* Leopard Head Silhouette / Shield */}
          <path
            d="M24 10L36 17V28C36 34.5 30.5 39.5 24 41.5C17.5 39.5 12 34.5 12 28V17L24 10Z"
            fill="#FCB900"
            fillOpacity="0.14"
            stroke="#FCB900"
            strokeWidth="2"
            strokeLinejoin="round"
          />

          {/* Agile Claws / Chevrons (Vigilance & Strength) */}
          <path
            d="M21 20L24 17L27 20"
            stroke="#FCB900"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M18 25L24 21L30 25"
            stroke="#FCB900"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M21 30L24 27L27 30"
            stroke="#FCB900"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Central Strategic Focus Point */}
          <circle cx="24" cy="34" r="1.75" fill="#FCB900" />
        </svg>
      </div>

      {/* Corporate Wordmark & Platform Designation */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
          <span
            style={{
              fontFamily: "'Montserrat', 'Inter', sans-serif",
              fontWeight: 800,
              fontSize: titleSize,
              letterSpacing: '0.05em',
              color: 'var(--rawbank-text-primary)',
              lineHeight: 1.1,
            }}
          >
            RAWBANK
          </span>

          {showBadge && (
            <span
              style={{
                color: 'var(--rawbank-yellow)',
                fontWeight: 700,
                fontSize: badgeSize,
                padding: '1px 6px',
                background: 'var(--rawbank-yellow-fill)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--rawbank-yellow-border)',
                letterSpacing: '0.05em',
                fontFamily: "'Montserrat', 'Inter', sans-serif",
              }}
            >
              SENTIENT
            </span>
          )}
        </div>

        {showSubtitle && (
          <div
            style={{
              fontSize: '10px',
              color: 'var(--rawbank-text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              fontWeight: 500,
              marginTop: '1px',
            }}
          >
            Fraud Operations & Forensic Intelligence • DRC
          </div>
        )}
      </div>
    </div>
  );
};
