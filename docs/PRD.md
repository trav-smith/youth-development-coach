# Youth Development Coach
## Product Requirements Document

**Version:** 0.5  
**Status:** Independently Deployed Field-Test Prototype  
**Product:** AI Sports Labs  
**Last Updated:** September 25, 2026

## 1. Product Overview

Youth Development Coach is an AI-powered tool that helps youth coaches turn observations from games and practices into structured, evidence-aware development guidance.

Parents may also contribute observations or use the system as a secondary user, but the current product workflow is designed primarily around the needs of a coach.

Coaches regularly observe meaningful patterns — an athlete struggling against fastballs, becoming tentative after mistakes, losing serve consistency later in a match, or performing differently in practice than competition — without necessarily having enough evidence to determine why the pattern is occurring.

Traditional generative AI can provide immediate advice, but often moves too quickly from an observation to a diagnosis or recommendation.

Youth Development Coach is designed around a different principle:

**Observe first. Hypothesize second. Intervene carefully. Learn over time.**

Rather than treating a single observation as proof of a problem, the product separates reported observations from AI inference, maintains competing hypotheses when evidence is incomplete, communicates confidence, recommends low-risk next actions, and identifies evidence that should be collected next.

Over time, the product builds a longitudinal evidence record for an individual athlete.

---

## 2. Problem

Youth coaches and parents regularly face three related challenges.

**Limited expertise:** A person may recognize that something changed without knowing the technical, physical, tactical, or psychological cause.

**Limited evidence:** Youth athlete development decisions are often based on a small number of games, practices, or memorable moments.

**Premature conclusions:** Both humans and AI systems can convert limited observations into confident diagnoses and corrective advice.

For example:

> “My 12-year-old struck out twice and was late on fastballs.”

Possible explanations could include timing, pitch recognition, velocity, mechanics, approach, normal performance variance, or some combination of factors.

A useful development tool should not automatically select one explanation. It should help the user determine what is known, what is possible, and what evidence would distinguish among those possibilities.

---

## 3. Target Users

**Primary user:** Youth coach seeking a low-friction way to capture athlete observations during games and practices, maintain a longitudinal development record, and reason across evidence over time.

**Secondary user:** Parent of a youth athlete who wants to support development while avoiding premature conclusions from isolated performances.

**Athlete:** Youth athlete approximately ages 5–18 participating in organized or recreational sports.

The initial reasoning architecture is designed to be sport-general rather than tied to a single sport. Baseball is the primary workflow context for the current coach-facing prototype, with tennis used as a secondary test of cross-sport generalization.

The product is intended to support — not replace — the judgment of coaches, parents, and athletes.

---

## 4. Product Principles

### Evidence before diagnosis
Reported observations should remain distinct from AI-generated interpretations.

### Uncertainty should be visible
The system should communicate when available evidence is insufficient to support a conclusion.

### Competing hypotheses are valuable
When several explanations fit the available evidence, the system should preserve those alternatives rather than prematurely selecting one.

### Recommendations should match confidence
Low-confidence analysis should favor observation, measurement, and low-risk practice activities rather than highly specific corrective interventions.

### Development should remain constructive
Recommendations and coaching language should be age-appropriate, positive, and useful to youth coaches and parents.

### Athlete context should accumulate
Individual sessions provide weak evidence. Repeated observations across games and practices can reveal stronger patterns.

### AI output requires evaluation
Structured output does not guarantee correct reasoning. Model behavior must be tested for unsupported inference, invented details, overconfidence, and inappropriate recommendations.

### Evidence provenance matters
Human observations, structured performance records, AI-extracted evidence, and AI-generated hypotheses should remain distinguishable rather than collapsing into a single undifferentiated history.

---

## 5. Core User Journey

### Step 1 — Select athlete

The coach selects an existing athlete or creates a new athlete profile containing:

- Name or nickname
- Age
- Sport
- Team, optional
- Position or role, optional

### Step 2 — Capture observation

During a game or practice, the coach records a quick voice note or enters an observation as text.

For voice capture:

- The coach records the observation in the Streamlit interface.
- Speech-to-text converts the recording into a transcript.
- The transcript remains editable so the coach can verify or correct it before saving.

### Step 3 — Save evidence

The reviewed observation is saved immediately to the athlete's persistent longitudinal history.

Saving evidence does not require AI analysis.

This separation allows the coach to capture multiple observations without waiting for the reasoning model and preserves human-reported evidence before interpretation.

### Step 4 — Review athlete history

Saved game and practice observations accumulate chronologically in the athlete's persistent record.

The coach can review this history independently of AI-generated analysis.

### Step 5 — Generate Development Analysis

When useful, the coach requests a Development Analysis across the athlete's accumulated human-reported evidence.

The reasoning engine looks for:

- Repeated patterns
- Contradictory evidence
- Context-specific differences
- Evidence that strengthens or weakens hypotheses
- Changes or adjustments over time

### Step 6 — Receive structured guidance

The user receives:

- Observed
- Possible Explanations
- Development Priorities
- Next Practice
- Coaching Cues
- What to Track Next
- Overall Confidence

### Step 7 — Continue the evidence loop

Future observations are added to the athlete record and can strengthen, weaken, contradict, or leave unresolved earlier explanations.

The intended loop is:

**Capture → Preserve Evidence → Analyze → Track → Capture Again**

---

## 6. v0.1 — Structured Reasoning

### Status
Complete

The initial prototype accepts athlete and session information through a Streamlit interface and sends observations to Claude through the Anthropic API.

Claude produces a structured response enforced through Pydantic models.

### Inputs

- Athlete name/nickname
- Age
- Sport
- Team
- Position/role
- Session type
- Natural-language observation

### Outputs

- Direct observations
- Competing hypotheses
- Hypothesis confidence
- Development priorities
- Practice recommendations
- Coaching cues
- Future tracking recommendations
- Overall confidence and rationale

### Validated Sports

Initial tests successfully produced relevant output for:

- Baseball
- Tennis

No sport-specific application logic was required, supporting the initial hypothesis that the reasoning architecture can generalize across sports.

---

## 7. AI Reasoning Requirements

The AI analysis engine should:

1. Separate directly reported observations from inference.
2. Never represent a hypothesis as an established fact.
3. Avoid diagnosing mechanical, physical, or psychological problems without sufficient evidence.
4. Preserve competing hypotheses when multiple explanations are plausible.
5. Recommend no more than two primary development priorities.
6. Provide age-appropriate and constructive guidance.
7. Identify additional evidence that could confirm or reject hypotheses.
8. Express confidence as Low, Medium, or High.
9. Base confidence on evidence about the individual athlete rather than the general prevalence of an issue.
10. Normally maintain low confidence when evidence comes from a single game, practice, or small number of observations.
11. Avoid specific mechanical corrections when the underlying mechanical cause remains uncertain.
12. Favor observation and low-risk experimentation when evidence is limited.
13. Ensure coaching cues are consistent with the uncertainty of the analysis.
14. Avoid inventing repetitions, training frequency, measurements, history, or other facts not provided by the user.
15. Preserve subjective parent/coach descriptions as reported observations rather than converting them into objective measurements.
16. Require athlete-specific evidence for causal hypotheses.
17. Permit abstention when outcomes are observed but causes remain unsupported.
18. Propagate uncertainty from hypotheses into downstream priorities and recommendations.
19. Preserve evidence provenance rather than silently upgrading subjective or uncertain evidence.

---

## 8. Structured Output Architecture

The application uses a defined Pydantic schema rather than accepting unrestricted natural-language output from the model.

Core entities include:

**Observation**  
Directly reported information.

**Hypothesis**  
A possible explanation linked to supporting observation IDs, missing evidence, and confidence.

**Development Priority**  
A recommended focus linked to one or more hypotheses.

**Practice Recommendation**  
A potential practice action linked to a development priority.

**Coaching Cue**  
Simple athlete-facing language linked to a development priority.

**Tracking Item**  
Evidence to collect in future sessions linked to relevant hypotheses.

**Overall Confidence**  
System-level confidence rating and rationale.

Stable IDs allow relationships among these objects without relying on fragile text matching.

Structured output guarantees response shape, not truth. Model reasoning therefore remains subject to evaluation and deterministic product constraints.

---

## 9. Current Technical Architecture — v0.5

### Application flow

**Coach Browser / Phone  
→ Streamlit Community Cloud  
→ Supabase Postgres  
→ Longitudinal Evidence Retrieval  
→ Claude  
→ Pydantic Structured Output  
→ Deterministic Guardrails  
→ Development Analysis**

For voice observations:

**Coach Voice  
→ Streamlit Audio Input  
→ OpenAI Speech-to-Text  
→ Editable Transcript  
→ Human Review  
→ Supabase Athlete History**

### Key technologies

- Python
- Streamlit
- Streamlit Community Cloud
- Supabase Postgres
- Anthropic API
- Claude Sonnet
- OpenAI speech-to-text
- Pydantic
- GitHub
- Google Colab and Google Drive for development

### Security and secrets

API and database credentials are stored as server-side secrets and are not embedded in the GitHub repository or delivered to the client browser.

The field-test application uses password-based access control before exposing athlete data or application functionality.

This is intended as limited field-test protection rather than a production identity and authorization system.

---

## 10. Known Early Model Failure Modes

Initial testing revealed several important LLM reliability issues.

### Unsupported mechanical prescriptions

Early output recommended cues such as:

> “Get your foot down early.”

The available evidence did not establish that foot timing was the cause of the athlete's difficulty.

**Desired behavior:** Do not prescribe a specific mechanical correction until evidence supports the underlying mechanical hypothesis.

### Overconfidence from limited evidence

Early output assigned Medium or High confidence to explanations based on two at-bats from a single game.

**Desired behavior:** Confidence should reflect athlete-specific evidence quantity and quality.

### Psychological inference

The model sometimes inferred anxiety, confidence loss, or mental pressure from subjective descriptions such as “uncomfortable.”

**Desired behavior:** Psychological explanations should remain explicitly hypothetical unless supported by stronger evidence.

### Subjective-to-objective transformation

A tennis observation that the athlete “seemed to slow down her swing” was rewritten as:

> “Swing speed appeared to decrease.”

This risks converting a subjective observation into an objective-sounding measurement.

**Desired behavior:** Preserve the epistemic quality of the source observation.

### Invented specificity

The model generated recommendations such as:

> “10–15 repetitions”

and:

> “Track over the next 3–5 games.”

These quantities were not provided by the user and were not necessarily evidence-based.

**Desired behavior:** Avoid unsupported precision.

These failures became evaluation cases rather than being addressed solely through ad hoc prompt tuning.

---

## 11. v0.2 — Athlete History & Longitudinal Reasoning

### Status
Complete

### Objective

Extend the v0.1 single-session reasoning prototype into a persistent athlete development system that can reason across observations over time.

### Capabilities

- Create and persist athlete profiles
- Select existing athletes in the product UI
- Store dated game and practice observations
- Maintain separate records for human-provided evidence and AI-generated analysis
- Retrieve prior observations for a specific athlete
- Filter historical evidence based on session date
- Provide prior human observations to the AI as longitudinal context
- Compare current observations with historical evidence
- Identify repeated patterns, contradictory evidence, and context-specific differences
- Display persistent athlete session history in the product UI

### Original persistence architecture

v0.2 introduced SQLite for local relational persistence during development.

The data model included:

**ATHLETE**
- athlete_id
- name
- age
- sport
- team
- position

**SESSION**
- session_id
- athlete_id
- session_date
- session_type
- observation
- analysis_json

Human observations and AI-generated interpretations were deliberately stored separately.

Historical AI hypotheses are not automatically supplied to the model as evidence in future analyses. This prevents model-generated speculation from recursively becoming treated as fact.

### Longitudinal context flow

**Selected Athlete  
→ Retrieve prior human observations  
→ Apply temporal filtering  
→ Format evidence with explicit provenance  
→ Claude structured analysis**

### Key Product Principle

**Persistent memory is not the same as model context.**

The application controls which stored information becomes evidence for each AI analysis rather than relying on the model to remember prior interactions.

---

## 12. v0.3 — Evaluation Framework & Reasoning Guardrails

### Status
Complete

### Objective

Move from manual inspection of plausible-looking AI responses to repeatable evaluation of reasoning behavior and enforce critical product invariants that prompt instructions alone cannot reliably guarantee.

### Evaluation Framework

The prototype includes reusable evaluation cases representing different sports, evidence conditions, and known model failure modes.

Each case contains:

- Athlete context
- Current human-reported observation
- Relevant prior human-reported evidence
- Behavioral evaluation criteria

The evaluation system generates a structured development analysis and evaluates the response against explicit PASS/FAIL criteria.

An LLM judge provides repeatable evaluation of behavioral criteria and a rationale for each result. The LLM judge is treated as an evaluation aid rather than ground truth.

### Core Evaluation Behaviors

Evaluation criteria include:

- No unsupported mechanical diagnosis
- No unsupported psychological diagnosis
- Hypotheses grounded in athlete-specific evidence
- Appropriate abstention when causal evidence is insufficient
- Preservation of contradictory evidence
- Preservation of subjective-report provenance
- Confidence calibrated to evidence quality
- No invented facts, measurements, repetitions, or history
- No unsupported mechanical correction
- Requests for evidence that can distinguish among explanations
- Constructive, age-appropriate recommendations

### Evidence-Grounding Rules

1. Every causal hypothesis must be supported by athlete-specific evidence.
2. A theoretically possible cause is not automatically an evidence-supported hypothesis.
3. When only an outcome is known, the system may return no causal hypothesis rather than inventing one.
4. Contextual contrasts can support cautious, low-confidence hypotheses when the athlete's own history provides evidence for the contrast.
5. Subjective reports must retain their original provenance.
6. Unknown provenance must remain unknown.
7. Uncertainty must propagate into development priorities, recommendations, and coaching cues.

### Deterministic Guardrail

Prompt instructions alone were not sufficient to enforce every reasoning invariant.

The application therefore applies deterministic post-processing after structured model generation.

The core invariant is:

**A causal development priority cannot exist unless it traces back to an evidence-supported hypothesis.**

Development priorities with invalid hypothesis relationships are removed.

Practice recommendations and coaching cues must similarly trace to valid development priorities.

This provides a structural backstop around probabilistic model behavior.

### Validated Evaluation Cases

The v0.3 evaluation suite includes baseball and tennis scenarios designed around previously observed model failure modes.

Final regression runs passed all defined criteria for both initial evaluation cases.

The purpose of these tests is not to prove that the model is always correct. They demonstrate that known reasoning failures can be represented as repeatable product requirements and tested after changes to the system.

---

## 13. v0.4 — Voice-First Evidence Capture & Post-Session Analysis

### Status
Complete

### Objective

Redesign observation capture around the real environment of a youth coach.

The earlier prototype treated each observation as the beginning of an AI-analysis interaction. That created unnecessary friction for a coach who may need to record several observations while actively running a practice or game.

v0.4 separates rapid evidence capture from longitudinal AI reasoning.

### Capture-First Workflow

**Select Athlete  
→ Record Voice Note  
→ Transcribe  
→ Review/Edit  
→ Save Observation  
→ Ready for Next Observation**

AI analysis is not required during this workflow.

The coach can capture evidence quickly and continue coaching without waiting for the reasoning model.

### Voice Transcription

The application uses Streamlit's native audio input for recording and OpenAI speech-to-text for transcription.

The transcript is presented as an editable observation before persistence.

The original design principle remains unchanged:

**Human-provided evidence should be preserved before AI interpretation.**

Voice is therefore treated as an input mechanism rather than an additional reasoning source.

### Capture Reset

After a successful save:

- The observation is persisted to the selected athlete's history.
- The audio recorder resets.
- The transcript field clears.
- The interface is immediately ready for another observation.

### Post-Session Development Analysis

AI reasoning is a separate user action.

The coach can request a Development Analysis across the athlete's accumulated human-reported observation history.

The analysis considers the evidence chronologically and looks for:

- Repeated patterns
- Contradictions
- Context-specific differences
- Evidence that strengthens or weakens hypotheses
- Changes or adjustments over time

The same structured output schema, evidence-grounding policy, and deterministic guardrails introduced in earlier versions remain in effect.

### Analysis Persistence

Whole-history Development Analysis is currently generated on demand and is not attached to an individual session.

This is intentional.

A longitudinal analysis represents reasoning across multiple observations, so storing it as though it belonged to the most recent observation would misrepresent its provenance.

A future version may introduce a separate assessment entity for persistent longitudinal analyses.

### Validated End-to-End Flow

**Voice Observation  
→ Speech-to-Text  
→ Human Review  
→ Save Human-Reported Evidence  
→ Persistent Athlete History  
→ Longitudinal Evidence Retrieval  
→ Structured AI Reasoning  
→ Deterministic Guardrails  
→ Development Analysis**

Generating a Development Analysis does not create a new observation or alter the athlete's evidence history.

### Product Insight

Voice capture is not itself the core product differentiator.

Its value is reducing the friction required to build a useful longitudinal evidence record.

The differentiated product behavior is the system's treatment of:

- Evidence provenance
- Uncertainty
- Contradictory observations
- Longitudinal patterns
- Abstention
- Separation of human evidence from AI inference
- Guardrails between hypotheses and interventions

---

## 14. v0.5 — Independent Deployment & Hosted Persistence

### Status
Complete

### Objective

Move the working prototype from a developer-dependent environment into an independently accessible field-test application.

The application should be usable by a remote coach without requiring the developer's computer, Google Colab runtime, or temporary Cloudflare tunnel to remain active.

### Hosted persistence

v0.5 replaces runtime-dependent SQLite persistence with Supabase Postgres.

Athlete profiles and session observations now persist independently of:

- The Streamlit application process
- Google Colab
- The developer's computer
- Browser sessions
- Application restarts

The existing athlete/session relational model is retained while moving its persistence layer to hosted Postgres.

### Independent deployment

The application is deployed through Streamlit Community Cloud from the GitHub repository.

This creates a stable browser-accessible application rather than a temporary development tunnel.

### Server-side credentials

The deployed application retrieves Anthropic, OpenAI, and Supabase credentials from server-side Streamlit secrets.

Credentials are not stored in the public GitHub repository or exposed to the browser.

### Field-test access control

A shared password gate protects the application during limited field testing.

Authentication state is maintained for the active Streamlit session.

This is intentionally a lightweight field-test mechanism rather than a production authentication system.

A broader release would require stronger user identity and authorization controls.

### Cloud persistence validation

The deployed application has successfully:

- Retrieved an existing athlete from Supabase
- Retrieved previously stored athlete history
- Created observations through the hosted Streamlit application
- Persisted those observations to Supabase
- Retained data independently of the original Colab runtime

### Mobile validation

The permanent deployed application has been tested from a mobile browser.

The validated mobile workflow includes:

**Open deployed application  
→ Authenticate  
→ Select athlete  
→ Record voice observation  
→ Transcribe  
→ Review/edit transcript  
→ Save  
→ Persist to Supabase  
→ Update athlete history**

This establishes that the primary field workflow can operate without a desktop development environment.

### Deployment Architecture

**Coach Phone / Browser  
→ Password-Protected Streamlit Cloud Application  
→ OpenAI Speech-to-Text  
→ Human-Reviewed Observation  
→ Supabase Postgres  
→ Longitudinal Evidence Retrieval  
→ Claude Reasoning  
→ Pydantic Structured Output  
→ Deterministic Guardrails  
→ Development Analysis**

### v0.5 Completion Criteria

- Stable browser URL — Complete
- No Colab runtime dependency — Complete
- No temporary Cloudflare dependency — Complete
- Hosted persistent athlete/session data — Complete
- Server-side API/database credentials — Complete
- Basic field-test access control — Complete
- Cloud read/write validation — Complete
- Mobile browser validation — Complete
- Mobile voice capture and transcription — Complete
- Persistent mobile observation save — Complete

The application is therefore ready for remote coach field testing.

---

## 15. Future Structured & Multimodal Evidence

The current evidence record primarily contains human-reported observations.

Future versions can introduce additional evidence types while preserving explicit provenance.

### Scorecard / Box-Score Ingestion

A likely next evidence workflow is:

**Upload game record  
→ AI extraction  
→ Structured performance evidence  
→ Human review/correction  
→ Verified evidence  
→ Athlete record  
→ Longitudinal reasoning**

Potential inputs include:

- GameChanger or similar box-score screenshots
- Digital scorecards
- Paper scorebook photographs
- PDF game reports
- Other structured game summaries

AI-extracted information should not automatically become verified athlete evidence.

The coach should be able to review and correct extracted information before it enters the longitudinal record.

Structured game evidence should remain distinguishable from:

- Coach-reported observations
- Parent-reported observations
- AI-generated hypotheses

### Video Evidence

A later version may accept video from games or practices.

Potential flow:

**Video → Vision Analysis → Structured Observations → Human Review → Athlete Evidence Record → Longitudinal Reasoning**

Video should function primarily as an additional evidence source rather than replacing the core reasoning architecture.

Potential capabilities include:

- Identifying observable movement or timing patterns
- Comparing repeated attempts
- Extracting events from game/practice footage
- Supporting or contradicting human-reported observations
- Tracking visible changes over time

Multimodal analysis should not imply precision beyond what video quality, camera angle, frame rate, and model capabilities can support.

---

## 16. Evaluation Strategy

The product should maintain a repeatable set of test scenarios covering multiple sports and evidence conditions.

Evaluation dimensions should include:

**Observation fidelity:** Did the system preserve what was actually reported?

**Inference discipline:** Did it clearly distinguish hypotheses from facts?

**Confidence calibration:** Does confidence appropriately reflect evidence quality and quantity?

**Unsupported specificity:** Did the system invent measurements, repetitions, timelines, or history?

**Recommendation safety:** Are recommendations appropriate given uncertainty?

**Cross-sport generalization:** Does the reasoning framework work without sport-specific hard-coding?

**Longitudinal reasoning:** Does new evidence appropriately strengthen, weaken, contradict, or leave unresolved existing hypotheses?

**Provenance preservation:** Does the system preserve the distinction between human observations, externally derived evidence, and AI-generated inference?

---

## 17. Success Criteria

The product succeeds when a coach can capture a simple observation and receive guidance that is:

- More structured than a generic chatbot response
- Explicit about uncertainty
- Useful without pretending to know more than the evidence supports
- Actionable without unnecessary prescription
- Capable of improving as evidence accumulates
- Applicable across multiple youth sports

The field workflow succeeds when a coach can:

- Access the application remotely
- Capture an observation quickly from a phone
- Review AI transcription before saving
- Build a persistent athlete history over time
- Generate longitudinal analysis when useful
- Use the application without developer infrastructure running

Technical success requires reliable structured output, secure server-side API usage, persistent athlete/session data, repeatable evaluation, and an independently deployable user interface.

---

## 18. Non-Goals

The product is not intended to:

- Replace a qualified sport-specific coach
- Provide medical diagnosis or injury assessment
- Provide mental-health diagnosis
- Claim biomechanical precision without appropriate evidence
- Guarantee athletic performance improvements
- Automatically treat AI-generated hypotheses as facts
- Automatically treat AI-extracted evidence as verified facts
- Optimize youth athletes solely around performance at the expense of development or enjoyment

---

## 19. Roadmap

### Completed

- v0.1 — Structured AI Reasoning
- v0.2 — Athlete History & Longitudinal Reasoning
- v0.3 — Evaluation Framework & Reasoning Guardrails
- v0.4 — Voice-First Evidence Capture & Post-Session Analysis
- v0.5 — Independent Deployment & Hosted Persistence

### Next Product Validation

- Conduct remote field testing with a youth coach during actual practices and games
- Measure whether voice capture is fast and unobtrusive enough for live coaching
- Identify friction in athlete selection, recording, transcript review, and repeated observation capture
- Observe when the coach chooses to generate Development Analysis
- Determine whether the longitudinal record provides enough value to maintain over time
- Use field behavior to prioritize the next feature rather than expanding the prototype speculatively

### Candidate v0.6 — Structured Game Evidence

Explore scorecard and box-score ingestion as the next evidence source.

Initial scope should favor a human-reviewed workflow rather than fully autonomous ingestion:

**Upload → Extract → Review → Correct → Save**

The field test should help determine which real-world formats to prioritize.

### Future Evidence Sources

- Video-derived observations with explicit provenance and confidence
- Human review of automatically extracted evidence before it enters the athlete record
- Curated coaching knowledge retrieval separated from athlete-specific evidence

### Production Identity & Authorization

The shared password gate is intended only for limited field testing.

If the application expands to additional coaches, teams, parents, or athletes, future requirements should include:

- Individual user identity
- Team/athlete authorization
- Appropriate access boundaries
- More robust session management
- Privacy controls appropriate to youth athlete information

### Multimodal Extension

A future lab can explore tennis match video as a multimodal extension of the reasoning architecture developed here.

The intended architecture is:

**Video  
→ Event Detection  
→ Structured Visual Observations  
→ Human Review  
→ Athlete Evidence Record  
→ Longitudinal Reasoning**

The objective is not to recreate specialized sports-video analytics products, but to test how externally generated or model-generated evidence can safely enter an evidence-aware longitudinal reasoning system.
