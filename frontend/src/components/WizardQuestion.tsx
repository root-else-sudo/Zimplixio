import type { Question } from '../data/questions';

interface Props {
  question: Question;
  answer: string | string[];
  onChange: (value: string | string[]) => void;
  direction?: 'forward' | 'back';
}

export function WizardQuestion({ question, answer, onChange, direction = 'forward' }: Props) {
  const selected = Array.isArray(answer) ? answer : answer ? [answer] : [];

  function toggle(option: string) {
    if (question.type === 'single') {
      onChange(option);
    } else {
      if (selected.includes(option)) {
        onChange(selected.filter((v) => v !== option));
      } else {
        const max = question.maxSelect ?? Infinity;
        if (selected.length < max) {
          onChange([...selected, option]);
        }
      }
    }
  }

  return (
    <div className={direction === 'back' ? 'question-slide-back' : 'question-slide'}>
      <p className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-6">{question.text}</p>
      {question.type === 'multi' && (
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          {question.maxSelect
            ? `Select up to ${question.maxSelect}`
            : 'Select all that apply'}
        </p>
      )}
      <div className="space-y-3">
        {question.options.map((option) => {
          const isSelected = selected.includes(option);
          return (
            <button
              key={option}
              type="button"
              className={`assessment-option w-full text-left px-4 py-3 rounded-xl border-2 transition-all ${
                isSelected
                  ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-900/40 text-indigo-900 dark:text-indigo-200 font-medium'
                  : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:border-indigo-300 dark:hover:border-indigo-500'
              }`}
              onClick={() => toggle(option)}
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}
