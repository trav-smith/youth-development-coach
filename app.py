
import streamlit as st
from anthropic import Anthropic
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
"""


# -------------------------
# AI engine
# -------------------------

def analyze_observation(
    sport,
    age,
    session_type,
    observation_text,
    athlete_name=None,
    team=None,
    position=None
):

    client = Anthropic(
        api_key=st.secrets["ANTHROPIC_API_KEY"]
    )

    user_input = f"""
    Athlete name/nickname: {athlete_name or "Not provided"}
    Sport: {sport}
    Athlete age: {age}
    Team: {team or "Not provided"}
    Position/role: {position or "Not provided"}
    Session type: {session_type}

    Parent/coach observation:
    {observation_text}
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

    return message.parsed_output


# -------------------------
# User interface
# -------------------------

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

athlete_name = st.text_input(
    "Name or nickname"
)

age = st.number_input(
    "Age",
    min_value=5,
    max_value=18,
    value=12,
    step=1
)

sport = st.text_input(
    "Sport",
    value="Baseball"
)

team = st.text_input(
    "Team (optional)"
)

position = st.text_input(
    "Position or role (optional)"
)

st.header("Session")

session_type = st.selectbox(
    "Session type",
    ["Game", "Practice"]
)

observation_text = st.text_area(
    "What did you observe?",
    placeholder=(
        "Example: Struck out twice today. Both times he was late "
        "on fastballs. He looked uncomfortable when he got behind "
        "in the count and started swinging defensively."
    ),
    height=150
)

analyze_button = st.button(
    "Analyze",
    type="primary"
)


# -------------------------
# Run analysis + display results
# -------------------------

if analyze_button:

    if not observation_text.strip():
        st.warning("Please enter an observation before analyzing.")

    else:
        with st.spinner("Analyzing observations..."):

            analysis = analyze_observation(
                athlete_name=athlete_name,
                sport=sport,
                age=age,
                team=team,
                position=position,
                session_type=session_type,
                observation_text=observation_text
            )

        st.divider()
        st.header("Development Analysis")

        st.subheader("Observed")
        for item in analysis.observations:
            st.write(f"• {item.text}")

        st.subheader("Possible Explanations")
        for hypothesis in analysis.hypotheses:
            st.write(
                f"**{hypothesis.hypothesis}** "
                f"— {hypothesis.confidence} confidence"
            )

        st.subheader("Development Priorities")
        for priority in analysis.development_priorities:
            st.write(f"• {priority.priority}")

        st.subheader("Next Practice")
        for practice in analysis.practice_recommendations:
            st.write(f"• {practice.recommendation}")

        st.subheader("Coaching Cues")
        for cue in analysis.coaching_cues:
            st.write(f"• {cue.cue}")

        st.subheader("What to Track Next")
        for item in analysis.things_to_track_next:
            st.write(f"• {item.item}")

        st.subheader("Overall Confidence")
        st.write(f"**{analysis.overall_confidence.rating}**")
        st.write(analysis.overall_confidence.rationale)
