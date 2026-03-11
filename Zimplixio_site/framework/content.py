"""
Hardcoded framework content for the AI Adoption Framework page.
Each stage is a dict passed to the template via context.
body_html is pre-formatted HTML rendered with |safe in the template.
"""

STAGES = [
    {
        'number': '0',
        'name': 'AI Readiness Assessment',
        'type': 'step',
        'key_question': 'Is the organization ready to adopt AI responsibly?',
        'subtitle': 'Before you invest, know what you are investing into',
        'body_html': '''
            <p class="mb-4">This step is often skipped — and its absence is the most common reason AI pilots fail.
            The assessment is not about gatekeeping; it is about honest scoping.</p>
            <h4 class="text-lg font-semibold text-gray-900 mb-3">What to Evaluate</h4>
            <ul class="list-disc pl-5 space-y-2 text-gray-700 mb-4">
                <li><strong>Data quality and accessibility</strong> — does the org have clean, structured data where AI will operate?</li>
                <li><strong>Tooling maturity</strong> — are current workflows documented well enough to identify automation candidates?</li>
                <li><strong>Team skill baseline</strong> — what is the current AI literacy across roles?</li>
                <li><strong>Organizational appetite</strong> — is leadership aligned on risk tolerance and investment horizon?</li>
                <li><strong>Compliance posture</strong> — are there regulatory constraints (industry, geography) that will affect deployment?</li>
            </ul>
        ''',
        'callout': {
            'label': 'Real-World Signal',
            'text': 'An SMB that cannot describe its top 5 workflows by ROI is not ready to automate them. Start with process clarity before introducing AI.',
        },
        'table': None,
    },
    {
        'number': '1',
        'name': 'Workflows',
        'type': 'step',
        'key_question': 'Where will AI create the most value — and for whom?',
        'subtitle': 'The first strategic decision',
        'body_html': '''
            <p class="mb-4">The first strategic decision: is the company looking to elevate the services it delivers
            to customers, or to increase internal productivity in Engineering and Product teams? These are not
            mutually exclusive, but they require different prioritization, different stakeholders, and very
            different risk profiles.</p>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">Prioritization Criteria</h4>
            <ul class="list-disc pl-5 space-y-2 text-gray-700 mb-4">
                <li><strong>Impact:</strong> revenue influence, cost reduction, or risk mitigation</li>
                <li><strong>Feasibility:</strong> data availability, process clarity, tooling readiness</li>
                <li><strong>Time-to-value:</strong> can a meaningful result be shown within one quarter?</li>
                <li><strong>Reversibility:</strong> if the AI component fails, can the team fall back gracefully?</li>
            </ul>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">The FTE Reallocation Opportunity</h4>
            <p class="mb-4">AI adoption is not only about delivering faster. It is about what your team does with
            the time it recovers.</p>
            <p class="mb-4">Full-stack features that once took weeks to scope, design, and build can now be
            completed in hours with the right AI tooling and a skilled engineer directing it. But the real
            strategic gain is not speed — it is what your engineers do next. When AI absorbs the mechanical
            work of writing boilerplate code, generating tests, or scaffolding components, your FTEs become
            available for higher-value work: architecture decisions, client-facing problem solving, domain
            logic that requires real judgment.</p>
        ''',
        'callout': {
            'label': 'Real-World Example',
            'text': 'A feature that previously required a full sprint — frontend scaffolding, API wiring, basic validation logic — was completed in under a day using AI-assisted development. The developer did not write less; they wrote better. The time recovered was redirected to a complex integration that genuinely required their expertise. That reallocation is where the ROI compounds.',
        },
        'table': {
            'title': 'Workflow Comparison',
            'headers': ['Customer-Facing Workflows', 'Eng / Product Workflows'],
            'rows': [
                ['Which products are most profitable?', 'What is the current overhead cost per FTE? (billable hours model)'],
                ['What workflows are top-priority by ROI?', 'Where can delivery speed improve?'],
                ['What is the workflow status? (documentation / complexity)', 'How is the SDLC performing for non-coding activities?'],
                ['Can AI reduce time-to-value for the client?', 'Is the process ready to implement Skills and Agents?'],
            ],
        },
    },
    {
        'number': '2',
        'name': 'Guardians: Governance & Cost Control',
        'type': 'step',
        'key_question': 'How do we keep AI safe, scoped, and cost-efficient?',
        'subtitle': 'Keep AI safe, scoped, and cost-efficient',
        'body_html': '''
            <p class="mb-4">Governance is not a checkbox — it is an ongoing operational discipline. Two failure
            modes are equally dangerous: AI deployed with no boundaries, and AI so restricted it delivers no
            value. The Guardians step defines the boundaries and the mechanisms to enforce them.</p>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">Scope Control</h4>
            <ul class="list-disc pl-5 space-y-2 text-gray-700 mb-4">
                <li>Deploy AI in specific, bounded contexts — not company-wide open access</li>
                <li>Public-facing LLMs without context boundaries are a direct path to runaway token costs and off-topic liability</li>
            </ul>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">AI License ROI: Are You Getting What You Paid For?</h4>
            <p class="mb-4">Premium AI developer tools — Claude Code Max, GitHub Copilot Enterprise, Cursor Pro —
            carry real per-seat costs. The question every engineering manager must answer: is the license generating
            measurable output, or is it generating token spend?</p>
            <p class="mb-4">Two red flags that indicate a license is not delivering ROI:</p>
            <ul class="list-disc pl-5 space-y-2 text-gray-700 mb-6">
                <li>The engineer consistently hits token limits without completing assigned tasks. This signals either poor prompting discipline, working in overly large contexts, or attempting to solve problems the tool is not suited for.</li>
                <li>Token consumption is concentrated on low-value mechanical work — HTML edits, CSS tweaks, string updates — rather than on reasoning-heavy tasks where the model genuinely accelerates output.</li>
            </ul>
        ''',
        'callout': {
            'label': 'Real-World Example',
            'text': 'A SaaS platform embedded a chatbot with open LLM access for user support. Without context boundaries, users began asking questions outside the platform\'s scope (legal, tax, personal advice). The result: no real value delivered, significant token costs, and compliance exposure. The fix: context-bounded prompts, model downgrade for low-complexity queries, and a topic classifier at the entry point.',
        },
        'callout_2': {
            'label': 'Real-World Example',
            'text': 'A developer was burning through significant token allocation updating HTML templates and making CSS adjustments — tasks that a find-and-replace or a junior edit could handle in seconds. The AI agent was being used as a glorified text editor. The fix was simple: establish task tiers. Routine edits stay out of the AI context entirely. The agent is reserved for architecture questions, debugging complex flows, and generating tested logic from scratch.',
        },
        'table': {
            'title': 'Model Choice vs Token Cost Management',
            'headers': ['Model Choice', 'Token Cost Management'],
            'rows': [
                ['Right model for the right task — not every query needs GPT-4 class capability', 'How are tokens being consumed by resource type? (HTML parsing vs. semantic search vs. generation)'],
                ['Use smaller, faster models for classification, routing, and structured extraction', 'Track token cost per workflow — not just aggregate API spend'],
                ['Reserve frontier models for reasoning-intensive or high-stakes outputs', 'Model review cadence: re-evaluate model selection as new releases drop'],
            ],
        },
        'table_2': {
            'title': 'Measuring Engineer-Level AI Effectiveness',
            'headers': ['Output Quality Signals', 'Cost Efficiency Signals'],
            'rows': [
                ['Tasks completed per sprint vs. pre-AI baseline', 'Token spend per completed task (not just per session)'],
                ['Complexity of tasks the engineer is now able to take on', 'Ratio of frontier model usage vs. lightweight model usage'],
                ['Reduction in time spent on boilerplate and scaffolding', 'Frequency of hitting token limits mid-task (signals context mismanagement)'],
                ['Quality indicators: defect rate, PR review cycles, test coverage', 'License cost vs. estimated hours saved at loaded FTE rate'],
            ],
        },
    },
    {
        'number': '3',
        'name': 'Data Protection',
        'type': 'step',
        'key_question': 'How do we protect IP, PII, and security at every layer?',
        'subtitle': 'IP, PII, and security at every layer',
        'body_html': '''
            <p class="mb-4">Data protection is the non-negotiable foundation. For SMBs especially, a single data
            incident can be existential. This step is not about slowing down AI adoption — it is about ensuring
            it survives contact with the real world.</p>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">Security Practices</h4>
            <ul class="list-disc pl-5 space-y-2 text-gray-700 mb-4">
                <li><strong>Prompt injection:</strong> treat user inputs as untrusted — validate and sanitize before model ingestion</li>
                <li><strong>API key management:</strong> rotate credentials, scope by service, never hard-code</li>
                <li><strong>Access control:</strong> AI capabilities should respect the same RBAC as the rest of the platform</li>
                <li><strong>Vendor risk:</strong> evaluate third-party AI providers against your security standards</li>
            </ul>
        ''',
        'callout': None,
        'table': {
            'title': 'Three Protection Domains',
            'headers': ['Intellectual Property', 'PII & Privacy'],
            'rows': [
                ['Identify what constitutes proprietary IP in your context (source code, pricing models, client lists, trade secrets)', 'Mask or anonymize PII before it enters any model context'],
                ['Establish data classification before connecting any system to an LLM', 'Understand your LLM provider\'s data retention and training policies'],
                ['Audit which data flows into AI pipelines and from where', 'GDPR, CCPA, and industry-specific compliance (HIPAA, SOC 2) must be mapped to AI workflows'],
            ],
        },
    },
    {
        'number': 'P',
        'name': 'People & Change Management',
        'type': 'ongoing',
        'key_question': 'How do we build lasting internal AI competency?',
        'subtitle': 'The pillar that is consistently the most underfunded',
        'body_html': '''
            <p class="mb-4">This is the pillar that the framework\'s core premise demands — yet it is consistently
            the most underfunded part of any AI initiative.</p>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">Why It Fails Without This</h4>
            <p class="mb-4">You can build the perfect workflow automation and still have it ignored, circumvented,
            or quietly abandoned within 60 days. Not because the technology failed — because adoption was
            assumed, not managed.</p>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">Key Actions</h4>
            <ul class="list-disc pl-5 space-y-2 text-gray-700 mb-4">
                <li>Identify internal AI champions in each team before rollout — not after</li>
                <li>Create a safe space for experimentation: pilots that are allowed to fail without penalty</li>
                <li>Train for the workflow, not the tool — contextual training outperforms generic AI literacy programs</li>
                <li>Manage resistance explicitly: name the fears (job loss, skill obsolescence, extra work) and address them directly</li>
                <li>Communicate the \'why\' at every level — from executive sponsor to individual contributor</li>
            </ul>
        ''',
        'callout': {
            'label': 'Practical Note',
            'text': 'AI fluency is not uniform. Your best engineer and your most experienced domain expert will have opposite strengths. Design adoption programs that leverage both.',
        },
        'table': None,
    },
    {
        'number': 'M',
        'name': 'Measurement & ROI',
        'type': 'ongoing',
        'key_question': 'How do we know it is working?',
        'subtitle': 'Define success metrics before deployment — not after',
        'body_html': '''
            <p class="mb-4">SMBs need to justify AI spend to stakeholders who may be skeptical. This requires
            defining success metrics before deployment — not after.</p>

            <h4 class="text-lg font-semibold text-gray-900 mb-3">Review Cadence</h4>
            <ul class="list-disc pl-5 space-y-2 text-gray-700 mb-4">
                <li><strong>30 days:</strong> Is adoption happening? Are users engaging with the AI feature?</li>
                <li><strong>60 days:</strong> Are the KPIs moving? Identify early blockers.</li>
                <li><strong>90 days:</strong> Quantify ROI. Decide: scale, iterate, or sunset.</li>
                <li><strong>Quarterly:</strong> Re-evaluate model selection, token costs, and governance policies as the landscape evolves.</li>
            </ul>
        ''',
        'callout': None,
        'table': {
            'title': 'Example KPIs by Workflow Type',
            'headers': ['Workflow Type', 'Metric', 'Target Signal'],
            'rows': [
                ['Customer support automation', 'Resolution time / escalation rate', '20-40% reduction in Tier 1 tickets'],
                ['Code review assistance', 'PR cycle time', 'Faster review turnaround, lower defect rate'],
                ['Document generation', 'Time-to-draft', 'Hours saved per FTE per week'],
                ['Token cost governance', 'Cost per workflow task', 'Stays within budgeted threshold by model tier'],
                ['Internal knowledge search', 'Time-to-answer for common queries', 'Reduction in internal Slack/email noise'],
            ],
        },
    },
]
