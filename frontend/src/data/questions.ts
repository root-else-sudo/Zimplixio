export interface Question {
  key: string;
  text: string;
  type: 'single' | 'multi';
  options: string[];
  maxSelect?: number;
}

export const QUESTIONS: Question[] = [
  {
    key: 'industry',
    text: 'What industry or sector best describes your business?',
    type: 'single',
    options: [
      'Professional Services (consulting, legal, accounting)',
      'Healthcare or Life Sciences',
      'Financial Services or Insurance',
      'Retail or E-commerce',
      'Manufacturing or Logistics',
      'Technology or Software',
      'Education or Non-profit',
      'Other',
    ],
  },
  {
    key: 'size',
    text: 'How many people work at your company?',
    type: 'single',
    options: [
      '1–10 (solo or micro)',
      '11–50 (small)',
      '51–200 (mid-size)',
      '201–500',
      '500+',
    ],
  },
  {
    key: 'ai_usage',
    text: 'How is AI currently used in your business?',
    type: 'single',
    options: [
      'Not at all — we have not started',
      'Experimenting informally (staff using ChatGPT, etc.)',
      'A few approved tools in limited departments',
      'Structured pilots with defined goals',
      'AI is embedded in multiple workflows',
    ],
  },
  {
    key: 'data_readiness',
    text: 'How would you describe the state of your business data?',
    type: 'single',
    options: [
      'Scattered across spreadsheets, emails, and siloed systems',
      'Mostly centralised but not consistently structured',
      'Clean and structured in one or more core systems',
      'Well-governed, documented, and API-accessible',
    ],
  },
  {
    key: 'leadership',
    text: 'How does leadership view AI adoption?',
    type: 'single',
    options: [
      'Skeptical or unaware',
      'Interested but waiting for proof',
      'Supportive — actively asking for a plan',
      'Fully committed with budget allocated',
    ],
  },
  {
    key: 'goals',
    text: 'What are your primary goals for adopting AI? (select all that apply)',
    type: 'multi',
    options: [
      'Reduce operational costs',
      'Improve customer experience',
      'Speed up internal processes',
      'Unlock new revenue streams',
      'Improve decision-making with data',
      'Stay competitive in the market',
      'Reduce manual or repetitive work',
    ],
  },
  {
    key: 'concerns',
    text: 'What concerns you most about AI adoption? (select up to 3)',
    type: 'multi',
    maxSelect: 3,
    options: [
      'Data privacy and security',
      'Integration with existing systems',
      'Cost and ROI uncertainty',
      'Lack of internal AI skills',
      'Resistance from staff',
      'Regulatory or compliance risk',
      'Not knowing where to start',
      'Quality and reliability of AI outputs',
    ],
  },
  {
    key: 'timeline',
    text: 'What is your expected timeline for meaningful AI adoption?',
    type: 'single',
    options: [
      'Immediate — we need wins in 30–60 days',
      'Short term — 3 to 6 months',
      'Medium term — 6 to 12 months',
      'Long term — 1 to 2 years',
      'No specific timeline yet',
    ],
  },
];
