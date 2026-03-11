import { useRef, useEffect, useState } from 'react';

interface SpokeLineProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  index: number;
  active: boolean;
}

export function SpokeLine({ x1, y1, x2, y2, index, active }: SpokeLineProps) {
  const ref = useRef<SVGLineElement>(null);
  const [len, setLen] = useState(200);

  useEffect(() => {
    if (ref.current) {
      const dx = x2 - x1;
      const dy = y2 - y1;
      setLen(Math.sqrt(dx * dx + dy * dy));
    }
  }, [x1, y1, x2, y2]);

  return (
    <line
      ref={ref}
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={active ? '#4F46E5' : '#D1D5DB'}
      strokeWidth={active ? 2.5 : 1.5}
      className={`spoke-line${active ? ' active' : ''}`}
      style={{
        '--spoke-len': `${len}`,
        animationDelay: `${index * 100}ms`,
      } as React.CSSProperties}
    />
  );
}
