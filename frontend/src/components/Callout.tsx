import type { Callout as CalloutType } from '../data/stages';

interface CalloutProps {
  callout: CalloutType;
}

export function Callout({ callout }: CalloutProps) {
  return (
    <div className="framework-callout">
      <div className="framework-callout-label">{callout.label}</div>
      <p className="text-gray-700 text-sm leading-relaxed">{callout.text}</p>
    </div>
  );
}
