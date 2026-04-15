interface IconProps {
  color?: string;
  size?: number;
}

function deriveColors(color: string) {
  const isActive = color === 'white';
  return {
    primary:   color,
    secondary: isActive ? 'rgba(255,255,255,0.65)' : '#60a5fa',
    accent:    isActive ? 'rgba(255,255,255,0.45)' : '#06b6d4',
    fill:      isActive ? 'rgba(255,255,255,0.10)' : 'rgba(37,99,235,0.09)',
  };
}

// ── 01 Readiness — circuit clipboard with scan line ──────────────────────────
export function IconReadiness({ color = 'currentColor', size = 36 }: IconProps) {
  const { primary, secondary, accent, fill } = deriveColors(color);
  return (
    <svg viewBox="0 0 36 36" width={size} height={size} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Clipboard body */}
      <rect x="8" y="5" width="20" height="26" rx="2" stroke={primary} strokeWidth="1.2" fill={fill} />
      {/* Clipboard tab */}
      <rect x="13" y="3" width="10" height="4" rx="1" stroke={primary} strokeWidth="1.2" fill="none" />
      {/* Circuit traces */}
      <line x1="12" y1="13" x2="16" y2="13" stroke={secondary} strokeWidth="1" className="icon-trace" />
      <circle cx="17.5" cy="13" r="1.5" fill="none" stroke={secondary} strokeWidth="1" className="icon-trace-dot" />
      <line x1="19" y1="13" x2="24" y2="13" stroke={secondary} strokeWidth="1" className="icon-trace" />
      <line x1="17.5" y1="14.5" x2="17.5" y2="17" stroke={secondary} strokeWidth="1" className="icon-trace" />
      <line x1="12" y1="18" x2="15" y2="18" stroke={secondary} strokeWidth="1" className="icon-trace" />
      <line x1="15" y1="17" x2="15" y2="19" stroke={secondary} strokeWidth="1" />
      <line x1="17.5" y1="17" x2="24" y2="17" stroke={secondary} strokeWidth="1" className="icon-trace" />
      {/* Scan line */}
      <line x1="10" y1="22" x2="26" y2="22" stroke={accent} strokeWidth="1.5" strokeDasharray="2 2" className="icon-scan-line" />
      <line x1="12" y1="25" x2="20" y2="25" stroke={primary} strokeWidth="1" opacity="0.35" />
    </svg>
  );
}

// ── 02 Workflows — branching pipeline ────────────────────────────────────────
export function IconWorkflows({ color = 'currentColor', size = 36 }: IconProps) {
  const { primary, secondary, accent, fill } = deriveColors(color);
  return (
    <svg viewBox="0 0 36 36" width={size} height={size} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Root node */}
      <circle cx="18" cy="7" r="3" stroke={primary} strokeWidth="1.2" fill={fill} />
      {/* Branch lines */}
      <line x1="18" y1="10" x2="18" y2="14" stroke={primary} strokeWidth="1.2" />
      <line x1="18" y1="14" x2="10" y2="18" stroke={primary} strokeWidth="1.2" />
      <line x1="18" y1="14" x2="26" y2="18" stroke={primary} strokeWidth="1.2" />
      {/* Mid nodes */}
      <circle cx="10" cy="19" r="2.5" stroke={secondary} strokeWidth="1.2" fill="none" className="icon-flow-node" />
      <circle cx="26" cy="19" r="2.5" stroke={secondary} strokeWidth="1.2" fill="none" className="icon-flow-node" />
      {/* Second branch */}
      <line x1="10" y1="21.5" x2="10" y2="25" stroke={secondary} strokeWidth="1" />
      <line x1="26" y1="21.5" x2="26" y2="25" stroke={secondary} strokeWidth="1" />
      <line x1="10" y1="25" x2="14" y2="29" stroke={secondary} strokeWidth="1" />
      <line x1="26" y1="25" x2="22" y2="29" stroke={secondary} strokeWidth="1" />
      {/* Leaf node */}
      <rect x="12" y="28" width="12" height="5" rx="1" stroke={accent} strokeWidth="1" fill="none" className="icon-leaf" />
    </svg>
  );
}

// ── 03 Governance — shield with circuit grid ─────────────────────────────────
export function IconGovernance({ color = 'currentColor', size = 36 }: IconProps) {
  const { primary, secondary, fill } = deriveColors(color);
  return (
    <svg viewBox="0 0 36 36" width={size} height={size} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Shield */}
      <path d="M18 4 L28 8 L28 18 C28 24 18 32 18 32 C18 32 8 24 8 18 L8 8 Z"
        stroke={primary} strokeWidth="1.3" fill={fill} />
      {/* Circuit grid */}
      <line x1="13" y1="14" x2="23" y2="14" stroke={secondary} strokeWidth="0.8" opacity="0.7" className="icon-trace" />
      <line x1="13" y1="18" x2="23" y2="18" stroke={secondary} strokeWidth="0.8" opacity="0.7" className="icon-trace" />
      <line x1="13" y1="22" x2="21" y2="22" stroke={secondary} strokeWidth="0.8" opacity="0.45" className="icon-trace" />
      <line x1="13" y1="14" x2="13" y2="22" stroke={secondary} strokeWidth="0.8" opacity="0.7" className="icon-trace" />
      <line x1="18" y1="14" x2="18" y2="22" stroke={secondary} strokeWidth="0.8" opacity="0.7" className="icon-trace" />
      <line x1="23" y1="14" x2="23" y2="18" stroke={secondary} strokeWidth="0.8" opacity="0.7" className="icon-trace" />
      {/* Junction dots */}
      <circle cx="13" cy="14" r="1.2" fill={primary} className="icon-trace-dot" />
      <circle cx="18" cy="14" r="1.2" fill={primary} className="icon-trace-dot" />
      <circle cx="23" cy="14" r="1.2" fill={primary} className="icon-trace-dot" />
      <circle cx="13" cy="18" r="1.2" fill={secondary} className="icon-trace-dot" />
      <circle cx="18" cy="18" r="1.2" fill={secondary} className="icon-trace-dot" />
      <circle cx="23" cy="18" r="1.2" fill={secondary} className="icon-trace-dot" />
    </svg>
  );
}

// ── 04 Data Protection — lock with data streams ──────────────────────────────
export function IconDataProtection({ color = 'currentColor', size = 36 }: IconProps) {
  const { primary, secondary, accent, fill } = deriveColors(color);
  return (
    <svg viewBox="0 0 36 36" width={size} height={size} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Lock body */}
      <rect x="10" y="18" width="16" height="13" rx="2" stroke={primary} strokeWidth="1.3" fill={fill} />
      {/* Lock shackle */}
      <path d="M13 18 L13 13 C13 10 23 10 23 13 L23 18" stroke={primary} strokeWidth="1.3" />
      {/* Keyhole */}
      <circle cx="18" cy="24" r="2.5" stroke={secondary} strokeWidth="1.2" fill="none" className="icon-keyhole" />
      <line x1="18" y1="26.5" x2="18" y2="29" stroke={secondary} strokeWidth="1.2" className="icon-keyhole" />
      {/* Data streams — left */}
      <line x1="5" y1="20" x2="9" y2="20" stroke={accent} strokeWidth="1" strokeDasharray="1.5 1.5" className="icon-data-stream" opacity="0.8" />
      <line x1="5" y1="23" x2="9" y2="23" stroke={accent} strokeWidth="1" strokeDasharray="1.5 1.5" className="icon-data-stream" opacity="0.55" />
      <line x1="5" y1="26" x2="9" y2="26" stroke={accent} strokeWidth="1" strokeDasharray="1.5 1.5" className="icon-data-stream" opacity="0.3" />
      {/* Data streams — right */}
      <line x1="27" y1="20" x2="31" y2="20" stroke={accent} strokeWidth="1" strokeDasharray="1.5 1.5" className="icon-data-stream" opacity="0.8" />
      <line x1="27" y1="23" x2="31" y2="23" stroke={accent} strokeWidth="1" strokeDasharray="1.5 1.5" className="icon-data-stream" opacity="0.55" />
      <line x1="27" y1="26" x2="31" y2="26" stroke={accent} strokeWidth="1" strokeDasharray="1.5 1.5" className="icon-data-stream" opacity="0.3" />
    </svg>
  );
}

// ── 05 People — network of person nodes ──────────────────────────────────────
export function IconPeople({ color = 'currentColor', size = 36 }: IconProps) {
  const { primary, secondary, accent, fill } = deriveColors(color);
  return (
    <svg viewBox="0 0 36 36" width={size} height={size} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Center person */}
      <circle cx="18" cy="11" r="3.5" stroke={primary} strokeWidth="1.3" fill={fill} />
      <path d="M11 24 C11 19 25 19 25 24" stroke={primary} strokeWidth="1.3" />
      {/* Left person */}
      <circle cx="8" cy="16" r="2.5" stroke={secondary} strokeWidth="1" fill="none" className="icon-person-node" />
      <path d="M4 26 C4 22.5 12 22.5 12 26" stroke={secondary} strokeWidth="1" />
      {/* Right person */}
      <circle cx="28" cy="16" r="2.5" stroke={secondary} strokeWidth="1" fill="none" className="icon-person-node" />
      <path d="M24 26 C24 22.5 32 22.5 32 26" stroke={secondary} strokeWidth="1" />
      {/* Connection dashes */}
      <line x1="11" y1="13" x2="14.5" y2="11.5" stroke={accent} strokeWidth="0.8" strokeDasharray="2 2" className="icon-connection" />
      <line x1="25" y1="13" x2="21.5" y2="11.5" stroke={accent} strokeWidth="0.8" strokeDasharray="2 2" className="icon-connection" />
    </svg>
  );
}

// ── 06 ROI — ascending columns with spark line ───────────────────────────────
export function IconROI({ color = 'currentColor', size = 36 }: IconProps) {
  const { primary, secondary, accent, fill } = deriveColors(color);
  return (
    <svg viewBox="0 0 36 36" width={size} height={size} fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Baseline */}
      <line x1="5" y1="29" x2="31" y2="29" stroke={secondary} strokeWidth="0.8" opacity="0.35" />
      {/* Left column (short) */}
      <rect x="7" y="22" width="6" height="7" rx="1" fill={fill} stroke={secondary} strokeWidth="0.9" className="icon-flow-node" />
      {/* Middle column (medium) */}
      <rect x="15" y="17" width="6" height="12" rx="1" fill={fill} stroke={secondary} strokeWidth="0.9" className="icon-flow-node" />
      {/* Right column (tall) — accent stroke to highlight peak */}
      <rect x="23" y="10" width="6" height="19" rx="1" fill={fill} stroke={accent} strokeWidth="0.9" className="icon-leaf" />
      {/* Spark line connecting column peaks */}
      <polyline points="10,22 18,17 26,10" fill="none" stroke={accent} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="icon-trend-line" />
      {/* Peak dots */}
      <circle cx="10" cy="22" r="1.5" fill={secondary} className="icon-trace-dot" />
      <circle cx="18" cy="17" r="1.5" fill={secondary} className="icon-trace-dot" />
      <circle cx="26" cy="10" r="2" fill={primary} className="icon-trace-dot" />
      {/* Upward arrow from tallest peak */}
      <line x1="26" y1="10" x2="26" y2="6" stroke={primary} strokeWidth="1.2" strokeLinecap="round" className="icon-data-point" />
      <polyline points="23.5,8 26,6 28.5,8" fill="none" stroke={primary} strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" className="icon-data-point" />
    </svg>
  );
}

export const STAGE_ICONS: Record<string, React.ComponentType<IconProps>> = {
  '0': IconReadiness,
  '1': IconWorkflows,
  '2': IconGovernance,
  '3': IconDataProtection,
  'P': IconPeople,
  'M': IconROI,
};
