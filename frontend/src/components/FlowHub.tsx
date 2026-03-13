import { ReactFlow, type Node, type Edge, type EdgeTypes } from '@xyflow/react';
import { STAGES } from '../data/stages';
import { HubNode } from './HubNode';
import { StageNode } from './StageNode';
import { GradientEdge } from './GradientEdge';

interface FlowHubProps {
  activeStage: string | null;
  onToggle: (stageNumber: string) => void;
}

const ORBIT_R = 265;

// 6 nodes evenly distributed — 60° apart, Stage 0 at 12 o'clock, clockwise
const ANGLES: Record<string, number> = {
  '0':   0,   // 12 o'clock
  '1':  60,   //  2 o'clock
  '2': 120,   //  4 o'clock
  '3': 180,   //  6 o'clock
  'P': 240,   //  8 o'clock
  'M': 300,   // 10 o'clock
};

const SHORT_LABELS: Record<string, string> = {
  '0': 'Readiness',
  '1': 'Workflows',
  '2': 'Governance',
  '3': 'Data',
  'P': 'People',
  'M': 'ROI',
};

// Staggered entrance delays: hub first, then each stage 500ms apart
const NODE_DELAYS: Record<string, number> = {
  hub: 200,
  '0':  700,
  '1': 1200,
  '2': 1700,
  '3': 2200,
  'P': 2700,
  'M': 3200,
};

// Edges appear 200ms after their target node
const EDGE_DELAYS: Record<string, number> = {
  '0':  900,
  '1': 1400,
  '2': 1900,
  '3': 2400,
  'P': 2900,
  'M': 3400,
};

function degToRad(deg: number) {
  return (deg * Math.PI) / 180;
}

function nodePos(angleDeg: number) {
  const rad = degToRad(angleDeg - 90);
  return {
    x: ORBIT_R * Math.cos(rad),
    y: ORBIT_R * Math.sin(rad),
  };
}

const nodeTypes = { hubNode: HubNode, stageNode: StageNode };
const edgeTypes: EdgeTypes = { gradientEdge: GradientEdge };

export function FlowHub({ activeStage, onToggle }: FlowHubProps) {
  const nodes: Node[] = [
    {
      id: 'hub',
      type: 'hubNode',
      position: { x: 0, y: 0 },
      data: {
        idle: activeStage === null,
        entranceDelay: NODE_DELAYS.hub,
      },
    },
    ...STAGES.map((stage) => ({
      id: stage.number,
      type: 'stageNode',
      position: nodePos(ANGLES[stage.number] ?? 0),
      data: {
        stage,
        active: activeStage === stage.number,
        onToggle,
        label: SHORT_LABELS[stage.number] ?? stage.name,
        entranceDelay: NODE_DELAYS[stage.number] ?? 400,
      },
    })),
  ];

  const edges: Edge[] = STAGES.map((stage) => ({
    id: `hub-${stage.number}`,
    source: 'hub',
    target: stage.number,
    type: 'gradientEdge',
    animated: activeStage === stage.number,
    data: { entranceDelay: EDGE_DELAYS[stage.number] ?? 600 },
  }));

  return (
    <div style={{ width: '100%', height: 760, marginBottom: '2rem' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.08, maxZoom: 1 }}
        onNodeClick={(_event, node) => {
          if (node.id !== 'hub') onToggle(node.id);
        }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={false}
        zoomOnScroll={false}
        zoomOnPinch={false}
        zoomOnDoubleClick={false}
        preventScrolling={false}
        proOptions={{ hideAttribution: true }}
        nodeOrigin={[0.5, 0.5]}
        style={{ background: 'transparent' }}
      />
    </div>
  );
}
