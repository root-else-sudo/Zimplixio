import { useState, useEffect, useRef, useCallback } from 'react';
import { STAGES } from '../data/stages';
import { RadialHub } from './RadialHub';
import { StageContent } from './StageContent';

declare const AOS: { refresh: () => void } | undefined;

export function FrameworkAccordion() {
  const [openStage, setOpenStage] = useState<string | null>(null);
  const panelRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const panelContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (typeof AOS !== 'undefined') {
      AOS.refresh();
    }
  }, []);

  useEffect(() => {
    for (const stage of STAGES) {
      const el = panelRefs.current[stage.number];
      if (!el) continue;

      if (openStage === stage.number) {
        el.style.maxHeight = el.scrollHeight + 'px';
        el.style.opacity = '1';
      } else {
        el.style.maxHeight = '0px';
        el.style.opacity = '0';
      }
    }
  }, [openStage]);

  const handleToggle = useCallback((stageNumber: string) => {
    setOpenStage((prev) => {
      const next = prev === stageNumber ? null : stageNumber;
      // On mobile, scroll to content panel when opening
      if (next !== null && window.innerWidth < 640) {
        requestAnimationFrame(() => {
          panelContainerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
      }
      return next;
    });
  }, []);

  return (
    <div>
      {/* Radial hub-and-spoke diagram */}
      <RadialHub activeStage={openStage} onToggle={handleToggle} />

      {/* Content panels — all always rendered in DOM, only active one is visible */}
      <div ref={panelContainerRef}>
        {STAGES.map((stage) => (
          <div
            key={stage.number}
            ref={(el) => { panelRefs.current[stage.number] = el; }}
            className="overflow-hidden"
            style={{
              maxHeight: 0,
              opacity: 0,
              transition: 'max-height 0.4s ease-out, opacity 0.3s ease-out',
            }}
          >
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
              <StageContent stage={stage} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
