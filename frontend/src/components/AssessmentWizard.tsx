import { useEffect, useState } from 'react';
import { QUESTIONS } from '../data/questions';
import type { ReportData } from '../types/assessment';
import { WizardQuestion } from './WizardQuestion';
import { LoadingScreen } from './LoadingScreen';
import { ContactForm } from './ContactForm';
import { AssessmentReport } from './AssessmentReport';

type Step = 'idle' | 'questions' | 'loading' | 'contact' | 'report' | 'error';
type Direction = 'forward' | 'back';

function getCsrf(): string {
  return (document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement)?.content ?? '';
}

export function AssessmentWizard() {
  const [step, setStep] = useState<Step>('idle');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [direction, setDirection] = useState<Direction>('forward');
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    function onStart() {
      setStep('questions');
      setCurrentQuestion(0);
      setDirection('forward');
      setAnswers({});
      setTimeout(() => {
        document.getElementById('assessment')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
    document.addEventListener('assessmentStart', onStart);
    return () => document.removeEventListener('assessmentStart', onStart);
  }, []);

  const q = QUESTIONS[currentQuestion];
  const currentAnswer = answers[q?.key ?? ''] ?? (q?.type === 'multi' ? [] : '');
  const canProceed =
    q?.type === 'single'
      ? typeof currentAnswer === 'string' && currentAnswer !== ''
      : Array.isArray(currentAnswer) && currentAnswer.length > 0;

  function handleAnswerChange(value: string | string[]) {
    setAnswers((prev) => ({ ...prev, [q.key]: value }));
  }

  function goBack() {
    if (currentQuestion > 0) {
      setDirection('back');
      setCurrentQuestion((i) => i - 1);
    }
  }

  async function goNext() {
    if (currentQuestion < QUESTIONS.length - 1) {
      setDirection('forward');
      setCurrentQuestion((i) => i + 1);
    } else {
      // Submit
      setStep('loading');
      try {
        const resp = await fetch('/framework/api/assessment/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrf(),
          },
          body: JSON.stringify({ answers }),
        });
        const data = await resp.json();
        if (!resp.ok) {
          setError(data.error ?? 'The assessment service is temporarily unavailable.');
          setStep('error');
          return;
        }
        setReport(data.report);
        setStep('contact');
      } catch {
        setError('Network error. Please check your connection and try again.');
        setStep('error');
      }
    }
  }

  function handleRestart() {
    setStep('questions');
    setCurrentQuestion(0);
    setDirection('forward');
    setAnswers({});
    setReport(null);
    setError('');
  }

  if (step === 'idle') return null;

  if (step === 'loading') {
    return <LoadingScreen />;
  }

  if (step === 'error') {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-2xl max-w-md mx-auto mb-6">
          {error}
        </div>
        <button
          onClick={handleRestart}
          className="bg-indigo-600 text-white font-semibold px-6 py-3 rounded-xl hover:bg-indigo-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (step === 'contact' && report) {
    return <ContactForm report={report} onSuccess={() => setStep('report')} />;
  }

  if (step === 'report' && report) {
    return <AssessmentReport report={report} onRestart={handleRestart} />;
  }

  // step === 'questions'
  const progress = ((currentQuestion) / QUESTIONS.length) * 100;

  return (
    <div className="assessment-wizard max-w-2xl mx-auto">
      {/* Step dots */}
      <div className="flex justify-center gap-2 mb-4">
        {QUESTIONS.map((_, i) => (
          <div
            key={i}
            className={`rounded-full transition-all duration-300 ${
              i < currentQuestion
                ? 'w-2.5 h-2.5 bg-indigo-600'
                : i === currentQuestion
                ? 'w-2.5 h-2.5 bg-indigo-600 ring-2 ring-indigo-300 ring-offset-1'
                : 'w-2.5 h-2.5 bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Question {currentQuestion + 1} of {QUESTIONS.length}</span>
          <span>{Math.round(progress)}% complete</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-600 rounded-full"
            style={{
              width: `${progress}%`,
              transition: 'width 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
            }}
          />
        </div>
      </div>

      {/* Question — key forces remount to trigger animation */}
      <WizardQuestion
        key={currentQuestion}
        question={q}
        answer={currentAnswer}
        onChange={handleAnswerChange}
        direction={direction}
      />

      {/* Navigation */}
      <div className="flex justify-between mt-8">
        <button
          onClick={goBack}
          disabled={currentQuestion === 0}
          className="px-6 py-3 rounded-xl border-2 border-gray-300 text-gray-600 font-medium hover:border-indigo-400 hover:text-indigo-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Back
        </button>
        <button
          onClick={goNext}
          disabled={!canProceed}
          className="px-6 py-3 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-indigo-600/20"
        >
          {currentQuestion === QUESTIONS.length - 1 ? 'Get My Report' : 'Next'}
        </button>
      </div>
    </div>
  );
}
