import { Handle, Position, type NodeProps } from '@xyflow/react';

interface HubData {
  idle: boolean;
  entranceDelay: number;
  [key: string]: unknown;
}

const HUB = 178; // measured container size (React Flow uses this for handle placement)

// Centers a decorative element of `size` within the HUB container
function centered(size: number): React.CSSProperties {
  const offset = (HUB - size) / 2;
  return {
    position: 'absolute',
    width: size,
    height: size,
    top: offset,
    left: offset,
    borderRadius: '50%',
    pointerEvents: 'none',
  };
}

export function HubNode({ data }: NodeProps) {
  const { idle, entranceDelay = 0 } = data as HubData;
  const paused = !idle;

  return (
    <div style={{
      position: 'relative',
      width: HUB,
      height: HUB,
      overflow: 'visible',
      animation: 'nodeEnter 0.9s cubic-bezier(0.34, 1.56, 0.64, 1) both',
      animationDelay: `${entranceDelay}ms`,
    }}>

      {/* ── Layer 1: Soft ambient glow bloom ── */}
      <div style={{
        ...centered(420),
        background: 'radial-gradient(circle, rgba(99,102,241,0.18) 0%, rgba(99,102,241,0.06) 45%, transparent 70%)',
      }} />

      {/* ── Layer 2: Rotating dashed orbit ring ── */}
      <div className="hub-orbit-ring" style={{
        ...centered(270),
        border: '1px dashed rgba(129,140,248,0.45)',
      }} />

      {/* ── Layer 3: Static inner accent ring ── */}
      <div style={{
        ...centered(212),
        border: '1px solid rgba(99,102,241,0.18)',
      }} />

      {/* ── Layer 4: Three staggered pulse rings ── */}
      {([0, -850, -1700] as const).map((delay, i) => (
        <div
          key={i}
          className={`hub-pulse-ring${paused ? ' paused' : ''}`}
          style={{
            ...centered(236),
            border: '1.5px solid rgba(99,102,241,0.4)',
            animationDelay: `${delay}ms`,
          }}
        />
      ))}

      {/* ── Layer 5: Main circle ── */}
      <div style={{
        ...centered(HUB),
        background: 'linear-gradient(135deg, #818CF8 0%, #4F46E5 45%, #3730A3 100%)',
        boxShadow: [
          '0 0 0 1px rgba(255,255,255,0.1) inset',
          '0 0 40px rgba(79,70,229,0.55)',
          '0 0 90px rgba(99,102,241,0.2)',
        ].join(', '),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1,
        overflow: 'hidden',
      }}>
        {/* Inner highlight spot */}
        <div style={{
          position: 'absolute',
          width: 107,
          height: 107,
          top: -17,
          left: -17,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.22) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        {/* "AI" text */}
        <span style={{
          color: 'white',
          fontFamily: 'DM Serif Display, serif',
          fontStyle: 'italic',
          fontSize: 52,
          lineHeight: 1,
          letterSpacing: '-0.5px',
          position: 'relative',
          zIndex: 1,
        }}>
          AI
        </span>

        {/* Divider */}
        <div style={{
          width: 42,
          height: 1,
          background: 'rgba(255,255,255,0.3)',
          margin: '6px 0 4px',
        }} />

        {/* "Hub" subtitle */}
        <span style={{
          color: 'rgba(255,255,255,0.6)',
          fontFamily: 'DM Sans, sans-serif',
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: '0.18em',
          textTransform: 'uppercase',
          position: 'relative',
          zIndex: 1,
        }}>
          Hub
        </span>
      </div>

      {/* ── Invisible source handles on all 4 sides ── */}
      <Handle type="source" id="t" position={Position.Top}    style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
      <Handle type="source" id="r" position={Position.Right}  style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
      <Handle type="source" id="b" position={Position.Bottom} style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
      <Handle type="source" id="l" position={Position.Left}   style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
    </div>
  );
}
