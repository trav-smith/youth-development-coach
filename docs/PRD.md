# Youth Development Coach
## Product Requirements Document

**Version:** 0.4  
**Status:** Prototype Complete  
**Product:** AI Sports Labs  
**Last Updated:** September 25, 2026

1. Product Overview
Youth Development Coach is an AI-powered tool that helps parents and coaches turn observations from youth sports games and practices into structured, evidence-aware development guidance.
Parents frequently observe meaningful patterns — an athlete struggling against fastballs, becoming tentative after mistakes, losing serve consistency later in a match, or performing differently in practice than competition — but may lack the expertise or objective evidence necessary to determine why the pattern is occurring.
Traditional generative AI can provide immediate advice, but often moves too quickly from an observation to a diagnosis or recommendation.
Youth Development Coach is designed around a different principle:
Observe first. Hypothesize second. Intervene carefully. Learn over time.
Rather than treating a single observation as proof of a problem, the product separates reported observations from AI inference, maintains competing hypotheses when evidence is incomplete, communicates confidence, recommends low-risk next actions, and identifies evidence that should be collected next.
Over time, the product is intended to build a longitudinal understanding of an individual athlete.

2. Problem
Parents and youth coaches regularly face three related challenges.
Limited expertise: A parent may recognize that something changed without knowing the technical, physical, tactical, or psychological cause.
Limited evidence: Youth athlete development decisions are often based on a small number of games, practices, or memorable moments.
Premature conclusions: Both humans and AI systems can convert limited observations into confident diagnoses and corrective advice.
For example:
“My 12-year-old struck out twice and was late on fastballs.”
Possible explanations could include timing, pitch recognition, velocity, mechanics, approach, normal performance variance, or some combination of factors.
A useful development tool should not automatically select one explanation. It should help the user determine what is known, what is possible, and what evidence would distinguish among those possibilities.

3. Target Users

Primary user: Youth coach seeking a low-friction way to capture athlete observations during games and practices, maintain a longitudinal development record, and reason across evidence over time.

Secondary user: Parent of a youth athlete who wants to support development while avoiding premature conclusions from isolated performances.

Athlete: Youth athlete approximately ages 5–18 participating in organized or recreational sports.

The initial reasoning architecture is designed to be sport-general rather than tied to a single sport. Baseball is the primary workflow context for the current coach-facing prototype, with tennis used as a secondary test of cross-sport generalization.

The product is intended to support — not replace — the judgment of coaches, parents, and athletes.

4. Product Principles
Evidence before diagnosis
Reported observations should remain distinct from AI-generated interpretations.
Uncertainty should be visible
The system should communicate when available evidence is insufficient to support a conclusion.
Competing hypotheses are valuable
When several explanations fit the available evidence, the system should preserve those alternatives rather than prematurely selecting one.
Recommendations should match confidence
Low-confidence analysis should favor observation, measurement, and low-risk practice activities rather than highly specific corrective interventions.
Development should remain constructive
Recommendations and coaching language should be age-appropriate, positive, and useful to parents and youth coaches.
Athlete context should accumulate
Individual sessions provide weak evidence. Repeated observations across games and practices can reveal stronger patterns.
AI output requires evaluation
Structured output does not guarantee correct reasoning. Model behavior must be tested for unsupported inference, invented details, overconfidence, and inappropriate recommendations.

5. Core User Journey

Step 1 — Select athlete

The coach selects an existing athlete or creates a new athlete profile containing:
- Name or nickname
- Age
- Sport
- Team, optional
- Position or role, optional

Step 2 — Capture observation

During a game or practice, the coach records a quick voice note or enters an observation as text.

For voice capture:
- The coach records the observation in the Streamlit interface.
- Speech-to-text converts the recording into a transcript.
- The transcript remains editable so the coach can verify or correct it before saving.

Step 3 — Save evidence

The reviewed observation is saved immediately to the athlete's longitudinal history.

Saving evidence does not require AI analysis.

This separation allows the coach to capture multiple observations without waiting for the reasoning model and preserves the human-reported evidence before interpretation.

Step 4 — Review athlete history

Saved game and practice observations accumulate chronologically in the athlete's persistent record.

The coach can review this history independently of AI-generated analysis.

Step 5 — Generate Development Analysis

When useful, the coach requests a Development Analysis across the athlete's accumulated human-reported evidence.

The reasoning engine looks for:
- Repeated patterns
- Contradictory evidence
- Context-specific differences
- Evidence that strengthens or weakens hypotheses
- Changes or adjustments over time

Step 6 — Receive structured guidance

The user receives:
- Observed
- Possible Explanations
- Development Priorities
- Next Practice
- Coaching Cues
- What to Track Next
- Overall Confidence

Step 7 — Continue the evidence loop

Future observations are added to the athlete record and can strengthen, weaken, contradict, or leave unresolved earlier explanations.

The intended loop is:

Capture → Preserve Evidence → Analyze → Track → Capture Again

6. v0.1 — Working Prototype
Status: Implemented
The current prototype accepts athlete and session information through a Streamlit interface and sends the observation to Claude through the Anthropic API.
Claude produces a structured response enforced through Pydantic models.
Current Inputs
Athlete name/nickname
Age
Sport
Team
Position/role
Session type
Natural-language observation
Current Outputs
Direct observations
Competing hypotheses
Hypothesis confidence
Development priorities
Practice recommendations
Coaching cues
Future tracking recommendations
Overall confidence and rationale
Validated Sports
Initial tests successfully produced relevant output for:
Baseball
Tennis
No sport-specific application logic was required, supporting the initial hypothesis that the reasoning architecture can generalize across sports.

7. AI Reasoning Requirements
The AI analysis engine should:
Separate directly reported observations from inference.
Never represent a hypothesis as an established fact.
Avoid diagnosing mechanical, physical, or psychological problems without sufficient evidence.
Preserve competing hypotheses when multiple explanations are plausible.
Recommend no more than two primary development priorities.
Provide age-appropriate and constructive guidance.
Identify additional evidence that could confirm or reject hypotheses.
Express confidence as Low, Medium, or High.
Base confidence on evidence about the individual athlete rather than the general prevalence of an issue.
Normally maintain low confidence when evidence comes from a single game, practice, or small number of observations.
Avoid specific mechanical corrections when the underlying mechanical cause remains uncertain.
Favor observation and low-risk experimentation when evidence is limited.
Ensure coaching cues are consistent with the uncertainty of the analysis.
Avoid inventing repetitions, training frequency, measurements, history, or other facts not provided by the user.
Preserve subjective parent/coach descriptions as reported observations rather than converting them into objective measurements.

8. Structured Output Architecture
The application uses a defined Pydantic schema rather than accepting unrestricted natural-language output from the model.
Core entities include:
Observation
Directly reported information.
Hypothesis
A possible explanation linked to supporting observation IDs, missing evidence, and confidence.
Development Priority
A recommended focus linked to one or more hypotheses.
Practice Recommendation
A potential practice action linked to a development priority.
Coaching Cue
Simple athlete-facing language linked to a development priority.
Tracking Item
Evidence to collect in future sessions linked to relevant hypotheses.
Overall Confidence
System-level confidence rating and rationale.
Stable IDs allow relationships among these objects without relying on fragile text matching.

9. Technical Architecture — v0.1
Current application flow:
User → Streamlit → Python → Anthropic API → Claude → Pydantic Structured Output → Streamlit Results
Key technologies:
Python
Google Colab
Streamlit
Anthropic API
Claude Sonnet
Pydantic
Google Drive for persistent development artifacts
GitHub planned for source control and portfolio publication
API credentials are stored separately from application source code and are not embedded in the repository.

10. Known v0.1 Limitations and Evaluation Cases
Initial testing revealed several important LLM reliability issues.
Unsupported mechanical prescriptions
Early output recommended cues such as:
“Get your foot down early.”
The available evidence did not establish that foot timing was the cause of the athlete's difficulty.
Desired behavior: Do not prescribe a specific mechanical correction until evidence supports the underlying mechanical hypothesis.
Overconfidence from limited evidence
Early output assigned Medium or High confidence to explanations based on two at-bats from a single game.
Desired behavior: Confidence should reflect athlete-specific evidence quantity and quality.
Psychological inference
The model sometimes inferred anxiety, confidence loss, or mental pressure from subjective descriptions such as “uncomfortable.”
Desired behavior: Psychological explanations should remain explicitly hypothetical unless supported by stronger evidence.
Subjective-to-objective transformation
A tennis observation that the athlete “seemed to slow down her swing” was rewritten as:
“Swing speed appeared to decrease.”
This risks converting a subjective observation into an objective-sounding measurement.
Desired behavior: Preserve the epistemic quality of the source observation.
Invented specificity
The model generated recommendations such as:
“10–15 repetitions”
and
“Track over the next 3–5 games.”
These quantities were not provided by the user and were not necessarily evidence-based.
Desired behavior: Avoid unsupported precision.
These examples should become initial cases in a formal evaluation suite rather than relying solely on manual prompt testing.

11.v0.2 — Athlete History & Longitudinal Reasoning

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
- Store structured AI analysis separately from source observations
- Display persistent athlete session history in the product UI

### Persistence Architecture

The prototype uses SQLite for local relational persistence.

ATHLETE
- athlete_id
- name
- age
- sport
- team
- position

SESSION
- session_id
- athlete_id
- session_date
- session_type
- observation
- analysis_json

Human observations and AI-generated interpretations are deliberately stored separately.

Historical AI hypotheses are not automatically supplied to the model as evidence in future analyses. This prevents model-generated speculation from recursively becoming treated as fact.

### Longitudinal Context Flow

Selected Athlete
→ Retrieve prior human observations
→ Apply temporal filtering
→ Format evidence with explicit provenance
→ Combine historical evidence with current observation
→ Claude structured analysis
→ Save current human observation and AI analysis separately

### Current Limitations

- Same-day sessions are ordered by database insertion rather than actual event time.
- Historical context currently includes all qualifying prior human observations rather than selecting observations by relevance.
- SQLite is appropriate for prototype development but is not the intended production persistence layer.
- AI reasoning still requires evaluation for unsupported specificity, confidence calibration, mechanical prescriptions, and subjective-to-objective evidence drift.

### Key Product Principle

Persistent memory is not the same as model context.

The application controls which stored information becomes evidence for each AI analysis rather than relying on the model to remember prior interactions.

12. v0.3 — Evaluation Framework & Reasoning Guardrails

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

The evaluation system generates a structured development analysis and then evaluates the response against explicit PASS/FAIL criteria.

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

v0.3 strengthened the reasoning policy with several additional requirements:

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

13. v0.4 — Voice-First Evidence Capture & Post-Session Analysis

### Status
Complete

### Objective
Redesign observation capture around the real environment of a youth coach.

The earlier prototype treated each observation as the beginning of an AI-analysis interaction. That created unnecessary friction for a coach who may need to record several observations while actively running a practice or game.

v0.4 separates rapid evidence capture from longitudinal AI reasoning.

### Capture-First Workflow

The on-field workflow is:

Select Athlete
→ Record Voice Note
→ Transcribe
→ Review/Edit
→ Save Observation
→ Ready for Next Observation

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

This supports repeated capture during a game or practice.

### Post-Session Development Analysis

AI reasoning is now a separate user action.

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

The v0.4 prototype has validated the following workflow:

Voice Observation
→ Speech-to-Text
→ Human Review
→ Save Human-Reported Evidence
→ Persistent Athlete History
→ Longitudinal Evidence Retrieval
→ Structured AI Reasoning
→ Deterministic Guardrails
→ Development Analysis

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

14. Future Multimodal Capability
A later version may accept video from games or practices.
Potential flow:
Video → Vision Analysis → Structured Observations → Existing Reasoning Pipeline
Video should function primarily as an additional evidence source rather than replacing the core reasoning architecture.
Potential capabilities include:
Identifying observable movement or timing patterns
Comparing repeated attempts
Extracting events from game/practice footage
Supporting or contradicting parent-reported observations
Tracking visible changes over time
Multimodal analysis should not imply precision beyond what the video quality, camera angle, frame rate, and model capabilities can support.

15. Evaluation Strategy
The product should maintain a repeatable set of test scenarios covering multiple sports and evidence conditions.
Evaluation dimensions should include:
Observation fidelity: Did the system preserve what was actually reported?
Inference discipline: Did it clearly distinguish hypotheses from facts?
Confidence calibration: Does confidence appropriately reflect evidence quality and quantity?
Unsupported specificity: Did the system invent measurements, repetitions, timelines, or history?
Recommendation safety: Are recommendations appropriate given uncertainty?
Cross-sport generalization: Does the reasoning framework work without sport-specific hard-coding?
Longitudinal reasoning: Does new evidence appropriately strengthen, weaken, contradict, or leave unresolved existing hypotheses?

16. Success Criteria
The product succeeds when a parent or coach can enter a simple observation and receive guidance that is:
More structured than a generic chatbot response
Explicit about uncertainty
Useful without pretending to know more than the evidence supports
Actionable without unnecessary prescription
Capable of improving as evidence accumulates
Applicable across multiple youth sports
Technical success requires reliable structured output, secure API usage, persistent athlete/session data, repeatable evaluation, and a deployable user interface.

17. Non-Goals
The product is not intended to:
Replace a qualified sport-specific coach
Provide medical diagnosis or injury assessment
Provide mental-health diagnosis
Claim biomechanical precision without appropriate evidence
Guarantee athletic performance improvements
Automatically treat AI-generated hypotheses as facts
Optimize youth athletes solely around performance at the expense of development or enjoyment

18. Roadmap

### Completed

- v0.1 — Structured AI Reasoning
- v0.2 — Athlete History & Longitudinal Reasoning
- v0.3 — Evaluation Framework & Reasoning Guardrails
- v0.4 — Voice-First Evidence Capture & Post-Session Analysis

### Next Product Validation

- Conduct field testing with youth coaches during real practices
- Measure whether voice capture is fast and unobtrusive enough for live coaching
- Identify friction in athlete selection, recording, transcript review, and repeated observation capture
- Evaluate whether coaches find the resulting longitudinal record useful enough to maintain over time

### Future Evidence Sources

- Structured game statistics and box-score data
- Video-derived observations with explicit provenance and confidence
- Human review of automatically extracted evidence before it enters the athlete record
- Curated coaching knowledge retrieval separated from athlete-specific evidence

### Multimodal Extension

A future lab will explore tennis match video as a multimodal extension of the reasoning architecture developed here.

The intended architecture is:

Video
→ Event Detection
→ Structured Visual Observations
→ Human Review
→ Athlete Evidence Record
→ Longitudinal Reasoning

The objective is not to recreate specialized sports-video analytics products, but to test how externally generated or model-generated evidence can safely enter an evidence-aware longitudinal reasoning system.
