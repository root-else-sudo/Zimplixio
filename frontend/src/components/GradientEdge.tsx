import { getStraightPath, type EdgeProps } from '@xyflow/react';

export function GradientEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  animated,
  data,
}: EdgeProps) {
  const [edgePath] = getStraightPath({ sourceX, sourceY, targetX, targetY });
  const glowId = `glow-${id}`;
  const entranceDelay = (data as { entranceDelay?: number })?.entranceDelay ?? 0;

  return (
    <>
      {animated && (
        <defs>
          <filter id={glowId} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      )}

      {/* Entrance fade-in group */}
      <g style={{
        animation: 'edgeEnter 0.7s ease-out both',
        animationDelay: `${entranceDelay}ms`,
      }}>
        {/* Dots only — no base line */}
        <path
          d={edgePath}
          fill="none"
          stroke={animated ? 'rgba(37,99,235,0.95)' : 'rgba(29,78,216,0.7)'}
          strokeWidth={animated ? 4 : 3}
          strokeDasharray={animated ? '2 11' : '2 16'}
          strokeLinecap="round"
          filter={animated ? `url(#${glowId})` : undefined}
          style={{
            animation: `dashdraw ${animated ? '0.7s' : '2.8s'} linear infinite`,
          }}
        />
      </g>
    </>
  );
}
