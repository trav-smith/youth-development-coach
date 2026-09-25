
import streamlit as st
import json
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal


# -------------------------
# Structured AI output
# -------------------------

class Observation(BaseModel):
    id: str
    text: str


class Hypothesis(BaseModel):
    id: str
    hypothesis: str
    evidence_for_observation_ids: list[str]
    evidence_missing: list[str]
    confidence: Literal["Low", "Medium", "High"]


class DevelopmentPriority(BaseModel):
    id: str
    priority: str
    addresses_hypothesis_ids: list[str]


class PracticeRecommendation(BaseModel):
    id: str
    recommendation: str
    priority_ids: list[str]


class CoachingCue(BaseModel):
    id: str
    cue: str
    priority_ids: list[str]


class TrackingItem(BaseModel):
    id: str
    item: str
    hypothesis_ids: list[str]


class OverallConfidence(BaseModel):
    rating: Literal["Low", "Medium", "High"]
    rationale: str


class YouthCoachAnalysis(BaseModel):
    sport: str
    athlete_age: int | None
    observations: list[Observation]
    hypotheses: list[Hypothesis]
    development_priorities: list[DevelopmentPriority]
    practice_recommendations: list[PracticeRecommendation]
    coaching_cues: list[CoachingCue]
    things_to_track_next: list[TrackingItem]
    overall_confidence: OverallConfidence


# -------------------------
# AI behavior
# -------------------------

SYSTEM_PROMPT = """
You are the analysis engine for a youth athlete development product.

Your job is to help parents and coaches turn observations from games
and practices into useful, age-appropriate development guidance.

CORE RULES:

1. Separate directly observed facts from inference.

2. Never present a hypothesis as an established fact.

3. Do not diagnose a mechanical, physical, or psychological problem
   unless sufficient evidence has been provided.

4. When multiple explanations are plausible, preserve them as
   competing hypotheses rather than selecting one without evidence.

5. Recommend no more than two development priorities.

6. Recommendations must be age-appropriate, constructive, and
   understandable to a parent or youth coach.

7. Identify what additional evidence would help confirm or reject
   each hypothesis.

8. Confidence must be Low, Medium, or High.

9. Confidence reflects the strength and amount of evidence for THIS
   athlete, not how common a problem may be among athletes generally.

10. A single game, practice, or small number of observations should
    normally result in Low overall confidence unless unusually strong
    evidence is provided.

11. Do not prescribe a specific mechanical correction when the
    underlying mechanical cause is still only a hypothesis.

12. When evidence is limited, prefer low-risk observation, practice,
    or data-gathering recommendations over corrective interventions.

13. Coaching cues must not contradict the uncertainty of the analysis.
    If a mechanical issue has not been established, do not give a
    mechanical correction cue as though it has been established.

14. Do not invent training frequency, repetitions, measurements,
    athlete history, or other facts that were not supplied.

15. Treat parent/coach descriptions such as "late," "defensive,"
    "nervous," or "tired" as reported observations, not objective
    diagnoses.


16. Every hypothesis must be supported by athlete-specific evidence,
    not merely be a plausible cause of the observed outcome.

    Distinguish evidence from causal possibility. For example, observing
    that an athlete was late on fastballs establishes that the athlete
    was late; by itself it does not establish evidence of insufficient
    bat speed, poor pitch recognition, a long swing path, unusual pitcher
    velocity, or another possible cause.

    Include a causal hypothesis only when the supplied observations or
    history contain additional evidence that specifically points toward
    that explanation. Otherwise, identify the possible cause as missing
    evidence to investigate rather than promoting it to a hypothesis.

    Low confidence does not make an unsupported causal possibility
    evidence-grounded.


17. Match the hypothesis set to the strength of the athlete-specific
    evidence.

    If the evidence establishes only an outcome and contains no
    additional evidence pointing toward why it occurred:
    - return an empty hypotheses list
    - keep overall confidence Low
    - use things_to_track_next to identify evidence that could support
      or distinguish possible explanations

    If additional athlete-specific evidence points toward an explanation,
    that explanation may be included as a Low-confidence hypothesis even
    though causation has not been established. Preserve the distinction
    between evidence that supports a hypothesis and proof that the
    hypothesis is true.

    Contrasting observations across contexts may support a contextual
    hypothesis when the difference itself is observed. A subjective
    parent or coach report may contribute evidence, but must remain
    explicitly attributed and must not be converted into an objective
    psychological diagnosis.

    Recommendations and coaching cues must preserve the same uncertainty
    as the hypotheses. Do not design an intervention around an unconfirmed
    cause as though that cause has been established.

    Do not generate hypotheses merely to populate the hypotheses field.
    It is better to return no causal hypothesis than to present an
    unsupported possibility as an athlete-specific hypothesis.


18. Recommendations, development priorities, and coaching cues must
    preserve the uncertainty of the hypotheses they address.

    A Low-confidence hypothesis must not be converted downstream into
    an established problem to fix. When the cause remains uncertain,
    prefer actions that:
    - gather evidence that could confirm or reject the hypothesis
    - are useful across multiple plausible explanations
    - are low-risk even if the hypothesis is wrong

    For example, if match context or nervousness is only a
    Low-confidence hypothesis, do not state that the athlete needs to
    build confidence, manage nerves, or correct a psychological problem
    as though that cause has been established.

    For youth athletes, do not use physical conditioning, punishment,
    punitive consequences, embarrassment, or extra exercise as a
    consequence for performance mistakes. Practice activities should
    support skill development, learning, confidence, and useful
    observation rather than punish errors.


19. Preserve the provenance of observations exactly as supplied.

    Do not invent or infer who made an observation. If the input does
    not specify whether an observation came from a parent, coach,
    athlete, video, sensor, or another source, do not add a source
    attribution.

    When a source is explicitly supplied, preserve that distinction.
    For example, "her parent said she looked nervous" must remain an
    attributed parent report rather than becoming the objective fact
    "she was nervous."

    Unknown provenance must remain unknown.
"""


# -------------------------
# AI engine
# -------------------------


def apply_reasoning_guardrails(analysis):
    valid_hypothesis_ids = {
        hypothesis.id
        for hypothesis in analysis.hypotheses
    }

    # Keep only priorities that trace to at least one valid hypothesis.
    valid_priorities = [
        priority
        for priority in analysis.development_priorities
        if priority.addresses_hypothesis_ids
        and set(priority.addresses_hypothesis_ids).issubset(
            valid_hypothesis_ids
        )
    ]

    valid_priority_ids = {
        priority.id
        for priority in valid_priorities
    }

    # Keep recommendations and cues only when all referenced priorities
    # survived the hypothesis-grounding check.
    valid_recommendations = [
        recommendation
        for recommendation in analysis.practice_recommendations
        if recommendation.priority_ids
        and set(recommendation.priority_ids).issubset(
            valid_priority_ids
        )
    ]

    valid_cues = [
        cue
        for cue in analysis.coaching_cues
        if cue.priority_ids
        and set(cue.priority_ids).issubset(
            valid_priority_ids
        )
    ]

    analysis.development_priorities = valid_priorities
    analysis.practice_recommendations = valid_recommendations
    analysis.coaching_cues = valid_cues

    return analysis


def analyze_observation(
    sport,
    age,
    session_type,
    observation_text,
    history_context,
    athlete_name=None,
    team=None,
    position=None
):

    client = Anthropic(
        api_key=st.secrets["ANTHROPIC_API_KEY"]
    )

    user_input = f"""
ATHLETE CONTEXT

Athlete name/nickname: {athlete_name or "Not provided"}
Sport: {sport}
Athlete age: {age}
Team: {team or "Not provided"}
Position/role: {position or "Not provided"}


PRIOR HUMAN-REPORTED OBSERVATIONS

{history_context}


CURRENT HUMAN-REPORTED OBSERVATION

Session type: {session_type}

{observation_text}


LONGITUDINAL REASONING INSTRUCTIONS

Use prior observations only as historical evidence supplied by the user.

Compare the current observation with prior observations.

Look for:
- repeated patterns
- contradictory evidence
- context-specific differences
- evidence that strengthens or weakens a hypothesis

Do not assume that a pattern exists simply because it appeared once before.

Do not treat previous AI hypotheses as evidence.

When current and prior observations conflict, preserve that uncertainty
and identify what additional evidence would help explain the difference.
"""

    message = client.messages.parse(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ],
        output_format=YouthCoachAnalysis
    )

    analysis = message.parsed_output

    analysis = apply_reasoning_guardrails(analysis)

    return analysis



def analyze_athlete_history(
    sport,
    age,
    history_context,
    athlete_name=None,
    team=None,
    position=None
):

    client = Anthropic(
        api_key=st.secrets["ANTHROPIC_API_KEY"]
    )

    user_input = f"""
ATHLETE CONTEXT

Athlete name/nickname: {athlete_name or "Not provided"}
Sport: {sport}
Athlete age: {age}
Team: {team or "Not provided"}
Position/role: {position or "Not provided"}


CHRONOLOGICAL HUMAN-REPORTED OBSERVATIONS

{history_context}


LONGITUDINAL REASONING INSTRUCTIONS

Analyze the athlete's human-reported observation history as a whole.

Look for:
- repeated patterns
- contradictory evidence
- context-specific differences
- evidence that strengthens or weakens a hypothesis
- changes or adjustments over time

Do not assume that a pattern exists simply because it appeared once.

Do not treat previous AI hypotheses as evidence.

When observations conflict, preserve that uncertainty and identify what
additional evidence would help distinguish between competing explanations.

Base the analysis only on the human-reported evidence provided above.
"""

    message = client.messages.parse(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ],
        output_format=YouthCoachAnalysis
    )

    analysis = message.parsed_output

    analysis = apply_reasoning_guardrails(analysis)

    return analysis


# -------------------------
# User interface
# -------------------------

# -------------------------
# Voice transcription
# -------------------------

def transcribe_audio(audio_file):
    openai_client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
    )

    transcription = openai_client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=(audio_file.name, audio_file.getvalue(), audio_file.type)
    )

    return transcription.text.strip()


# DATABASE — v0.5 Supabase
# ============================================================

from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_SECRET_KEY"]
)


def create_athlete(name, age, sport, team=None, position=None):
    response = (
        supabase.table("athletes")
        .insert({
            "name": name,
            "age": age,
            "sport": sport,
            "team": team,
            "position": position
        })
        .execute()
    )

    return response.data[0]["athlete_id"]


def get_athletes():
    response = (
        supabase.table("athletes")
        .select("athlete_id,name,age,sport,team,position")
        .order("name")
        .execute()
    )

    return [
        (
            row["athlete_id"],
            row["name"],
            row["age"],
            row["sport"],
            row["team"],
            row["position"]
        )
        for row in response.data
    ]


def get_session_history(athlete_id):
    response = (
        supabase.table("sessions")
        .select(
            "session_id,session_date,session_type,observation,analysis_json"
        )
        .eq("athlete_id", athlete_id)
        .order("session_date", desc=True)
        .order("session_id", desc=True)
        .execute()
    )

    return [
        (
            row["session_id"],
            row["session_date"],
            row["session_type"],
            row["observation"],
            row["analysis_json"]
        )
        for row in response.data
    ]


def get_athlete_history(athlete_id, through_date):
    response = (
        supabase.table("sessions")
        .select("session_date,session_type,observation")
        .eq("athlete_id", athlete_id)
        .lte("session_date", str(through_date))
        .order("session_date")
        .order("session_id")
        .execute()
    )

    return [
        (
            row["session_date"],
            row["session_type"],
            row["observation"]
        )
        for row in response.data
    ]


def format_history_for_ai(history):
    if not history:
        return "No prior observations are available."

    formatted_sessions = []

    for session_date, session_type, observation in history:
        formatted_sessions.append(
            f"""
Date: {session_date}
Session type: {session_type}
Human-reported observation:
{observation.strip()}
"""
        )

    return "\n---\n".join(formatted_sessions)


def save_session(
    athlete_id,
    session_date,
    session_type,
    observation,
    analysis_json=None
):
    response = (
        supabase.table("sessions")
        .insert({
            "athlete_id": athlete_id,
            "session_date": str(session_date),
            "session_type": session_type,
            "observation": observation,
            "analysis_json": analysis_json
        })
        .execute()
    )

    return response.data[0]["session_id"]


# FIELD-TEST ACCESS CONTROL
# ============================================================

import hmac


def require_password():
    if st.session_state.get("authenticated", False):
        return

    st.title("Youth Development Coach")
    st.write("Enter the field-test password to continue.")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Sign in"):
        if hmac.compare_digest(
            password,
            st.secrets["APP_PASSWORD"]
        ):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.stop()


require_password()


st.set_page_config(
    page_title="Youth Development Coach",
    page_icon="🏅",
    layout="centered"
)

st.title("Youth Development Coach")

st.write(
    "Turn observations from games and practices into "
    "focused development ideas for your athlete."
)


st.header("Athlete")

athletes = get_athletes()

if athletes:
    athlete_options = {
        f"{athlete[1]} — {athlete[3]}": athlete
        for athlete in athletes
    }

    selected_label = st.selectbox(
        "Select athlete",
        options=list(athlete_options.keys())
    )

    selected_athlete = athlete_options[selected_label]

    athlete_id = selected_athlete[0]
    athlete_name = selected_athlete[1]
    age = selected_athlete[2]
    sport = selected_athlete[3]
    team = selected_athlete[4]
    position = selected_athlete[5]

    athlete_details = [str(age), sport]

    if position:
        athlete_details.append(position)

    if team:
        athlete_details.append(team)

    st.caption(" • ".join(athlete_details))

else:
    st.info("No athletes have been added yet.")
    athlete_id = None
    athlete_name = None
    age = None
    sport = None
    team = None
    position = None



with st.expander("➕ Add New Athlete"):
    new_name = st.text_input(
        "Name or nickname",
        key="new_athlete_name"
    )

    new_age = st.number_input(
        "Age",
        min_value=5,
        max_value=18,
        value=12,
        step=1,
        key="new_athlete_age"
    )

    new_sport = st.text_input(
        "Sport",
        key="new_athlete_sport"
    )

    new_team = st.text_input(
        "Team (optional)",
        key="new_athlete_team"
    )

    new_position = st.text_input(
        "Position or role (optional)",
        key="new_athlete_position"
    )

    if st.button("Save Athlete"):
        if not new_name.strip() or not new_sport.strip():
            st.warning("Name and sport are required.")
        else:
            new_athlete_id = create_athlete(
                name=new_name.strip(),
                age=new_age,
                sport=new_sport.strip(),
                team=new_team.strip() or None,
                position=new_position.strip() or None
            )

            st.success(f"{new_name.strip()} added.")
            st.rerun()


st.header("Session")

session_date = st.date_input(
    "Date"
)

session_type = st.selectbox(
    "Session type",
    ["Game", "Practice"]
)

st.subheader("Capture Observation")

st.caption(
    "Record a quick voice note from the field, or type the observation below."
)

if "audio_input_version" not in st.session_state:
    st.session_state.audio_input_version = 0

audio_note = st.audio_input(
    "Record observation",
    sample_rate=16000,
    key=f"observation_audio_{st.session_state.audio_input_version}"
)

if st.session_state.pop("clear_observation_draft", False):
    st.session_state.observation_draft = ""

if "observation_draft" not in st.session_state:
    st.session_state.observation_draft = ""

if audio_note is not None:
    audio_bytes = audio_note.getvalue()

    if st.session_state.get("last_audio_bytes") != audio_bytes:
        with st.spinner("Transcribing voice note..."):
            try:
                st.session_state.observation_draft = transcribe_audio(audio_note)
                st.session_state.last_audio_bytes = audio_bytes
            except Exception as e:
                st.error(f"Voice transcription failed: {e}")

observation_text = st.text_area(
    "Review observation",
    key="observation_draft",
    placeholder="Record a voice note above or type an observation here.",
    height=150
)

save_button = st.button(
    "Save Observation",
    type="primary"
)


# -------------------------
# Save observation
# -------------------------

if save_button:

    if athlete_id is None:
        st.warning("Please select an athlete before saving.")

    elif not observation_text.strip():
        st.warning("Please record or enter an observation before saving.")

    else:
        session_id = save_session(
            athlete_id=athlete_id,
            session_date=str(session_date),
            session_type=session_type,
            observation=observation_text.strip(),
            analysis_json=None
        )

        st.session_state.clear_observation_draft = True
        st.session_state.audio_input_version += 1
        st.session_state.pop("last_audio_bytes", None)

        st.rerun()

# ============================================================

# ============================================================
# ATHLETE HISTORY
# ============================================================

if athlete_id is not None:
    st.divider()
    st.header("Athlete History")

    session_history = get_session_history(athlete_id)

    if not session_history:
        st.info("No sessions recorded yet.")

    else:
        st.caption(
            f"{len(session_history)} recorded "
            f"{'session' if len(session_history) == 1 else 'sessions'}"
        )

        for (
            history_session_id,
            history_date,
            history_type,
            history_observation,
            history_analysis_json
        ) in session_history:

            with st.expander(
                f"{history_date} • {history_type}"
            ):
                st.write(history_observation.strip())

                if history_analysis_json:
                    st.caption("AI analysis saved")
                else:
                    st.caption("No saved AI analysis")


# ============================================================
# DEVELOPMENT ANALYSIS — v0.4
# ============================================================

if athlete_id is not None:
    st.divider()
    st.header("Development Analysis")

    st.caption(
        "Generate an evidence-based analysis from this athlete's "
        "saved observation history."
    )

    generate_analysis_button = st.button(
        "Generate Development Analysis",
        type="secondary"
    )

    if generate_analysis_button:

        history = get_athlete_history(
            athlete_id,
            session_date
        )

        if not history:
            st.warning(
                "Save at least one observation before generating an analysis."
            )

        else:
            history_context = format_history_for_ai(history)

            with st.spinner("Analyzing athlete history..."):
                analysis = analyze_athlete_history(
                    athlete_name=athlete_name,
                    sport=sport,
                    age=age,
                    team=team,
                    position=position,
                    history_context=history_context
                )

            st.subheader("Observed")
            for item in analysis.observations:
                st.write(f"• {item.text}")

            st.subheader("Possible Explanations")
            if analysis.hypotheses:
                for hypothesis in analysis.hypotheses:
                    st.write(
                        f"**{hypothesis.hypothesis}** "
                        f"— {hypothesis.confidence} confidence"
                    )
            else:
                st.write(
                    "No evidence-supported causal explanation yet."
                )

            st.subheader("Development Priorities")
            if analysis.development_priorities:
                for priority in analysis.development_priorities:
                    st.write(f"• {priority.priority}")
            else:
                st.write(
                    "No causal development priority supported yet."
                )

            st.subheader("Next Practice")
            if analysis.practice_recommendations:
                for practice in analysis.practice_recommendations:
                    st.write(f"• {practice.recommendation}")
            else:
                st.write(
                    "Continue gathering observations before prescribing "
                    "a targeted intervention."
                )

            st.subheader("Coaching Cues")
            if analysis.coaching_cues:
                for cue in analysis.coaching_cues:
                    st.write(f"• {cue.cue}")
            else:
                st.write(
                    "No evidence-supported coaching cue yet."
                )

            st.subheader("What to Track Next")
            for item in analysis.things_to_track_next:
                st.write(f"• {item.item}")

            st.subheader("Overall Confidence")
            st.write(f"**{analysis.overall_confidence.rating}**")
            st.write(analysis.overall_confidence.rationale)

