import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { Stage } from '../data/stages';
import { STAGE_ICONS } from './StageIcons';

interface StageData {
  stage: Stage;
  active: boolean;
  onToggle: (num: string) => void;
  label: string;
  entranceDelay: number;
  [key: string]: unknown;
}

const NODE_STEP: Record<string, string> = {
  '0': '01',
  '1': '02',
  '2': '03',
  '3': '04',
  'P': '05',
  'M': '06',
};

export function StageNode({ data }: NodeProps) {
  const { stage, active, onToggle, label, entranceDelay = 0 } = data as StageData;
  const isOngoing = stage.type === 'ongoing';
  const size = 152;

  const Icon = STAGE_ICONS[stage.number];
  const iconColor = active ? 'white' : '#60a5fa';
  const iconSize  = 72;

  // Color palette — deep navy inactive, electric blue active
  const accentColor   = 'rgba(37,99,235,';
  const inactiveBorder = '1.5px solid rgba(37,99,235,0.4)';
  const inactiveBg    = '#0f1628';
  const activeBg      = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';

  // Decorative ring dimensions — centered via top/left offset inside overflow:visible container
  const orbitSize = size + 16;
  const orbitOffset = -(orbitSize - size) / 2;   // negative = overflow outward
  const pulseSize = size + 26;
  const pulseOffset = -(pulseSize - size) / 2;

  return (
    <div style={{
      position: 'relative',
      width: size,
      height: size,
      overflow: 'visible',
      animation: 'nodeEnter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) both',
      animationDelay: `${entranceDelay}ms`,
    }}>

      {/* ── Pulse ring (inactive only) ── */}
      {!active && (
        <div
          className="stage-pulse-ring"
          style={{
            position: 'absolute',
            width: pulseSize,
            height: pulseSize,
            top: pulseOffset,
            left: pulseOffset,
            borderRadius: '50%',
            border: `1px solid ${accentColor}0.35)`,
            pointerEvents: 'none',
          }}
        />
      )}

      {/* ── Rotating orbit ring (inactive only) ── */}
      {!active && (
        <div
          className={isOngoing ? 'stage-orbit-ccw' : 'stage-orbit-cw'}
          style={{
            position: 'absolute',
            width: orbitSize,
            height: orbitSize,
            top: orbitOffset,
            left: orbitOffset,
            borderRadius: '50%',
            border: `1px dashed ${accentColor}0.3)`,
            pointerEvents: 'none',
          }}
        />
      )}

      {/* ── Active glow bloom ── */}
      {active && (
        <div style={{
          position: 'absolute',
          inset: -12,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${accentColor}0.28) 0%, transparent 70%)`,
          pointerEvents: 'none',
        }} />
      )}

      {/* ── Main circle ── */}
      <div
        className="stage-node-circle"
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          border: active ? 'none' : inactiveBorder,
          background: active ? activeBg : inactiveBg,
          boxShadow: active
            ? `0 0 20px ${accentColor}0.6), 0 4px 12px rgba(0,0,0,0.2)`
            : `0 0 12px ${accentColor}0.25), 0 4px 16px rgba(0,0,0,0.4)`,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          transform: active ? 'scale(1.1)' : 'scale(1)',
          position: 'relative',
          overflow: 'hidden',
        }}
        role="button"
        aria-pressed={active}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onToggle(stage.number);
          }
        }}
      >
        {/* Inner highlight (active only) */}
        {active && (
          <div style={{
            position: 'absolute',
            width: size * 0.6,
            height: size * 0.6,
            top: -size * 0.15,
            left: -size * 0.1,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%)',
            pointerEvents: 'none',
          }} />
        )}

        {/* Icon — floats gently when idle */}
        <div className={active ? undefined : 'stage-icon-float'}>
          {Icon && <Icon color={iconColor} size={iconSize} />}
        </div>

        {/* Number badge */}
        <span style={{
          fontSize: 22,
          fontFamily: 'DM Sans, ui-sans-serif, system-ui, sans-serif',
          fontWeight: 800,
          letterSpacing: '-0.02em',
          lineHeight: 1,
          color: active
            ? 'rgba(255,255,255,0.95)'
            : (isOngoing ? '#A78BFA' : '#60a5fa'),
        }}>
          {NODE_STEP[stage.number] ?? stage.number}
        </span>
      </div>

      {/* Label below */}
      <div style={{
        position: 'absolute',
        top: size + 7,
        left: '50%',
        transform: 'translateX(-50%)',
        whiteSpace: 'nowrap',
        fontSize: 16,
        fontFamily: 'DM Sans, sans-serif',
        fontWeight: active ? 700 : 600,
        color: active ? (isOngoing ? '#7C3AED' : '#2563eb') : '#6B7280',
        pointerEvents: 'none',
        letterSpacing: '0.01em',
      }}>
        {label}
      </div>

      {/* Invisible target handles on all 4 sides */}
      <Handle type="target" id="t" position={Position.Top}    style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
      <Handle type="target" id="r" position={Position.Right}  style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
      <Handle type="target" id="b" position={Position.Bottom} style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
      <Handle type="target" id="l" position={Position.Left}   style={{ opacity: 0, background: 'transparent', border: 'none', width: 1, height: 1 }} />
    </div>
  );
}
