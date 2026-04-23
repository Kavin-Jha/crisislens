# CLAUDE_REFINE.md — CrisisLens Complete Overhaul

Read this entire file before touching any code. This is a refinement pass on an already-working CrisisLens app. The following files are CORRECT and must NOT be modified under any circumstances:
- pipeline.py
- redteam.py
- session_store.py
- prompts.py
- sample_transcripts/

You are ONLY creating/replacing these files:
- app.py (full replacement)
- styles.py (new)
- report_generator.py (new)
- scenario_generator.py (new)
- comparative.py (new)

---

## Aesthetic Direction: "Clinical Precision"

This app must look like a medical audit dashboard — dark, precise, authoritative. Not a generic Streamlit app. Every design decision should reinforce the idea that this is a serious clinical tool.

Design rules:
- Color palette: #0A0F1E (deep navy background), #0FF4C6 (electric teal accent), #FF4B6E (alert red), #F5A623 (warning amber), #1A2035 (card background), #2A3350 (border color), white for primary text, #8896B3 for secondary text
- Typography: Import "Space Mono" from Google Fonts for scores/data, "DM Sans" for prose
- Cards with 1px borders in #2A3350, subtle box-shadow: 0 4px 24px rgba(0,255,196,0.04)
- Confidence badges: pill-shaped, color-coded (teal=HIGH, amber=MEDIUM, slate=LOW)
- Animated pipeline progress steps during analysis
- No default Streamlit purple anywhere
- Sidebar with icon labels, clean navigation

---

## Step 1: Create styles.py

```python
def load_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0A0F1E;
    color: #E8EDF5;
}

.stApp {
    background-color: #0A0F1E;
}

/* ── Hide default streamlit elements ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
header {visibility: hidden;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0D1428;
    border-right: 1px solid #2A3350;
}

[data-testid="stSidebar"] .stRadio label {
    color: #8896B3;
    font-size: 0.9rem;
    padding: 8px 0;
    transition: color 0.2s;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: #0FF4C6;
}

/* ── Cards ── */
.cl-card {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(15, 244, 198, 0.04);
    transition: border-color 0.2s;
}

.cl-card:hover {
    border-color: #3A4570;
}

.cl-card-accent {
    border-left: 3px solid #0FF4C6;
}

/* ── Metric Cards ── */
.cl-metric {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}

.cl-metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #0FF4C6;
    line-height: 1;
    margin-bottom: 6px;
}

.cl-metric-label {
    color: #8896B3;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Confidence Badges ── */
.badge-high {
    display: inline-block;
    background: rgba(255, 75, 110, 0.15);
    color: #FF4B6E;
    border: 1px solid rgba(255, 75, 110, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.badge-medium {
    display: inline-block;
    background: rgba(245, 166, 35, 0.15);
    color: #F5A623;
    border: 1px solid rgba(245, 166, 35, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.badge-low {
    display: inline-block;
    background: rgba(136, 150, 179, 0.15);
    color: #8896B3;
    border: 1px solid rgba(136, 150, 179, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* ── Signal Cards ── */
.signal-card {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
}

.signal-card-high { border-left: 3px solid #FF4B6E; }
.signal-card-medium { border-left: 3px solid #F5A623; }
.signal-card-low { border-left: 3px solid #8896B3; }

.signal-exchange {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #8896B3;
    margin-bottom: 6px;
}

.signal-quote {
    font-style: italic;
    color: #E8EDF5;
    font-size: 0.95rem;
    margin-bottom: 10px;
    padding: 8px 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
}

.signal-reasoning {
    color: #8896B3;
    font-size: 0.85rem;
    line-height: 1.5;
}

/* ── Pipeline Steps ── */
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    background: #1A2035;
    border: 1px solid #2A3350;
    font-size: 0.9rem;
}

.pipeline-step-active {
    border-color: #0FF4C6;
    color: #0FF4C6;
}

.pipeline-step-done {
    border-color: #2A3350;
    color: #8896B3;
}

.pipeline-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #0FF4C6;
    animation: pulse 1s infinite;
    flex-shrink: 0;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* ── Coaching Cards ── */
.coaching-card {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-left: 3px solid #FF4B6E;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 14px;
}

.coaching-issue {
    color: #FF4B6E;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}

.coaching-exchange {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #8896B3;
    margin-bottom: 12px;
}

.coaching-quote {
    font-style: italic;
    padding: 8px 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.coaching-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #8896B3;
    margin-bottom: 4px;
}

.coaching-better {
    color: #0FF4C6;
    font-size: 0.9rem;
    padding: 8px 12px;
    background: rgba(15, 244, 198, 0.05);
    border-radius: 6px;
    border: 1px solid rgba(15, 244, 198, 0.15);
}

/* ── Section Headers ── */
.cl-section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #0FF4C6;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2A3350;
}

/* ── Recall Gauge ── */
.recall-score-big {
    font-family: 'Space Mono', monospace;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
}

.recall-good { color: #0FF4C6; }
.recall-mid { color: #F5A623; }
.recall-bad { color: #FF4B6E; }

/* ── Strength / Gap / Critical items ── */
.strength-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(15, 244, 198, 0.05);
    border: 1px solid rgba(15, 244, 198, 0.15);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #C8D0E0;
}

.gap-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(245, 166, 35, 0.05);
    border: 1px solid rgba(245, 166, 35, 0.15);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #C8D0E0;
}

.critical-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(255, 75, 110, 0.05);
    border: 1px solid rgba(255, 75, 110, 0.15);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #C8D0E0;
}

/* ── Timeline ── */
.timeline-container {
    position: relative;
    padding-left: 24px;
}

.timeline-line {
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, #0FF4C6, transparent);
}

.timeline-item {
    position: relative;
    margin-bottom: 16px;
}

.timeline-dot {
    position: absolute;
    left: -20px;
    top: 6px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.timeline-dot-high { background: #FF4B6E; box-shadow: 0 0 8px rgba(255,75,110,0.5); }
.timeline-dot-medium { background: #F5A623; box-shadow: 0 0 8px rgba(245,166,35,0.5); }
.timeline-dot-low { background: #8896B3; }

/* ── Comparison ── */
.compare-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #0FF4C6;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #2A3350;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0FF4C6 0%, #00C9A7 100%);
    color: #0A0F1E;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 10px 24px;
    transition: all 0.2s;
    letter-spacing: 0.02em;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(15, 244, 198, 0.3);
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #1A2035 !important;
    border: 1px solid #2A3350 !important;
    border-radius: 8px !important;
    color: #E8EDF5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #0FF4C6 !important;
    box-shadow: 0 0 0 2px rgba(15, 244, 198, 0.1) !important;
}

.stSelectbox > div > div {
    background: #1A2035 !important;
    border: 1px solid #2A3350 !important;
    border-radius: 8px !important;
    color: #E8EDF5 !important;
}

hr {
    border-color: #2A3350 !important;
    margin: 24px 0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1A2035;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #2A3350;
}

.stTabs [data-baseweb="tab"] {
    color: #8896B3;
    font-family: 'DM Sans', sans-serif;
}

.stTabs [aria-selected="true"] {
    background: #2A3350;
    color: #0FF4C6 !important;
    border-radius: 6px;
}

/* ── Onboarding ── */
.onboard-container {
    max-width: 680px;
    margin: 40px auto 32px auto;
    text-align: center;
}

.onboard-title {
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    color: #0FF4C6;
    margin-bottom: 8px;
}

.onboard-sub {
    color: #8896B3;
    font-size: 1.05rem;
    margin-bottom: 40px;
    font-weight: 300;
}

.onboard-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px 20px;
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 10px;
    margin-bottom: 12px;
    text-align: left;
}

.onboard-num {
    font-family: 'Space Mono', monospace;
    font-size: 1.2rem;
    color: #0FF4C6;
    font-weight: 700;
    min-width: 32px;
}

.onboard-step-title {
    font-weight: 600;
    color: #E8EDF5;
    margin-bottom: 4px;
}

.onboard-step-desc {
    color: #8896B3;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* ── Report card ── */
.report-card {
    background: linear-gradient(135deg, #1A2035 0%, #141929 100%);
    border: 1px solid #2A3350;
    border-top: 3px solid #0FF4C6;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
}

.report-title {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    color: #0FF4C6;
    margin-bottom: 16px;
}

/* ── Framework reference ── */
.framework-item {
    padding: 10px 14px;
    background: #141929;
    border-radius: 8px;
    margin-bottom: 8px;
    border: 1px solid #2A3350;
}

.framework-item-title {
    font-weight: 600;
    font-size: 0.85rem;
    color: #E8EDF5;
    margin-bottom: 4px;
}

.framework-item-desc {
    font-size: 0.8rem;
    color: #8896B3;
    line-height: 1.4;
}

/* ── Scenario tags ── */
.scenario-tag {
    display: inline-block;
    background: rgba(15, 244, 198, 0.1);
    color: #0FF4C6;
    border: 1px solid rgba(15, 244, 198, 0.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-family: 'Space Mono', monospace;
    margin: 4px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A0F1E; }
::-webkit-scrollbar-thumb { background: #2A3350; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3A4570; }
</style>
"""
```

---

## Step 2: Create scenario_generator.py

```python
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"

SCENARIO_TYPES = {
    "Indirect Language Only": "The caller never uses direct suicidal language. All signals are embedded in metaphor, euphemism, or indirect phrasing. The volunteer must work harder to uncover meaning.",
    "Deflector": "The caller actively changes the subject or deflects every time the volunteer gets close to a sensitive topic. They use humor, topic changes, and minimization.",
    "High-Functioning Crisis": "The caller sounds composed and functional on the surface — talking about work, plans, normal life — but the underlying signals reveal serious risk. Superficially they seem fine.",
    "Farewell Caller": "The caller is saying goodbye without explicitly saying so. They are tying up loose ends, expressing gratitude to people in their life, and seem at peace in a concerning way.",
    "Hopelessness Without Ideation": "The caller expresses deep hopelessness and meaninglessness but never mentions death or suicide directly. The risk is in the passive ideation and hopelessness markers.",
    "Ambiguous Mixed Signals": "The caller sends contradictory signals — sometimes hopeful, sometimes despairing. The volunteer must navigate the inconsistency without dismissing the risk."
}

def generate_scenario(scenario_type: str, difficulty: str = "Hard") -> dict:
    scenario_desc = SCENARIO_TYPES.get(scenario_type, "")

    prompt = f"""You are a crisis intervention training designer.

Create a realistic crisis hotline practice transcript with this specific scenario profile:

SCENARIO TYPE: {scenario_type}
DESCRIPTION: {scenario_desc}
DIFFICULTY: {difficulty} — signals should be subtle and require clinical training to identify

Rules:
- 10-15 exchanges numbered starting from 1
- Label turns as "Caller:" and "Volunteer:"
- Volunteer responses should be generic and miss most signals (training failure scenario)
- The transcript must feel like a real conversation
- Embed C-SSRS risk signals naturally into the dialogue

Also provide ground truth of planted signals.

Output ONLY a JSON object with no preamble and no markdown:
{{
  "transcript": "full transcript as string with newlines between exchanges",
  "scenario_type": "{scenario_type}",
  "difficulty": "{difficulty}",
  "ground_truth": [
    {{
      "exchange_number": 3,
      "category": "C-SSRS category name",
      "planted_text": "exact phrase",
      "why_subtle": "one sentence explaining why this is hard to catch"
    }}
  ],
  "clinical_notes": "2-3 sentences a supervisor would say about what to watch for in this scenario type"
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a crisis intervention training content designer. Output only valid JSON with no markdown fences."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    raw = response.choices[0].message.content.strip()
    try:
        cleaned = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        return {"error": str(e), "raw": raw}
```

---

## Step 3: Create comparative.py

```python
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import (
    RISK_DETECTION_PROMPT,
    MI_SCORING_PROMPT,
    COACHING_PROMPT
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"

def call_gpt(system_prompt: str, user_content: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def safe_parse(raw: str):
    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        return {"error": str(e), "raw": raw}

def analyze_single(transcript: str) -> dict:
    signals_raw = call_gpt(RISK_DETECTION_PROMPT, f"TRANSCRIPT:\n{transcript}")
    signals = safe_parse(signals_raw)
    if isinstance(signals, dict) and "error" in signals:
        signals = []

    mi_raw = call_gpt(MI_SCORING_PROMPT, f"TRANSCRIPT:\n{transcript}")
    mi = safe_parse(mi_raw)

    coaching_input = f"TRANSCRIPT:\n{transcript}\n\nDETECTED SIGNALS:\n{json.dumps(signals, indent=2)}\n\nMI SCORING:\n{json.dumps(mi, indent=2)}"
    coaching_raw = call_gpt(COACHING_PROMPT, coaching_input)
    coaching = safe_parse(coaching_raw)

    return {"signals": signals, "mi": mi, "coaching": coaching}

def run_comparative(transcript_a: str, transcript_b: str, name_a: str = "Volunteer A", name_b: str = "Volunteer B") -> dict:
    result_a = analyze_single(transcript_a)
    result_b = analyze_single(transcript_b)

    score_a = result_a["coaching"].get("score", 0) if isinstance(result_a["coaching"], dict) else 0
    score_b = result_b["coaching"].get("score", 0) if isinstance(result_b["coaching"], dict) else 0
    mi_a = result_a["mi"].get("overall_mi_score", 0) if isinstance(result_a["mi"], dict) else 0
    mi_b = result_b["mi"].get("overall_mi_score", 0) if isinstance(result_b["mi"], dict) else 0
    sigs_a = len(result_a["signals"]) if isinstance(result_a["signals"], list) else 0
    sigs_b = len(result_b["signals"]) if isinstance(result_b["signals"], list) else 0
    summary_a = result_a["coaching"].get("summary", "") if isinstance(result_a["coaching"], dict) else ""
    summary_b = result_b["coaching"].get("summary", "") if isinstance(result_b["coaching"], dict) else ""

    comparison_prompt = f"""You are a senior crisis intervention training supervisor.

You reviewed the same scenario handled by two different volunteers.

{name_a}: Score {score_a}/100, MI {mi_a}/100, Signals caught: {sigs_a}
Summary: {summary_a}

{name_b}: Score {score_b}/100, MI {mi_b}/100, Signals caught: {sigs_b}
Summary: {summary_b}

Write a head-to-head supervisor comparison. Output ONLY a JSON object with no preamble and no markdown:
{{
  "winner": "name of winner or Tie",
  "winner_reasoning": "2 sentences on why",
  "a_strength": "what {name_a} did better",
  "b_strength": "what {name_b} did better",
  "shared_gaps": "what both volunteers missed",
  "recommendation": "one actionable training recommendation for each volunteer"
}}"""

    comparison_raw = call_gpt("You are a crisis intervention training supervisor. Output only valid JSON.", comparison_prompt)
    comparison = safe_parse(comparison_raw)

    return {
        "name_a": name_a,
        "name_b": name_b,
        "result_a": result_a,
        "result_b": result_b,
        "comparison": comparison
    }
```

---

## Step 4: Create report_generator.py

```python
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"

def generate_report_card(volunteer_name: str, sessions: list) -> dict:
    if len(sessions) < 2:
        return {"error": "Need at least 2 sessions for a report card."}

    prompt = f"""You are a senior crisis intervention training supervisor writing a formal report card for a volunteer trainee.

Volunteer: {volunteer_name}
Sessions completed: {len(sessions)}

Session data:
{json.dumps(sessions, indent=2)}

Write a detailed, honest supervisor report card. Be specific. Do not be generic.

Output ONLY a JSON object with no preamble and no markdown:
{{
  "overall_grade": "A or B or C or D or F",
  "overall_score_trend": "Improving or Declining or Stable",
  "narrative": "3-4 sentence overall assessment written as a supervisor would write it, referencing specific session patterns",
  "consistent_strengths": ["strength 1", "strength 2"],
  "persistent_gaps": ["gap 1", "gap 2"],
  "risk_detection_assessment": "2 sentences on how the volunteer handles risk signal detection across sessions",
  "mi_assessment": "2 sentences on their MI technique trend",
  "priority_recommendation": "the single most important thing this volunteer should focus on next",
  "readiness_assessment": "Ready for supervised calls or Needs more practice or Not yet ready"
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a crisis intervention training supervisor. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    try:
        cleaned = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        return {"error": str(e)}

def generate_alternative_responses(exchange_num: int, caller_text: str, volunteer_text: str, signal_category: str) -> list:
    prompt = f"""You are a Motivational Interviewing expert and crisis intervention trainer.

A volunteer missed a critical risk signal. Generate 3 alternative responses ranked by clinical quality.

Exchange: {exchange_num}
Caller said: "{caller_text}"
Volunteer actually said: "{volunteer_text}"
Signal category missed: {signal_category}

Output ONLY a JSON array with no preamble and no markdown:
[
  {{
    "rank": 1,
    "response": "the best alternative response",
    "why": "one sentence on why this is clinically strong"
  }},
  {{
    "rank": 2,
    "response": "a good alternative response",
    "why": "one sentence on why this is solid"
  }},
  {{
    "rank": 3,
    "response": "an acceptable alternative response",
    "why": "one sentence on why this works but is less ideal"
  }}
]"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a crisis intervention trainer. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    try:
        cleaned = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        return []
```

---

## Step 5: Replace app.py completely

Replace the ENTIRE contents of app.py with this. Delete everything that was there before and write this from scratch:

```python
import streamlit as st
import json
import time
from pipeline import run_pipeline
from redteam import generate_adversarial_transcript, evaluate_recall
from session_store import add_session, get_sessions, clear_sessions
from styles import load_css
from scenario_generator import generate_scenario, SCENARIO_TYPES
from comparative import run_comparative
from report_generator import generate_report_card, generate_alternative_responses

st.set_page_config(
    page_title="CrisisLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(load_css(), unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 8px 0;">
        <div style="font-family: 'Space Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #0FF4C6;">CrisisLens</div>
        <div style="font-size: 0.75rem; color: #8896B3; text-transform: uppercase; letter-spacing: 0.08em;">AI Training Coach</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    mode = st.radio(
        "Navigation",
        ["🏠  Overview", "📋  Transcript Analysis", "⚔️  Red-Team Mode", "🎯  Scenario Generator", "⚖️  Comparative Analysis", "📈  Progress Tracker"],
        label_visibility="collapsed"
    )

    st.divider()

    volunteer_name = st.text_input("Volunteer Name", value="Trainee", help="Used for longitudinal tracking")

    st.divider()

    with st.expander("📖 C-SSRS Reference"):
        frameworks = [
            ("Passive Ideation", "Wishes to be dead, no plan"),
            ("Active Ideation", "Thinking about suicide, no method"),
            ("Ideation + Plan", "Has a method in mind"),
            ("Preparatory", "Taking steps toward attempt"),
            ("Veiled Signal", "Indirect language suggesting ideation"),
            ("Hopelessness", "Deep meaninglessness, clinically significant"),
        ]
        for title, desc in frameworks:
            st.markdown(f"""
            <div class="framework-item">
                <div class="framework-item-title">{title}</div>
                <div class="framework-item-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📖 MI Principles"):
        mi_items = [
            ("Reflective Listening", "Accurately reflects caller's emotional state"),
            ("Open-Ended Questions", "Invites elaboration, not yes/no"),
            ("Affirmation", "Acknowledges caller's strengths"),
            ("Avoid Leading", "Does not suggest answers or minimize"),
            ("Escalation", "Explores risk signals, does not pivot away"),
        ]
        for title, desc in mi_items:
            st.markdown(f"""
            <div class="framework-item">
                <div class="framework-item-title">{title}</div>
                <div class="framework-item-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("Clear Session Data"):
        clear_sessions()
        st.success("Session cleared.")


# ── Helper functions ──────────────────────────────────────────────────────────

def render_signal_card(sig):
    confidence = sig.get("confidence", "LOW")
    css_class = f"signal-card signal-card-{confidence.lower()}"
    badge_class = f"badge-{confidence.lower()}"
    st.markdown(f"""
    <div class="{css_class}">
        <div class="signal-exchange">EXCHANGE {sig.get('exchange_number')} &nbsp;·&nbsp; {sig.get('category', '')}</div>
        <div class="signal-quote">"{sig.get('caller_text', '')}"</div>
        <div style="margin-bottom: 8px;"><span class="{badge_class}">{confidence}</span></div>
        <div class="signal-reasoning">{sig.get('reasoning', '')}</div>
        <div class="signal-reasoning" style="margin-top: 4px; font-style: italic;">{sig.get('confidence_reasoning', '')}</div>
    </div>
    """, unsafe_allow_html=True)


def render_coaching_card(pf):
    st.markdown(f"""
    <div class="coaching-card">
        <div class="coaching-issue">{pf.get('issue', '')}</div>
        <div class="coaching-exchange">Exchange {pf.get('exchange', '')}</div>
        <div class="coaching-label">Caller said</div>
        <div class="coaching-quote">"{pf.get('caller_signal', '')}"</div>
        <div class="coaching-label" style="margin-top: 10px;">Volunteer said</div>
        <div class="coaching-quote" style="color: #8896B3;">"{pf.get('volunteer_response', '')}"</div>
        <div class="coaching-label" style="margin-top: 10px; color: #0FF4C6;">Recommended response</div>
        <div class="coaching-better">{pf.get('recommended_response', '')}</div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(score, signals_count, mi_score):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{score}</div><div class="cl-metric-label">Overall Score</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{signals_count}</div><div class="cl-metric-label">Risk Signals Found</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{mi_score}</div><div class="cl-metric-label">MI Score</div></div>', unsafe_allow_html=True)


def run_pipeline_with_progress(transcript):
    steps = [
        "Scanning for C-SSRS risk signals",
        "Calibrating confidence scores",
        "Evaluating MI technique",
        "Generating coaching feedback"
    ]
    placeholder = st.empty()
    for i in range(len(steps)):
        html = ""
        for j, s in enumerate(steps):
            if j < i:
                html += f'<div class="pipeline-step pipeline-step-done">✓ &nbsp; {s}</div>'
            elif j == i:
                html += f'<div class="pipeline-step pipeline-step-active"><span class="pipeline-dot"></span>&nbsp; {s}...</div>'
            else:
                html += f'<div class="pipeline-step pipeline-step-done" style="opacity:0.4;">○ &nbsp; {s}</div>'
        placeholder.markdown(f'<div style="margin:16px 0;">{html}</div>', unsafe_allow_html=True)
        time.sleep(0.4)
    results = run_pipeline(transcript)
    placeholder.empty()
    return results


# ── Overview ─────────────────────────────────────────────────────────────────
if "Overview" in mode:
    st.markdown("""
    <div class="onboard-container">
        <div class="onboard-title">CrisisLens</div>
        <div class="onboard-sub">AI-powered coaching for crisis hotline volunteer training</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown('<div class="cl-section-header">How It Works</div>', unsafe_allow_html=True)
        steps_data = [
            ("01", "Risk Signal Detection", "Scans transcripts for language mapping to Columbia Suicide Severity Rating Scale (C-SSRS) criteria — the clinical gold standard used by crisis organizations worldwide."),
            ("02", "Confidence Scoring", "Rates certainty on every flagged signal: HIGH, MEDIUM, or LOW — with reasoning. A system that treats all flags identically is dangerous."),
            ("03", "MI Evaluation", "Scores volunteer responses against Motivational Interviewing principles. Did they reflect emotions? Avoid leading questions? Escalate appropriately?"),
            ("04", "Coaching Feedback", "Generates exchange-level coaching notes with specific recommended responses — not generic summaries, but targeted clinical guidance."),
        ]
        for num, title, desc in steps_data:
            st.markdown(f"""
            <div class="onboard-step">
                <div class="onboard-num">{num}</div>
                <div>
                    <div class="onboard-step-title">{title}</div>
                    <div class="onboard-step-desc">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="cl-section-header">Modes</div>', unsafe_allow_html=True)
        features = [
            ("📋", "Transcript Analysis", "Full 4-step pipeline on any practice transcript"),
            ("⚔️", "Red-Team Mode", "Adversarial testing with recall metrics"),
            ("🎯", "Scenario Generator", "6 targeted training scenario types"),
            ("⚖️", "Comparative Analysis", "Head-to-head volunteer comparison"),
            ("📈", "Progress Tracker", "Longitudinal improvement with report cards"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
            <div class="cl-card">
                <div style="font-size: 1.1rem; margin-bottom: 4px;">{icon} <strong style="color: #E8EDF5;">{title}</strong></div>
                <div style="color: #8896B3; font-size: 0.84rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cl-card" style="margin-top: 4px;">
            <div style="color: #8896B3; font-size: 0.84rem; line-height: 1.6;">
                Grounded in the <strong style="color: #0FF4C6;">C-SSRS</strong> and <strong style="color: #0FF4C6;">SAMHSA MI Guidelines</strong>. All data is synthetic. No real caller data is ever used.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Transcript Analysis ───────────────────────────────────────────────────────
elif "Transcript" in mode:
    st.markdown('<div class="cl-section-header">Transcript Analysis</div>', unsafe_allow_html=True)

    sample_options = {
        "— Select a sample —": "",
        "Easy — Explicit Signals": open("sample_transcripts/easy.txt").read(),
        "Medium — Mixed Signals": open("sample_transcripts/medium.txt").read(),
        "Hard — Buried Signals": open("sample_transcripts/hard.txt").read(),
    }

    col_left, col_right = st.columns([2, 1])
    with col_left:
        sample_choice = st.selectbox("Load a sample transcript", list(sample_options.keys()))
        transcript_input = st.text_area(
            "Transcript",
            value=sample_options[sample_choice],
            height=280,
            placeholder="Volunteer: Hi, thanks for calling.\nCaller: Not great, honestly...",
            label_visibility="collapsed"
        )
    with col_right:
        st.markdown("""
        <div class="cl-card">
            <div class="cl-section-header">Format Guide</div>
            <div style="color: #8896B3; font-size: 0.85rem; line-height: 1.8;">
                Label each turn:<br>
                <code style="color: #0FF4C6;">Volunteer: ...</code><br>
                <code style="color: #0FF4C6;">Caller: ...</code><br><br>
                Number exchanges or keep sequential.<br><br>
                <strong style="color: #E8EDF5;">Tip:</strong> Load the Hard sample to see subtle signal detection.
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Analyze Transcript", type="primary"):
        if not transcript_input.strip():
            st.error("Please paste a transcript or load a sample.")
        else:
            results = run_pipeline_with_progress(transcript_input)

            if "error" in results:
                st.error(f"Pipeline error: {results['error']}")
            else:
                signals = results.get("signals") or []
                mi = results.get("mi_results") or {}
                coaching = results.get("coaching") or {}
                score = coaching.get("score", 0) if isinstance(coaching, dict) else 0
                mi_score = mi.get("overall_mi_score", 0) if isinstance(mi, dict) else 0

                add_session(volunteer_name, score, len(signals), mi_score)

                st.divider()
                render_metrics(score, len(signals), mi_score)
                st.divider()

                tab1, tab2, tab3, tab4 = st.tabs(["Risk Signals", "Signal Timeline", "MI Assessment", "Coaching"])

                with tab1:
                    st.markdown('<div class="cl-section-header">Detected Risk Signals</div>', unsafe_allow_html=True)
                    if not signals:
                        st.info("No risk signals detected.")
                    else:
                        for level in ["HIGH", "MEDIUM", "LOW"]:
                            subset = [s for s in signals if s.get("confidence") == level]
                            if subset:
                                st.markdown(f"**{level.capitalize()} Confidence**")
                                for s in subset:
                                    render_signal_card(s)

                with tab2:
                    st.markdown('<div class="cl-section-header">Signal Timeline</div>', unsafe_allow_html=True)
                    if not signals:
                        st.info("No signals to display.")
                    else:
                        st.markdown('<div class="timeline-container"><div class="timeline-line"></div>', unsafe_allow_html=True)
                        for sig in sorted(signals, key=lambda x: x.get("exchange_number", 0)):
                            conf = sig.get("confidence", "LOW").lower()
                            st.markdown(f"""
                            <div class="timeline-item">
                                <div class="timeline-dot timeline-dot-{conf}"></div>
                                <div class="signal-card signal-card-{conf}" style="margin-bottom:0;">
                                    <div class="signal-exchange">EXCHANGE {sig.get('exchange_number')} · {sig.get('category', '')} · <span class="badge-{conf}">{sig.get('confidence','')}</span></div>
                                    <div class="signal-quote">"{sig.get('caller_text','')}"</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                with tab3:
                    st.markdown('<div class="cl-section-header">MI Assessment</div>', unsafe_allow_html=True)
                    if isinstance(mi, dict):
                        col_s, col_g = st.columns(2)
                        with col_s:
                            st.markdown("**Strengths**")
                            for s in mi.get("strengths", []):
                                st.markdown(f'<div class="strength-item">✓ &nbsp; {s}</div>', unsafe_allow_html=True)
                        with col_g:
                            st.markdown("**Gaps**")
                            for g in mi.get("gaps", []):
                                st.markdown(f'<div class="gap-item">⚠ &nbsp; {g}</div>', unsafe_allow_html=True)
                        if mi.get("critical_misses"):
                            st.markdown("**Critical Misses**")
                            for cm in mi.get("critical_misses", []):
                                st.markdown(f'<div class="critical-item">✕ &nbsp; {cm}</div>', unsafe_allow_html=True)

                with tab4:
                    st.markdown('<div class="cl-section-header">Coaching Feedback</div>', unsafe_allow_html=True)
                    if isinstance(coaching, dict):
                        st.markdown(f"""
                        <div class="report-card">
                            <div class="report-title">Supervisor Summary</div>
                            <div style="color: #C8D0E0; line-height: 1.7;">{coaching.get('summary', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        for pf in coaching.get("priority_feedback", []):
                            render_coaching_card(pf)
                            btn_key = f"alt_{pf.get('exchange')}_{id(pf)}"
                            if st.button(f"Generate 3 Alternative Responses — Exchange {pf.get('exchange')}", key=btn_key):
                                with st.spinner("Generating ranked alternatives..."):
                                    alts = generate_alternative_responses(
                                        pf.get("exchange"),
                                        pf.get("caller_signal", ""),
                                        pf.get("volunteer_response", ""),
                                        pf.get("issue", "")
                                    )
                                rank_colors = {1: "#0FF4C6", 2: "#F5A623", 3: "#8896B3"}
                                for alt in (alts or []):
                                    color = rank_colors.get(alt.get("rank", 3), "#8896B3")
                                    st.markdown(f"""
                                    <div class="cl-card" style="border-left: 3px solid {color}; margin-left: 20px;">
                                        <div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:{color}; margin-bottom:8px;">RANK {alt.get('rank')}</div>
                                        <div style="color:#E8EDF5; margin-bottom:8px;">"{alt.get('response','')}"</div>
                                        <div style="color:#8896B3; font-size:0.82rem;">{alt.get('why','')}</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="cl-card" style="margin-top:16px;">
                            <div class="coaching-label">MI Feedback</div>
                            <div style="color:#C8D0E0; line-height:1.6; margin-top:8px;">{coaching.get('mi_feedback','')}</div>
                        </div>
                        """, unsafe_allow_html=True)


# ── Red-Team Mode ─────────────────────────────────────────────────────────────
elif "Red-Team" in mode:
    st.markdown('<div class="cl-section-header">Red-Team Mode — Adversarial Evaluation</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="cl-card cl-card-accent">
        <div style="color:#C8D0E0; font-size:0.9rem; line-height:1.6;">
            Generate transcripts with <strong style="color:#0FF4C6;">deliberately buried risk signals</strong>, then measure what percentage the pipeline catches.
            <strong style="color:#FF4B6E;">Recall rate on adversarial transcripts</strong> is the primary evaluation metric — this is where silent failures hide.
        </div>
    </div>
    """, unsafe_allow_html=True)

    num_signals = st.slider("Planted signals", min_value=2, max_value=5, value=3)

    if st.button("Generate Adversarial Transcript", type="primary"):
        with st.spinner("Generating adversarial transcript..."):
            result = generate_adversarial_transcript(num_signals=num_signals)
        if isinstance(result, dict) and "error" not in result:
            st.session_state["adversarial_transcript"] = result.get("transcript", "")
            st.session_state["ground_truth"] = result.get("ground_truth", [])
            st.success(f"Generated with {num_signals} buried signals.")

    if "adversarial_transcript" in st.session_state:
        st.text_area("Generated Transcript", value=st.session_state["adversarial_transcript"], height=280, label_visibility="collapsed")

        with st.expander("Reveal Ground Truth"):
            for gt in st.session_state.get("ground_truth", []):
                st.markdown(f"""
                <div class="signal-card signal-card-high">
                    <div class="signal-exchange">EXCHANGE {gt.get('exchange_number')} · {gt.get('category','')}</div>
                    <div class="signal-quote">"{gt.get('planted_text','')}"</div>
                </div>
                """, unsafe_allow_html=True)

        if st.button("Run Recall Evaluation", type="primary"):
            with st.spinner("Evaluating recall..."):
                recall = evaluate_recall(
                    st.session_state["adversarial_transcript"],
                    st.session_state["ground_truth"]
                )

            if "error" not in recall:
                score = recall["recall_score"]
                score_class = "recall-good" if score >= 70 else "recall-mid" if score >= 40 else "recall-bad"

                col_g, col_d = st.columns([1, 2])
                with col_g:
                    st.markdown(f"""
                    <div class="cl-card" style="text-align:center; padding:32px;">
                        <div class="cl-metric-label">Recall Score</div>
                        <div class="recall-score-big {score_class}">{score}%</div>
                        <div style="color:#8896B3; font-size:0.8rem; margin-top:8px;">{recall['total_planted']} planted · {len(recall['caught'])} caught</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_d:
                    if recall["caught"]:
                        st.markdown(f'<div class="strength-item">✓ &nbsp; Caught at exchanges: {recall["caught"]}</div>', unsafe_allow_html=True)
                    if recall["missed"]:
                        st.markdown(f'<div class="critical-item">✕ &nbsp; Missed at exchanges: {recall["missed"]}</div>', unsafe_allow_html=True)
                    if recall["false_positives"]:
                        st.markdown(f'<div class="gap-item">⚠ &nbsp; False positives at exchanges: {recall["false_positives"]}</div>', unsafe_allow_html=True)

                with st.expander("Full detected signals"):
                    st.json(recall.get("detected_signals", []))


# ── Scenario Generator ────────────────────────────────────────────────────────
elif "Scenario" in mode:
    st.markdown('<div class="cl-section-header">Scenario Generator</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="cl-card cl-card-accent">
        <div style="color:#C8D0E0; font-size:0.9rem; line-height:1.6;">
            Generate targeted practice scenarios for specific training gaps. Each type develops a different clinical skill.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        scenario_type = st.selectbox("Scenario Type", list(SCENARIO_TYPES.keys()))
        difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Hard")
        gen_btn = st.button("Generate Scenario", type="primary")
    with col2:
        st.markdown(f"""
        <div class="cl-card">
            <div class="cl-section-header">{scenario_type}</div>
            <div style="color:#C8D0E0; font-size:0.88rem; line-height:1.6;">{SCENARIO_TYPES.get(scenario_type,'')}</div>
            <div style="margin-top:12px;">
                <span class="scenario-tag">{difficulty}</span>
                <span class="scenario-tag">Synthetic</span>
                <span class="scenario-tag">C-SSRS Grounded</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if gen_btn:
        with st.spinner(f"Generating scenario..."):
            result = generate_scenario(scenario_type, difficulty)
        if isinstance(result, dict) and "error" not in result:
            st.session_state["scenario_result"] = result
            st.success("Scenario generated.")
        else:
            st.error(f"Error: {result.get('error', 'Unknown error')}")

    if "scenario_result" in st.session_state:
        res = st.session_state["scenario_result"]

        if res.get("clinical_notes"):
            st.markdown(f"""
            <div class="report-card">
                <div class="report-title">Clinical Notes</div>
                <div style="color:#C8D0E0; line-height:1.7; font-size:0.9rem;">{res['clinical_notes']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.text_area("Generated Transcript", value=res.get("transcript", ""), height=280, label_visibility="collapsed")

        with st.expander("Ground Truth"):
            for gt in res.get("ground_truth", []):
                st.markdown(f"""
                <div class="signal-card signal-card-high">
                    <div class="signal-exchange">EXCHANGE {gt.get('exchange_number')} · {gt.get('category','')}</div>
                    <div class="signal-quote">"{gt.get('planted_text','')}"</div>
                    <div class="signal-reasoning">Why subtle: {gt.get('why_subtle','')}</div>
                </div>
                """, unsafe_allow_html=True)

        if st.button("Analyze This Scenario", type="primary"):
            results = run_pipeline_with_progress(res.get("transcript", ""))
            if "error" not in results:
                signals = results.get("signals") or []
                mi = results.get("mi_results") or {}
                coaching = results.get("coaching") or {}
                score = coaching.get("score", 0) if isinstance(coaching, dict) else 0
                mi_score = mi.get("overall_mi_score", 0) if isinstance(mi, dict) else 0
                add_session(volunteer_name, score, len(signals), mi_score)
                render_metrics(score, len(signals), mi_score)
                st.divider()
                if signals:
                    st.markdown('<div class="cl-section-header">Signals Detected</div>', unsafe_allow_html=True)
                    for sig in signals:
                        render_signal_card(sig)
                if isinstance(coaching, dict) and coaching.get("priority_feedback"):
                    st.markdown('<div class="cl-section-header">Coaching</div>', unsafe_allow_html=True)
                    for pf in coaching.get("priority_feedback", []):
                        render_coaching_card(pf)


# ── Comparative Analysis ──────────────────────────────────────────────────────
elif "Comparative" in mode:
    st.markdown('<div class="cl-section-header">Comparative Analysis — Head-to-Head</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="cl-card cl-card-accent">
        <div style="color:#C8D0E0; font-size:0.9rem; line-height:1.6;">
            Submit two transcripts of the same scenario handled by different volunteers. CrisisLens runs the full pipeline on both and generates a head-to-head supervisor comparison.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="compare-header">Volunteer A</div>', unsafe_allow_html=True)
        name_a = st.text_input("Name A", value="Volunteer A", label_visibility="collapsed")
        transcript_a = st.text_area("Transcript A", height=220, placeholder="Paste Volunteer A transcript...", label_visibility="collapsed")
    with col_b:
        st.markdown('<div class="compare-header">Volunteer B</div>', unsafe_allow_html=True)
        name_b = st.text_input("Name B", value="Volunteer B", label_visibility="collapsed")
        transcript_b = st.text_area("Transcript B", height=220, placeholder="Paste Volunteer B transcript...", label_visibility="collapsed")

    if st.button("Run Comparative Analysis", type="primary"):
        if not transcript_a.strip() or not transcript_b.strip():
            st.error("Please provide both transcripts.")
        else:
            with st.spinner("Analyzing both transcripts..."):
                comp_results = run_comparative(transcript_a, transcript_b, name_a, name_b)

            res_a = comp_results.get("result_a", {})
            res_b = comp_results.get("result_b", {})
            comp = comp_results.get("comparison", {})

            winner = comp.get("winner", "")
            st.markdown(f"""
            <div class="report-card" style="text-align:center; border-top-color:#F5A623;">
                <div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#F5A623; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.1em;">Supervisor Verdict</div>
                <div style="font-family:'Space Mono',monospace; font-size:1.8rem; color:#E8EDF5; font-weight:700;">{winner}</div>
                <div style="color:#8896B3; font-size:0.88rem; margin-top:8px;">{comp.get('winner_reasoning','')}</div>
            </div>
            """, unsafe_allow_html=True)

            col_ra, col_rb = st.columns(2)
            for col, res, name, strength_key in [
                (col_ra, res_a, name_a, "a_strength"),
                (col_rb, res_b, name_b, "b_strength")
            ]:
                score = res.get("coaching", {}).get("score", 0) if isinstance(res.get("coaching"), dict) else 0
                mi = res.get("mi", {}).get("overall_mi_score", 0) if isinstance(res.get("mi"), dict) else 0
                sigs = len(res.get("signals", []) or [])
                with col:
                    st.markdown(f"""
                    <div class="cl-card">
                        <div class="compare-header">{name}</div>
                        <div class="cl-metric-value" style="font-size:1.5rem;">{score}/100</div>
                        <div class="cl-metric-label">Overall Score</div>
                        <div style="margin-top:12px; color:#8896B3; font-size:0.85rem;">MI: {mi}/100 &nbsp;·&nbsp; Signals: {sigs}</div>
                        <div style="margin-top:12px; color:#0FF4C6; font-size:0.85rem;">{comp.get(strength_key,'')}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if comp.get("shared_gaps"):
                st.markdown(f'<div class="gap-item" style="margin-top:16px;">⚠ &nbsp; <strong>Shared Gap:</strong> &nbsp; {comp["shared_gaps"]}</div>', unsafe_allow_html=True)
            if comp.get("recommendation"):
                st.markdown(f'<div class="cl-card" style="margin-top:12px;"><div class="coaching-label">Training Recommendation</div><div style="color:#C8D0E0; margin-top:8px; font-size:0.9rem;">{comp["recommendation"]}</div></div>', unsafe_allow_html=True)


# ── Progress Tracker ──────────────────────────────────────────────────────────
elif "Progress" in mode:
    st.markdown('<div class="cl-section-header">Progress Tracker</div>', unsafe_allow_html=True)

    sessions = get_sessions(volunteer_name)

    if not sessions:
        st.markdown(f"""
        <div class="cl-card" style="text-align:center; padding:40px;">
            <div style="font-size:2rem; margin-bottom:12px;">📋</div>
            <div style="color:#8896B3;">No sessions found for <strong style="color:#E8EDF5;">{volunteer_name}</strong>.</div>
            <div style="color:#8896B3; font-size:0.85rem; margin-top:8px;">Submit transcripts in Transcript Analysis to start tracking.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        avg_score = sum(s["score"] for s in sessions) / len(sessions)
        avg_mi = sum(s["mi_score"] for s in sessions) / len(sessions)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{len(sessions)}</div><div class="cl-metric-label">Sessions</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{avg_score:.0f}</div><div class="cl-metric-label">Avg Score</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{avg_mi:.0f}</div><div class="cl-metric-label">Avg MI Score</div></div>', unsafe_allow_html=True)

        st.divider()

        import pandas as pd
        df = pd.DataFrame(sessions)

        if len(sessions) > 1:
            st.markdown('<div class="cl-section-header">Score Trend</div>', unsafe_allow_html=True)
            st.line_chart(df.set_index("session_number")[["score", "mi_score"]], color=["#0FF4C6", "#F5A623"])

        st.markdown('<div class="cl-section-header">Session History</div>', unsafe_allow_html=True)
        st.dataframe(
            df[["session_number", "score", "signals_found", "mi_score"]].rename(columns={
                "session_number": "Session",
                "score": "Overall Score",
                "signals_found": "Signals Found",
                "mi_score": "MI Score"
            }),
            use_container_width=True,
            hide_index=True
        )

        if len(sessions) >= 2:
            st.divider()
            st.markdown('<div class="cl-section-header">Supervisor Report Card</div>', unsafe_allow_html=True)

            if st.button("Generate Report Card", type="primary"):
                with st.spinner("Generating supervisor report card..."):
                    report = generate_report_card(volunteer_name, sessions)

                if "error" not in report:
                    grade_colors = {"A": "#0FF4C6", "B": "#00C9A7", "C": "#F5A623", "D": "#FF8C42", "F": "#FF4B6E"}
                    grade = report.get("overall_grade", "N/A")
                    grade_color = grade_colors.get(grade, "#8896B3")
                    readiness = report.get("readiness_assessment", "")
                    readiness_colors = {
                        "Ready for supervised calls": "#0FF4C6",
                        "Needs more practice": "#F5A623",
                        "Not yet ready": "#FF4B6E"
                    }
                    readiness_color = readiness_colors.get(readiness, "#8896B3")

                    st.markdown(f"""
                    <div class="report-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                            <div class="report-title">Supervisor Report — {volunteer_name}</div>
                            <div style="font-family:'Space Mono',monospace; font-size:2rem; color:{grade_color}; font-weight:700;">{grade}</div>
                        </div>
                        <div style="color:#C8D0E0; line-height:1.7; margin-bottom:16px;">{report.get('narrative','')}</div>
                        <div style="display:inline-block; padding:6px 16px; background:rgba(15,244,198,0.1); border:1px solid rgba(15,244,198,0.2); border-radius:20px; font-size:0.82rem; color:{readiness_color};">
                            {readiness}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_s, col_g = st.columns(2)
                    with col_s:
                        st.markdown("**Consistent Strengths**")
                        for s in report.get("consistent_strengths", []):
                            st.markdown(f'<div class="strength-item">✓ &nbsp; {s}</div>', unsafe_allow_html=True)
                    with col_g:
                        st.markdown("**Persistent Gaps**")
                        for g in report.get("persistent_gaps", []):
                            st.markdown(f'<div class="gap-item">⚠ &nbsp; {g}</div>', unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="cl-card" style="margin-top:16px; border-left:3px solid #0FF4C6;">
                        <div class="coaching-label">Priority Recommendation</div>
                        <div style="color:#C8D0E0; margin-top:8px; font-size:0.9rem;">{report.get('priority_recommendation','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(report.get("error", "Report generation failed."))
```

---

## Step 6: Commit and push

```bash
git add .
git commit -m "feat: full UI overhaul + scenario generator + comparative analysis + report cards + alternative responses"
git push origin main
```

---

## Step 7: Final verification checklist

- [ ] styles.py exists and contains load_css()
- [ ] scenario_generator.py exists
- [ ] comparative.py exists
- [ ] report_generator.py exists
- [ ] app.py has been fully replaced (not appended to)
- [ ] Run `.venv/bin/streamlit run app.py` — zero import errors
- [ ] All 6 sidebar modes render without crashing: Overview, Transcript Analysis, Red-Team Mode, Scenario Generator, Comparative Analysis, Progress Tracker
- [ ] Pushed to GitHub

## Critical rules

- DO NOT modify pipeline.py, redteam.py, session_store.py, or prompts.py
- DO NOT install any new packages — pandas is already installed, everything else is stdlib or already in venv
- app.py must be fully replaced, not appended — delete the old content entirely first
- If any import fails, fix only that import, do not rewrite the module
- If streamlit throws a syntax error in app.py, fix it in place and rerun before declaring done
- Verify the checklist passes before declaring complete