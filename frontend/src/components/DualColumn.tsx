import type { Column } from '../data/stages';

interface DualColumnProps {
  left: Column;
  right: Column;
}

export function DualColumn({ left, right }: DualColumnProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
      <div>
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">{left.heading}</h4>
        <ul className="list-disc pl-5 space-y-2 text-gray-700 dark:text-gray-300 text-sm">
          {left.items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
      <div>
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">{right.heading}</h4>
        <ul className="list-disc pl-5 space-y-2 text-gray-700 dark:text-gray-300 text-sm">
          {right.items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
