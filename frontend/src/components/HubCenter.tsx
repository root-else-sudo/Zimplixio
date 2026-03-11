interface HubCenterProps {
  cx: number;
  cy: number;
  r: number;
  idle: boolean;
}

export function HubCenter({ cx, cy, r, idle }: HubCenterProps) {
  return (
    <g>
      {/* Pulse ring */}
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke="#6366F1"
        strokeWidth={2}
        className={`hub-pulse-ring${idle ? '' : ' paused'}`}
      />
      {/* Solid hub */}
      <circle cx={cx} cy={cy} r={r} fill="#4F46E5" />
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        fill="white"
        fontFamily="'DM Serif Display', serif"
        fontSize={22}
        fontWeight={700}
      >
        AI
      </text>
    </g>
  );
}
