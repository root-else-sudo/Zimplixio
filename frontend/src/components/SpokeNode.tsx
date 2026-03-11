interface SpokeNodeProps {
  cx: number;
  cy: number;
  r: number;
  number: string;
  label: string;
  ongoing: boolean;
  active: boolean;
  onClick: () => void;
}

export function SpokeNode({ cx, cy, r, number, label, ongoing, active, onClick }: SpokeNodeProps) {
  const labelY = cy + r + 16;

  return (
    <g
      className={`spoke-node${active ? ' active' : ''}`}
      style={{ transformOrigin: `${cx}px ${cy}px` }}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      role="button"
      tabIndex={0}
      aria-pressed={active}
      aria-label={`Stage ${number}: ${label}`}
    >
      {/* Node circle */}
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill={active ? '#4F46E5' : 'white'}
        stroke={active ? '#4F46E5' : '#D1D5DB'}
        strokeWidth={2}
        className={`node-circle${ongoing ? ' ongoing' : ''}${active ? ' active' : ''}`}
      />
      {/* Number */}
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        className={`node-number${active ? ' active' : ''}`}
      >
        {number}
      </text>
      {/* Label */}
      <text
        x={cx}
        y={labelY}
        textAnchor="middle"
        className={`node-label${active ? ' active' : ''}`}
      >
        {label}
      </text>
    </g>
  );
}
