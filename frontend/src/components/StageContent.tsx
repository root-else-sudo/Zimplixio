import type { Stage } from '../data/stages';
import { DualColumn } from './DualColumn';
import { Callout } from './Callout';
import { ComparisonTable } from './ComparisonTable';

interface StageContentProps {
  stage: Stage;
}

export function StageContent({ stage }: StageContentProps) {
  return (
    <div className="px-6 pb-6 pt-2 border-t border-gray-100">
      <p className="text-indigo-600 font-medium text-sm mb-4 italic">{stage.keyQuestion}</p>

      <div className="prose prose-gray max-w-none text-gray-700">
        <p className="mb-4">{stage.intro}</p>
      </div>

      <DualColumn left={stage.columns.left} right={stage.columns.right} />

      {stage.callouts.map((callout, i) => (
        <Callout key={i} callout={callout} />
      ))}

      {stage.tables?.map((table, i) => (
        <ComparisonTable key={i} table={table} />
      ))}
    </div>
  );
}
