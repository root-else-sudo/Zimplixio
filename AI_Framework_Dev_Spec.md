# AI Adoption Framework — Development Specification
**Project:** Zimplixio — AI Skills Showcase  
**Feature:** Responsible AI Adoption Framework + Readiness Assessment  
**Stack:** Django (backend) · React (frontend component) · Anthropic Python SDK  
**Last Updated:** March 2026

---

## 1. Overview

A single-page feature embedded directly in Zimplixio consisting of two sequential sections:

1. **Framework Display** — An interactive, navigable presentation of the 6-stage AI adoption framework. Designed to be executive-readable and portfolio-quality.
2. **AI Readiness Assessment** — An 8-question guided form that calls the Anthropic API server-side and returns a personalized readiness report rendered on screen.

The page serves two audiences simultaneously:
- **Prospective clients** who want to understand your AI adoption methodology
- **Technical evaluators / interviewers** who are assessing your ability to design and ship AI-powered products

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (component inside existing Django project) |
| Styling | Tailwind CSS (existing Zimplixio setup) |
| Backend | Django view — `POST /api/assessment/` |
| AI SDK | `anthropic` Python SDK |
| Model | `claude-sonnet-4-6` |
| Config | API key stored in `.env` as `ANTHROPIC_API_KEY` |
| Fonts | Google Fonts — display: `DM Serif Display`, body: `DM Sans` |

---

## 3. Design Direction

**Aesthetic:** Refined dark-mode editorial. Not a SaaS dashboard. Not a marketing page. Feels like a premium consulting artifact — the kind of thing McKinsey would build if they knew how to code.

**Color palette (CSS variables):**
```css
--bg-primary: #0A0E1A        /* near-black navy */
--bg-secondary: #111827      /* dark card surface */
--bg-elevated: #1A2235       /* elevated panel */
--accent-primary: #3B82F6    /* electric blue */
--accent-secondary: #60A5FA  /* lighter blue */
--accent-callout: #F59E0B    /* amber — for real-world callouts only */
--text-primary: #F1F5F9      /* near-white */
--text-secondary: #94A3B8    /* slate-400 */
--text-muted: #475569         /* slate-600 */
--border-subtle: #1E2D45     /* barely-visible border */
--success: #10B981           /* emerald — readiness indicators */
--warning: #F59E0B           /* amber */
--danger: #EF4444            /* red */
```

**Typography:**
- Display headings: `DM Serif Display` (italic for pull quotes and stage numbers)
- Body / UI: `DM Sans`
- Stage numbers: Large, translucent, used as typographic anchors behind content

**Motion:**
- Stage cards expand/collapse with smooth height transitions
- Assessment questions fade + slide between steps
- Report blocks stagger-reveal on load (150ms delay between each block)
- No gratuitous animation — motion is purposeful

**Callout boxes (Real-World Examples):**
- Left border: 3px solid `--accent-callout` (amber)
- Background: subtle amber tint `rgba(245, 158, 11, 0.06)`
- Label "Real-World Example" in amber uppercase tracking-widest
- These are the most credible content on the page — treat them as featured, not footnotes

---

## 4. Section 1 — Framework Display

### 4.1 Page Header

```
[Large typographic area]
RESPONSIBLE AI ADOPTION                    ← DM Serif Display, large
For Small & Mid-Sized Businesses           ← DM Sans, secondary color
────────────────────────────────
A practitioner framework built from
real implementation experience.            ← body text, muted
```

Subtle noise texture or grid pattern in background. Stage number "0" as a large ghost element behind the header.

---

### 4.2 Framework Navigator (Stepper)

Six stage cards rendered vertically. Each card:

**Collapsed state:**
- Left: large stage number (`0`–`3`, then icons for the two Ongoing stages)
- Center: Stage name + Key Question in one line
- Right: Chevron down indicator
- Full-width clickable

**Expanded state (click to open, click to close):**
- Stage name as heading
- Key question as prominent subheader in accent color
- Body content in clean prose
- Real-world callout box (amber, see design above) — visually prominent
- Two-column comparison table where applicable (Workflows, Guardians)
- Smooth height animation on expand/collapse

**Only one stage open at a time** (accordion behavior).

---

### 4.3 Stage Content

Hardcode all content from the framework document. Do not parse the .docx at runtime.

#### Stage 0 — AI Readiness Assessment
- Key question: *Is the organization ready to adopt AI responsibly?*
- What to Evaluate: 5 bullet points
- Callout: "An SMB that cannot describe its top 5 workflows by ROI is not ready to automate them..."

#### Stage 1 — Workflows
- Key question: *Where will AI create the most value — and for whom?*
- Two-column table: Customer-Facing vs Eng/Product
- Prioritization Criteria: 4 bullets
- Callout: FTE reallocation example (sprint → day story)

#### Stage 2 — Guardians: Governance & Cost Control
- Key question: *How do we keep AI safe, scoped, and cost-efficient?*
- Scope Control section
- Callout: The open chatbot / context boundary disaster story
- Model Selection two-column table
- AI License ROI section
- Callout: Developer burning tokens on HTML/CSS updates
- Engineer effectiveness two-column table

#### Stage 3 — Data Protection
- Key question: *How do we protect IP, PII, and security at every layer?*
- Two-column table: IP vs PII & Privacy
- Security Practices: 4 bullets

#### Ongoing — People & Change Management
- Why it fails without this
- Key Actions: 5 bullets
- Callout: AI fluency is not uniform

#### Ongoing — Measurement & ROI
- KPI table: 5 workflow types × 3 columns
- Review Cadence: 30/60/90/Quarterly bullets

---

### 4.4 Section Transition

After the last stage card, a full-width CTA panel transitions into Section 2:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│   See where your company stands                     │
│   Answer 8 questions and receive a personalized     │
│   AI readiness report for your organization.        │
│                                                     │
│              [ Start Assessment → ]                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

Button click scrolls to Section 2 and activates the form.

---

## 5. Section 2 — AI Readiness Assessment

### 5.1 Form UX

- One question visible at a time
- Progress bar at top (e.g. "Question 3 of 8")
- Back / Next navigation
- Final step shows "Generate My Assessment" CTA
- Form state managed in React (`useState`)
- All questions answered before submission is enabled

---

### 5.2 The 8 Questions

| # | Question | Type | Options |
|---|---|---|---|
| 1 | What industry are you in? | Single select | Technology, Legal & Compliance, Finance, Healthcare, Manufacturing, Retail & E-commerce, Professional Services, Other |
| 2 | How large is your company? | Single select | 1–10 employees, 11–50 employees, 51–200 employees, 200+ employees |
| 3 | How would you describe your current AI usage? | Single select | None — we haven't started, Experimenting informally, One tool in production, Multiple tools deployed |
| 4 | Where do you want AI to create value first? | Single select | Customer-facing products & services, Internal / Engineering productivity, Both equally |
| 5 | How well-documented are your core workflows? | Single select | Not documented, Partially documented, Well documented |
| 6 | How would you describe your team's AI literacy? | Single select | Low — most people haven't used AI tools, Mixed — varies by role, Moderate — comfortable with basic tools, High — active daily users |
| 7 | What are your biggest concerns about AI adoption? | Multi-select (up to 3) | Cost overruns & runaway spend, Data security & IP exposure, Team resistance to change, Lack of internal expertise, Regulatory & compliance risk, Moving too slowly vs competitors |
| 8 | What is your primary goal in the next 90 days? | Single select | Identify where AI can help us, Launch a focused pilot, Scale something already working, Build internal AI capability |

---

### 5.3 Loading State

After "Generate My Assessment" is clicked:
- Form fades out
- Centered loading indicator with message: *"Analyzing your profile..."*
- Estimated 3–6 seconds for API round-trip
- Do not show a spinner alone — show a brief animated sequence of the framework stage names appearing, as if being evaluated

---

### 5.4 Report Output Layout

Report replaces the form. Four distinct blocks, stagger-revealed with 150ms delay between each:

#### Block 1 — Readiness Level
```
┌────────────────────────────────┐
│  READINESS LEVEL               │
│                                │
│  ●  DEVELOPING                 │  ← badge: Early / Developing / Ready
│                                │
│  "One sentence diagnosis"      │
└────────────────────────────────┘
```
Badge color: Early = amber, Developing = blue, Ready = emerald

#### Block 2 — Where to Start
```
┌────────────────────────────────┐
│  WHERE TO START                │
│                                │
│  Step 2 — Guardians            │  ← stage name highlighted
│                                │
│  2-3 sentences specific to     │
│  this company's profile        │
└────────────────────────────────┘
```

#### Block 3 — Top Risks
Three cards in a row (or stacked on mobile):
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ ⚠ Risk 1 │  │ ⚠ Risk 2 │  │ ⚠ Risk 3 │
│          │  │          │  │          │
│ detail   │  │ detail   │  │ detail   │
└──────────┘  └──────────┘  └──────────┘
```

#### Block 4 — First 30 Days
Numbered action list, clean and scannable. 3–5 items. Each action is specific — not "evaluate AI tools" but "map your top 3 workflows by FTE hours spent and identify which has the best documentation."

#### Block 5 — Verdict
Full-width pull quote at the bottom:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  "The single most important thing for this          │
│   company right now."                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```
DM Serif Display italic, large, amber accent border left.

#### Actions below report
- `[ ← Start Over ]` — resets form state
- `[ Download PDF ]` — (optional, implement if time allows — use browser print dialog scoped to report div)

---

## 6. Backend — Django API View

### 6.1 URL

```python
# urls.py
path('api/assessment/', views.assessment_view, name='assessment'),
```

### 6.2 View

```python
# views.py
import json
import anthropic
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

@csrf_exempt
@require_POST
def assessment_view(request):
    try:
        body = json.loads(request.body)
        answers = body.get('answers', {})

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(answers)

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        raw = message.content[0].text
        # Strip any accidental markdown fences
        clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
        result = json.loads(clean)

        return JsonResponse({"success": True, "report": result})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid response from model"}, status=500)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
```

### 6.3 System Prompt

```python
def build_system_prompt():
    return """
You are an AI adoption advisor specializing in small and mid-sized businesses.
You use a specific 6-stage framework to assess organizational readiness:

STAGE 0 - AI Readiness Assessment: Evaluate data quality, workflow documentation,
team skill baseline, leadership alignment, and compliance posture before any investment.

STAGE 1 - Workflows: Identify whether value should be created for customers or
internal Engineering/Product teams first. Prioritize by ROI, feasibility,
time-to-value, and reversibility.

STAGE 2 - Guardians (Governance & Cost Control): Define AI deployment boundaries,
manage token costs, select the right model for each task, and measure license ROI
against actual engineer output.

STAGE 3 - Data Protection: Protect IP, PII, and security at every layer.
Classify data before connecting to any LLM. Enforce prompt injection safeguards.

ONGOING - People & Change Management: Build internal champions, manage resistance,
train for the workflow not the tool.

ONGOING - Measurement & ROI: Define KPIs before deployment. Review at 30, 60, 90 days.

CRITICAL RULES:
- Always return valid JSON matching the exact schema below. Nothing else.
- No markdown. No preamble. No explanation outside the JSON.
- Be specific and practitioner-level. Never generic.
- Reference the user's actual inputs in your reasoning.
- A legal firm with 11 employees gets different advice than a 200-person manufacturer.
- The first_30_days actions must be concrete and specific to their profile.
  Bad: "Evaluate AI tools." Good: "Map your top 3 client workflows by hours spent
  and identify which has the clearest success metric."

REQUIRED JSON SCHEMA:
{
  "readiness_level": "Early" | "Developing" | "Ready",
  "readiness_summary": "One sentence diagnosis specific to their profile",
  "priority_stage": {
    "name": "Stage name from the framework",
    "reason": "2-3 sentences specific to their inputs explaining why this stage first"
  },
  "top_risks": [
    { "risk": "Short risk title", "detail": "One sentence specific to their context" },
    { "risk": "...", "detail": "..." },
    { "risk": "...", "detail": "..." }
  ],
  "first_30_days": [
    "Specific action 1 tailored to their profile",
    "Specific action 2",
    "Specific action 3",
    "Specific action 4"
  ],
  "one_line_verdict": "The single most important thing for this company right now"
}
"""
```

### 6.4 User Prompt

```python
def build_user_prompt(answers):
    return f"""
A company has submitted the following AI readiness profile:

- Industry: {answers.get('industry', 'Not specified')}
- Company size: {answers.get('size', 'Not specified')}
- Current AI usage: {answers.get('current_usage', 'Not specified')}
- Where they want AI to create value first: {answers.get('value_target', 'Not specified')}
- Workflow documentation level: {answers.get('workflow_docs', 'Not specified')}
- Team AI literacy: {answers.get('ai_literacy', 'Not specified')}
- Biggest concerns about AI adoption: {answers.get('concerns', 'Not specified')}
- Primary goal in the next 90 days: {answers.get('goal_90_days', 'Not specified')}

Generate their AI Readiness Assessment. Return only the JSON object.
"""
```

---

## 7. Frontend — API Call

```javascript
// In your React component
const handleSubmit = async () => {
  setLoading(true);
  setError(null);

  try {
    const response = await fetch('/api/assessment/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: formAnswers }),
    });

    const data = await response.json();

    if (data.success) {
      setReport(data.report);
    } else {
      setError('Something went wrong. Please try again.');
    }
  } catch (err) {
    setError('Connection error. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

---

## 8. Environment Setup

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

```python
# settings.py — ensure env vars are loaded
import os
from dotenv import load_dotenv
load_dotenv()
```

```bash
# Install SDK
pip install anthropic
```

---

## 9. File Structure

```
zimplixio/
├── framework/                     ← new Django app
│   ├── views.py                   ← assessment_view
│   ├── urls.py                    ← /api/assessment/
│   └── prompts.py                 ← build_system_prompt, build_user_prompt
│
├── static/
│   └── js/
│       └── components/
│           └── AIFramework/
│               ├── index.jsx           ← root component
│               ├── FrameworkNav.jsx    ← Section 1 stepper
│               ├── StageCard.jsx       ← individual accordion card
│               ├── CalloutBox.jsx      ← amber callout component
│               ├── TwoColTable.jsx     ← comparison table component
│               ├── Assessment.jsx      ← Section 2 form
│               ├── QuestionStep.jsx    ← individual question UI
│               ├── LoadingState.jsx    ← animated loading
│               └── Report.jsx          ← report output renderer
│
└── templates/
    └── framework/
        └── index.html             ← page template mounting React root
```

---

## 10. Component State Map

```
AIFramework (root)
├── activeStage: number | null        ← which accordion card is open
├── assessmentActive: boolean         ← has user clicked Start Assessment
├── formAnswers: object               ← all 8 question responses
├── currentQuestion: number (0–7)     ← which question is showing
├── loading: boolean                  ← API call in flight
├── report: object | null             ← parsed API response
└── error: string | null              ← error message if call fails
```

---

## 11. Error Handling

| Scenario | Behavior |
|---|---|
| API key missing/invalid | Django returns 500, frontend shows "Assessment unavailable" with contact link |
| Model returns malformed JSON | Django catches JSONDecodeError, returns 500, frontend shows retry option |
| Network timeout | Frontend fetch fails, shows "Connection error — try again" with retry button |
| User hits back on question 1 | Back button disabled on first question |
| Form submitted incomplete | Submit button disabled until all questions answered |

---

## 12. What to Tell Claude Code

When starting the Claude Code session, provide:

1. This spec file as primary context
2. The `AI_Adoption_Framework.docx` (or paste the text content) so Claude Code has the exact framework wording for Section 1 content
3. Your existing Zimplixio project structure so the new components match your conventions

**Opening prompt for Claude Code session:**
```
I am building a new page in my Zimplixio Django project.
Read the attached development spec (AI_Framework_Dev_Spec.md) 
and the framework document (AI_Adoption_Framework.docx) fully 
before writing any code. Start with the Django backend — 
the assessment view, URL, and prompt builders — then move 
to the React components. Ask me before making any assumptions 
about my existing project structure.
```

---

## 13. Demo Script (for the interview)

1. Open Zimplixio to the framework page
2. Walk the interviewer through 2–3 stages — specifically open the Guardians callout (the token/chatbot story) and the FTE reallocation callout in Workflows — these are the experience signals
3. Scroll to the Assessment CTA
4. Fill out a profile matching Aderant's context: Legal & Compliance, 200+ employees, Multiple tools deployed, Internal/Engineering productivity, Well documented, Mixed literacy, Data security & compliance risk, Scale something existing
5. Submit and walk through the report as it renders
6. Point out: "The report is shaped by a system prompt I engineered — it knows the framework, it knows the risk profile for a legal-sector company, and it returns structured JSON that the frontend renders. That's the same pattern I'd use to embed AI into a product workflow."

That last sentence is the answer to "how would you apply this at Aderant."
