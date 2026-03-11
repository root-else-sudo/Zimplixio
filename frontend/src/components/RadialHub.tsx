import { STAGES } from '../data/stages';
import { useIsMobile } from '../hooks/useIsMobile';
import { HubCenter } from './HubCenter';
import { SpokeLine } from './SpokeLine';
import { SpokeNode } from './SpokeNode';

interface RadialHubProps {
  activeStage: string | null;
  onToggle: (stageNumber: string) => void;
}

/* Layout constants */
const CX = 300;
const CY = 300;
const HUB_R = 48;
const ORBIT_R = 200;
const STEP_R = 36;
const ONGOING_R = 32;

/* Node angles (degrees, clockwise from 12 o'clock) */
const ANGLES: Record<string, number> = {
  '0': -60,
  '1': -20,
  '2': 20,
  '3': 60,
  'P': 150,
  'M': 210,
};

/* Short labels for mobile */
const SHORT_LABELS: Record<string, string> = {
  '0': 'Readiness',
  '1': 'Workflows',
  '2': 'Governance',
  '3': 'Data',
  'P': 'People',
  'M': 'ROI',
};

function degToRad(deg: number) {
  return (deg * Math.PI) / 180;
}

function nodePos(angleDeg: number) {
  // 0° = 12 o'clock, clockwise
  const rad = degToRad(angleDeg - 90);
  return {
    x: CX + ORBIT_R * Math.cos(rad),
    y: CY + ORBIT_R * Math.sin(rad),
  };
}

export function RadialHub({ activeStage, onToggle }: RadialHubProps) {
  const isMobile = useIsMobile();

  return (
    <div className="flex justify-center mb-8">
      <svg
        viewBox="0 0 600 600"
        width="100%"
        style={{ maxWidth: 600 }}
        role="group"
        aria-label="AI Adoption Framework stages"
      >
        {/* Glow filter for active nodes */}
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Spoke lines (render behind nodes) */}
        {STAGES.map((stage, i) => {
          const angle = ANGLES[stage.number];
          if (angle === undefined) return null;
          const pos = nodePos(angle);
          return (
            <SpokeLine
              key={`spoke-${stage.number}`}
              x1={CX}
              y1={CY}
              x2={pos.x}
              y2={pos.y}
              index={i}
              active={activeStage === stage.number}
            />
          );
        })}

        {/* Central hub */}
        <HubCenter cx={CX} cy={CY} r={HUB_R} idle={activeStage === null} />

        {/* Orbit nodes */}
        {STAGES.map((stage) => {
          const angle = ANGLES[stage.number];
          if (angle === undefined) return null;
          const pos = nodePos(angle);
          const isOngoing = stage.type === 'ongoing';
          const r = isOngoing ? ONGOING_R : STEP_R;
          const label = isMobile ? SHORT_LABELS[stage.number] ?? stage.name : SHORT_LABELS[stage.number] ?? stage.name;
          return (
            <SpokeNode
              key={`node-${stage.number}`}
              cx={pos.x}
              cy={pos.y}
              r={r}
              number={stage.number}
              label={label}
              ongoing={isOngoing}
              active={activeStage === stage.number}
              onClick={() => onToggle(stage.number)}
            />
          );
        })}
      </svg>
    </div>
  );
}
