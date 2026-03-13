import { useState, useCallback, useEffect } from 'react';
import { STAGES } from '../data/stages';
import { FlowHub } from './FlowHub';
import { StageModal } from './StageModal';

declare const AOS: { refresh: () => void } | undefined;

export function FrameworkAccordion() {
  const [openStage, setOpenStage] = useState<string | null>(null);

  useEffect(() => {
    if (typeof AOS !== 'undefined') {
      AOS.refresh();
    }
  }, []);

  const handleToggle = useCallback((stageNumber: string) => {
    setOpenStage((prev) => (prev === stageNumber ? null : stageNumber));
  }, []);

  return (
    <div>
      <FlowHub activeStage={openStage} onToggle={handleToggle} />
      <StageModal
        stage={openStage ? STAGES.find((s) => s.number === openStage) ?? null : null}
        onClose={() => setOpenStage(null)}
      />
    </div>
  );
}
