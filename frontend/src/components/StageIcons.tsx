// SVG icon for each stage — 24×24 viewBox, stroke-based, strokeWidth 1.75
interface IconProps {
  color?: string;
  size?: number;
}

const base = (size: number, color: string) => ({
  width: size,
  height: size,
  display: 'block' as const,
  flexShrink: 0,
  stroke: color,
  fill: 'none',
  strokeWidth: 1.75,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
});

export function IconReadiness({ color = 'currentColor', size = 22 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" style={base(size, color)}>
      <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
      <rect x="9" y="3" width="6" height="4" rx="1" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

export function IconWorkflows({ color = 'currentColor', size = 22 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" style={base(size, color)}>
      <rect x="3" y="3" width="5" height="5" rx="1" />
      <rect x="16" y="3" width="5" height="5" rx="1" />
      <rect x="9.5" y="15.5" width="5" height="5" rx="1" />
      <path d="M5.5 8v3h13V8" />
      <path d="M12 11v4.5" />
    </svg>
  );
}

export function IconGovernance({ color = 'currentColor', size = 22 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" style={base(size, color)}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

export function IconDataProtection({ color = 'currentColor', size = 22 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" style={base(size, color)}>
      <rect x="5" y="11" width="14" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
      <circle cx="12" cy="16" r="1" fill={color} stroke="none" />
    </svg>
  );
}

export function IconPeople({ color = 'currentColor', size = 22 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" style={base(size, color)}>
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

export function IconROI({ color = 'currentColor', size = 22 }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" style={base(size, color)}>
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
      <polyline points="16 7 22 7 22 13" />
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
