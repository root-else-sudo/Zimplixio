export interface Column {
  heading: string;
  items: string[];
}

export interface Callout {
  label: string;
  text: string;
}

export interface Table {
  title: string;
  headers: string[];
  rows: string[][];
}

export interface Stage {
  number: string;
  name: string;
  type: 'step' | 'ongoing';
  keyQuestion: string;
  subtitle: string;
  intro: string;
  columns: {
    left: Column;
    right: Column;
  };
  callouts: Callout[];
  tables?: Table[];
}

export const STAGES: Stage[] = [
  {
    number: '0',
    name: 'AI Readiness Assessment',
    type: 'step',
    keyQuestion: 'Is the organization ready to adopt AI responsibly?',
    subtitle: 'Before you invest, know what you are investing into',
    intro:
      'This step is often skipped — and its absence is the most common reason AI pilots fail. ' +
      'The assessment is not about gatekeeping; it is about honest scoping. Before committing budget ' +
      'to any AI initiative, you need a clear-eyed view of where the organization actually stands — ' +
      'not where leadership hopes it stands.',
    columns: {
      left: {
        heading: 'Business Readiness',
        items: [
          'Data quality and accessibility — does the org have clean, structured data where AI will operate?',
          'Organizational appetite — is leadership aligned on risk tolerance and investment horizon?',
          'Compliance posture — are there regulatory constraints (industry, geography) that will affect deployment?',
        ],
      },
      right: {
        heading: 'Technical Readiness',
        items: [
          'Tooling maturity — are current workflows documented well enough to identify automation candidates?',
          'Team skill baseline — what is the current AI literacy across roles?',
          'Infrastructure readiness — can existing systems support API integrations, model hosting, or agent deployment?',
        ],
      },
    },
    callouts: [
      {
        label: 'Real-World Signal',
        text:
          'An SMB that cannot describe its top 5 workflows by ROI is not ready to automate them. ' +
          'Start with process clarity before introducing AI. The readiness assessment is not a formality — ' +
          'it is the difference between a pilot that delivers and one that quietly gets shelved at 60 days.',
      },
    ],
  },
  {
    number: '1',
    name: 'Workflows',
    type: 'step',
    keyQuestion: 'Where will AI create the most value — and for whom?',
    subtitle: 'The first strategic decision',
    intro:
      'The first strategic decision: is the company looking to elevate the services it delivers ' +
      'to customers, or to increase internal productivity in Engineering and Product teams? These are not ' +
      'mutually exclusive, but they require different prioritization, different stakeholders, and very ' +
      'different risk profiles. Getting this wrong means burning budget on the wrong problem.',
    columns: {
      left: {
        heading: 'Customer-Facing',
        items: [
          'Which products are most profitable — and where does AI improve them?',
          'What workflows are top-priority by ROI?',
          'Can AI reduce time-to-value for the client?',
          'What is the workflow status? (documentation, complexity, reversibility)',
        ],
      },
      right: {
        heading: 'Engineering & Product Teams',
        items: [
          'What is the current overhead cost per FTE? (billable hours model)',
          'Where can delivery speed improve without sacrificing quality?',
          'How is the SDLC performing for non-coding activities? (specs, reviews, testing)',
          'Is the process ready to implement Skills and Agents?',
        ],
      },
    },
    callouts: [
      {
        label: 'Real-World Example',
        text:
          'A feature that previously required a full sprint — frontend scaffolding, API wiring, basic ' +
          'validation logic — was completed in under a day using AI-assisted development. The developer ' +
          'did not write less; they wrote better. The time recovered was redirected to a complex integration ' +
          'that genuinely required their expertise. That reallocation is where the ROI compounds.',
      },
    ],
    tables: [
      {
        title: 'Prioritization Criteria',
        headers: ['Criterion', 'What to Ask'],
        rows: [
          ['Impact', 'Revenue influence, cost reduction, or risk mitigation?'],
          ['Feasibility', 'Data availability, process clarity, tooling readiness?'],
          ['Time-to-value', 'Can a meaningful result be shown within one quarter?'],
          ['Reversibility', 'If the AI component fails, can the team fall back gracefully?'],
        ],
      },
    ],
  },
  {
    number: '2',
    name: 'Guardians: Governance & Cost Control',
    type: 'step',
    keyQuestion: 'How do we keep AI safe, scoped, and cost-efficient?',
    subtitle: 'Keep AI safe, scoped, and cost-efficient',
    intro:
      'Governance is not a checkbox — it is an ongoing operational discipline. Two failure modes ' +
      'are equally dangerous: AI deployed with no boundaries, and AI so restricted it delivers no value. ' +
      'The Guardians step defines the boundaries and the mechanisms to enforce them. This is where most ' +
      'SMBs discover the gap between "we bought a license" and "we are getting ROI."',
    columns: {
      left: {
        heading: 'Model Choice',
        items: [
          'Right model for the right task — not every query needs GPT-4 class capability',
          'Use smaller, faster models for classification, routing, and structured extraction',
          'Reserve frontier models for reasoning-intensive or high-stakes outputs',
        ],
      },
      right: {
        heading: 'Token Cost Management',
        items: [
          'How are tokens being consumed by resource type? (HTML parsing vs. semantic search vs. generation)',
          'Track token cost per workflow — not just aggregate API spend',
          'Model review cadence: re-evaluate model selection as new releases drop',
        ],
      },
    },
    callouts: [
      {
        label: 'Real-World Example',
        text:
          'A SaaS platform embedded a chatbot with open LLM access for user support. Without context ' +
          'boundaries, users began asking questions outside the platform\'s scope — legal, tax, personal advice. ' +
          'The result: no real value delivered, significant token costs, and compliance exposure. The fix: ' +
          'context-bounded prompts, model downgrade for low-complexity queries, and a topic classifier at ' +
          'the entry point.',
      },
      {
        label: 'Real-World Example',
        text:
          'A developer was burning through significant token allocation updating HTML templates and making ' +
          'CSS adjustments — tasks that a find-and-replace or a junior edit could handle in seconds. The AI ' +
          'agent was being used as a glorified text editor. The fix was simple: establish task tiers. Routine ' +
          'edits stay out of the AI context entirely. The agent is reserved for architecture questions, ' +
          'debugging complex flows, and generating tested logic from scratch.',
      },
    ],
    tables: [
      {
        title: 'Measuring Engineer-Level AI Effectiveness',
        headers: ['Output Quality Signals', 'Cost Efficiency Signals'],
        rows: [
          [
            'Tasks completed per sprint vs. pre-AI baseline',
            'Token spend per completed task (not just per session)',
          ],
          [
            'Complexity of tasks the engineer is now able to take on',
            'Ratio of frontier model usage vs. lightweight model usage',
          ],
          [
            'Reduction in time spent on boilerplate and scaffolding',
            'Frequency of hitting token limits mid-task (signals context mismanagement)',
          ],
          [
            'Quality indicators: defect rate, PR review cycles, test coverage',
            'License cost vs. estimated hours saved at loaded FTE rate',
          ],
        ],
      },
    ],
  },
  {
    number: '3',
    name: 'Data Protection',
    type: 'step',
    keyQuestion: 'How do we protect IP, PII, and security at every layer?',
    subtitle: 'IP, PII, and security at every layer',
    intro:
      'Data protection is the non-negotiable foundation. For SMBs especially, a single data incident ' +
      'can be existential. This step is not about slowing down AI adoption — it is about ensuring it ' +
      'survives contact with the real world. Every AI workflow needs to answer: what data goes in, ' +
      'what comes out, and who can see it.',
    columns: {
      left: {
        heading: 'Intellectual Property',
        items: [
          'Identify what constitutes proprietary IP in your context (source code, pricing models, client lists, trade secrets)',
          'Establish data classification before connecting any system to an LLM',
          'Audit which data flows into AI pipelines and from where',
        ],
      },
      right: {
        heading: 'PII & Privacy',
        items: [
          'Mask or anonymize PII before it enters any model context',
          'Understand your LLM provider\'s data retention and training policies',
          'GDPR, CCPA, and industry-specific compliance (HIPAA, SOC 2) must be mapped to AI workflows',
        ],
      },
    },
    callouts: [
      {
        label: 'Security Practices',
        text:
          'Treat user inputs as untrusted — validate and sanitize before model ingestion (prompt injection). ' +
          'Rotate credentials, scope by service, never hard-code API keys. AI capabilities should respect ' +
          'the same RBAC as the rest of the platform. Evaluate third-party AI providers against your security standards.',
      },
    ],
  },
  {
    number: 'P',
    name: 'People & Change Management',
    type: 'ongoing',
    keyQuestion: 'How do we build lasting internal AI competency?',
    subtitle: 'The pillar that is consistently the most underfunded',
    intro:
      'This is the pillar that the framework\'s core premise demands — yet it is consistently the most ' +
      'underfunded part of any AI initiative. You can build the perfect workflow automation and still have ' +
      'it ignored, circumvented, or quietly abandoned within 60 days. Not because the technology failed — ' +
      'because adoption was assumed, not managed.',
    columns: {
      left: {
        heading: 'Leadership & Culture',
        items: [
          'Identify internal AI champions in each team before rollout — not after',
          'Create a safe space for experimentation: pilots that are allowed to fail without penalty',
          'Communicate the "why" at every level — from executive sponsor to individual contributor',
        ],
      },
      right: {
        heading: 'Teams & Skills',
        items: [
          'Train for the workflow, not the tool — contextual training outperforms generic AI literacy programs',
          'Manage resistance explicitly: name the fears (job loss, skill obsolescence, extra work) and address them directly',
          'Leverage diverse strengths — your best engineer and your most experienced domain expert will have opposite strengths',
        ],
      },
    },
    callouts: [
      {
        label: 'Practical Note',
        text:
          'AI fluency is not uniform. Your best engineer and your most experienced domain expert will have ' +
          'opposite strengths. Design adoption programs that leverage both — the engineer brings prompting ' +
          'discipline and tool intuition, the domain expert brings context that no model has.',
      },
    ],
  },
  {
    number: 'M',
    name: 'Measurement & ROI',
    type: 'ongoing',
    keyQuestion: 'How do we know it is working?',
    subtitle: 'Define success metrics before deployment — not after',
    intro:
      'SMBs need to justify AI spend to stakeholders who may be skeptical. This requires defining ' +
      'success metrics before deployment — not after. Without measurement, AI adoption becomes an ' +
      'act of faith rather than a business decision. The review cadence below is not optional — it is ' +
      'how you avoid the slow drift from "this is working" to "we\'re not sure what this costs."',
    columns: {
      left: {
        heading: 'Output Quality Signals',
        items: [
          'Tasks completed per sprint vs. pre-AI baseline',
          'Complexity of tasks the engineer is now able to take on',
          'Reduction in time spent on boilerplate and scaffolding',
          'Quality indicators: defect rate, PR review cycles, test coverage',
        ],
      },
      right: {
        heading: 'Cost Efficiency Signals',
        items: [
          'Token spend per completed task (not just per session)',
          'Ratio of frontier model usage vs. lightweight model usage',
          'Frequency of hitting token limits mid-task (signals context mismanagement)',
          'License cost vs. estimated hours saved at loaded FTE rate',
        ],
      },
    },
    callouts: [
      {
        label: 'Review Cadence',
        text:
          '30 days: Is adoption happening? Are users engaging with the AI feature? ' +
          '60 days: Are the KPIs moving? Identify early blockers. ' +
          '90 days: Quantify ROI — scale, iterate, or sunset. ' +
          'Quarterly: Re-evaluate model selection, token costs, and governance policies as the landscape evolves.',
      },
    ],
    tables: [
      {
        title: 'Example KPIs by Workflow Type',
        headers: ['Workflow Type', 'Metric', 'Target Signal'],
        rows: [
          ['Customer support automation', 'Resolution time / escalation rate', '20-40% reduction in Tier 1 tickets'],
          ['Code review assistance', 'PR cycle time', 'Faster review turnaround, lower defect rate'],
          ['Document generation', 'Time-to-draft', 'Hours saved per FTE per week'],
          ['Token cost governance', 'Cost per workflow task', 'Stays within budgeted threshold by model tier'],
          ['Internal knowledge search', 'Time-to-answer for common queries', 'Reduction in internal Slack/email noise'],
        ],
      },
    ],
  },
];
