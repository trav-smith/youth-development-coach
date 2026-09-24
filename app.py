
import streamlit as st
import json
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

    return message.parsed_output


# -------------------------
# User interface
# -------------------------

# DATABASE — v0.2 Athlete History
# ============================================================

import sqlite3
import os

DB_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "youth_coach.db"
)


def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS athletes (
        athlete_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        sport TEXT NOT NULL,
        team TEXT,
        position TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER NOT NULL,
        session_date TEXT NOT NULL,
        session_type TEXT NOT NULL,
        observation TEXT NOT NULL,
        analysis_json TEXT,
        FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_id)
    )
    """)

    conn.commit()
    conn.close()


init_database()


def create_athlete(name, age, sport, team=None, position=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO athletes (
        name,
        age,
        sport,
        team,
        position
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        age,
        sport,
        team,
        position
    ))

    athlete_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return athlete_id


def get_athletes():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        athlete_id,
        name,
        age,
        sport,
        team,
        position
    FROM athletes
    ORDER BY name
    """)

    athletes = cursor.fetchall()
    conn.close()

    return athletes





def get_session_history(athlete_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        session_id,
        session_date,
        session_type,
        observation,
        analysis_json
    FROM sessions
    WHERE athlete_id = ?
    ORDER BY session_date DESC, session_id DESC
    """, (athlete_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_athlete_history(athlete_id, through_date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        session_date,
        session_type,
        observation
    FROM sessions
    WHERE athlete_id = ?
      AND session_date <= ?
    ORDER BY session_date ASC, session_id ASC
    """, (
        athlete_id,
        str(through_date)
    ))

    rows = cursor.fetchall()
    conn.close()

    return rows



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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sessions (
        athlete_id,
        session_date,
        session_type,
        observation,
        analysis_json
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        athlete_id,
        session_date,
        session_type,
        observation,
        analysis_json
    ))

    session_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return session_id


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

            history = get_athlete_history(athlete_id, session_date)

            history_context = format_history_for_ai(history)

            analysis = analyze_observation(
                athlete_name=athlete_name,
                sport=sport,
                age=age,
                team=team,
                position=position,
                session_type=session_type,
                observation_text=observation_text,
                history_context=history_context
            )

            analysis_json = analysis.model_dump_json()

            session_id = save_session(
                athlete_id=athlete_id,
                session_date=str(session_date),
                session_type=session_type,
                observation=observation_text.strip(),
                analysis_json=analysis_json
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

