import { useEffect, useState } from 'react';

const STAGES = [
  'Analysing your responses…',
  'Mapping to framework stages…',
  'Identifying readiness level…',
  'Evaluating key risk areas…',
  'Drafting your 30-day plan…',
  'Generating your AI roadmap…',
];

export function LoadingScreen() {
  const [visible, setVisible] = useState<number[]>([]);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    STAGES.forEach((_, i) => {
      timers.push(
        setTimeout(() => {
          setVisible((prev) => [...prev, i]);
        }, i * 400)
      );
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="loading-container text-center py-12">
      <div className="loading-spinner mx-auto mb-8" />
      <div className="space-y-3 max-w-sm mx-auto">
        {STAGES.map((label, i) => (
          <div
            key={i}
            className={`loading-stage ${visible.includes(i) ? 'visible' : ''}`}
          >
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}
