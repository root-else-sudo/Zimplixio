import { useEffect, useState } from 'react';
import type { ReportData } from '../types/assessment';

interface Props {
  report: ReportData;
  onRestart: () => void;
}

const BADGE_CLASS: Record<string, string> = {
  early: 'badge-early',
  developing: 'badge-developing',
  ready: 'badge-ready',
};

const BADGE_LABEL: Record<string, string> = {
  early: 'Early Stage',
  developing: 'Developing',
  ready: 'Ready',
};

export function AssessmentReport({ report, onRestart }: Props) {
  const [visibleBlocks, setVisibleBlocks] = useState<number[]>([]);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    for (let i = 0; i < 5; i++) {
      timers.push(
        setTimeout(() => {
          setVisibleBlocks((prev) => [...prev, i]);
        }, i * 200)
      );
    }
    return () => timers.forEach(clearTimeout);
  }, []);

  function isVisible(i: number) {
    return visibleBlocks.includes(i);
  }

  return (
    <div id="report-output">
      {/* Block 0: Readiness level */}
      <div className={`report-block ${isVisible(0) ? 'visible' : ''}`}>
        <div className="flex items-center gap-4 mb-4">
          <span className={`readiness-badge ${BADGE_CLASS[report.readiness_level] ?? ''}`}>
            {BADGE_LABEL[report.readiness_level] ?? report.readiness_level}
          </span>
        </div>
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{report.readiness_summary}</p>
      </div>

      {/* Block 1: Priority stage */}
      <div className={`report-block ${isVisible(1) ? 'visible' : ''}`}>
        <h4 className="report-section-title">Your Priority Stage</h4>
        <p className="font-semibold text-indigo-700 dark:text-indigo-400 text-lg mb-2">{report.priority_stage.name}</p>
        <p className="text-gray-700 dark:text-gray-300">{report.priority_stage.reason}</p>
      </div>

      {/* Block 2: Top risks */}
      <div className={`report-block ${isVisible(2) ? 'visible' : ''}`}>
        <h4 className="report-section-title">Top Risks to Address</h4>
        <div className="risk-grid">
          {report.top_risks.map((risk, i) => (
            <div key={i} className="risk-card">
              <p className="font-semibold text-gray-900 dark:text-white mb-1">{risk.title}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{risk.detail}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Block 3: First 30 days */}
      <div className={`report-block ${isVisible(3) ? 'visible' : ''}`}>
        <h4 className="report-section-title">Your First 30 Days</h4>
        <ol className="first-30-list">
          {report.first_30_days.map((item, i) => (
            <li key={i} className="first-30-item">
              <span className="first-30-number">{i + 1}</span>
              <span>{item}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Block 4: Verdict */}
      <div className={`report-block ${isVisible(4) ? 'visible' : ''}`}>
        <div className="verdict-quote">
          <p>"{report.one_line_verdict}"</p>
        </div>
        <div className="flex gap-4 mt-8 justify-center flex-wrap">
          <button
            onClick={() => window.print()}
            className="bg-indigo-600 text-white font-semibold px-6 py-3 rounded-xl hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20"
          >
            Download PDF
          </button>
          <button
            onClick={onRestart}
            className="border-2 border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 font-semibold px-6 py-3 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
          >
            Start Over
          </button>
        </div>
      </div>
    </div>
  );
}
