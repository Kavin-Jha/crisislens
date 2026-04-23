# CLAUDE.md — CrisisLens Build Instructions

You are building **CrisisLens**, an AI-powered coaching assistant for mental health crisis hotline volunteer training. Read this entire file before writing a single line of code. Follow every step in order. Do not skip steps. Do not ask for clarification — everything you need is here.

---

## What You Are Building

CrisisLens takes a simulated crisis hotline practice transcript and runs it through a four-step agentic pipeline:

1. **Risk Signal Detection** — scan for language mapping to Columbia Suicide Severity Rating Scale (C-SSRS) criteria
2. **Confidence Scoring** — rate certainty on every flagged signal (high / medium / low) with reasoning
3. **MI Response Scoring** — evaluate volunteer responses against Motivational Interviewing principles
4. **Coaching Feedback** — generate specific, exchange-level coaching notes

**Standout feature: Red-Team Mode** — generates adversarial transcripts with deliberately buried risk signals, runs the pipeline on them, and produces a recall score (what % of planted signals were caught). This is the primary evaluation metric.

**Longitudinal tracking** — stores scores across multiple sessions in memory and shows a volunteer's improvement over time.

---

## Tech Stack

- Python 3.10+
- Streamlit (UI)
- OpenAI API (gpt-4o for all pipeline steps)
- python-dotenv
- No vector database. No fine-tuning. No external deployment.

---

## File Structure to Create

```
crisislens/
├── .env                  (already exists — DO NOT touch)
├── .gitignore            (already exists — DO NOT touch)
├── CLAUDE.md             (this file)
├── requirements.txt
├── app.py                (Streamlit UI — main entry point)
├── pipeline.py           (4-step agentic pipeline)
├── redteam.py            (adversarial transcript generator + recall evaluator)
├── session_store.py      (longitudinal session tracking)
├── prompts.py            (all system prompts)
├── sample_transcripts/
│   ├── easy.txt
│   ├── medium.txt
│   └── hard.txt
└── README.md
```

---

## Step 1: Install Dependencies

Create `requirements.txt`:

```
streamlit
openai
python-dotenv
```

Run:
```bash
pip install -r requirements.txt
```

---

## Step 2: Create `prompts.py`

This file contains all system prompts. Every prompt must be clinically grounded.

```python
RISK_DETECTION_PROMPT = """You are a clinical risk assessment assistant trained on the Columbia Suicide Severity Rating Scale (C-SSRS).

The C-SSRS categories you must detect are:
- Passive Ideation: wishes to be dead, no plan ("I don't see the point anymore", "I wish I could just disappear")
- Active Ideation Without Plan: thinking about suicide but no method ("I've been thinking about ending it")
- Active Ideation With Plan: has a method in mind ("I've been saving my pills")
- Preparatory Behavior: taking steps toward attempt ("I wrote a note", "I gave away my things")
- Veiled/Indirect Signal: indirect language that may indicate ideation ("I won't be a problem much longer", "everyone would be better off")
- Hopelessness Marker: expressions of hopelessness not directly suicidal but clinically significant

Given a crisis hotline practice transcript, identify every exchange where the CALLER (not the volunteer) uses language that maps to any of the above C-SSRS categories.

For each signal found, output:
- exchange_number: integer
- caller_text: exact quote
- category: one of the C-SSRS categories above
- reasoning: one sentence explaining why this maps to that category

Output ONLY a JSON array. No preamble. No markdown. Example:
[
  {
    "exchange_number": 3,
    "caller_text": "I don't see the point anymore",
    "category": "Passive Ideation",
    "reasoning": "Caller expresses loss of purpose without explicit suicidal plan, matching C-SSRS passive ideation criteria."
  }
]

If no signals are found, output: []
"""

CONFIDENCE_SCORING_PROMPT = """You are a clinical confidence calibration assistant.

You will receive a list of flagged risk signals from a crisis hotline transcript. For each signal, assign a confidence level and explain your reasoning.

Confidence levels:
- HIGH: language is unambiguous and maps directly to C-SSRS criteria with no alternative interpretation
- MEDIUM: language is suggestive but could have a non-clinical interpretation in context
- LOW: language is ambiguous and the flag is speculative

For each signal, output:
- exchange_number: integer (same as input)
- confidence: HIGH, MEDIUM, or LOW
- confidence_reasoning: one sentence explaining the confidence level

Output ONLY a JSON array. No preamble. No markdown. Example:
[
  {
    "exchange_number": 3,
    "confidence": "HIGH",
    "confidence_reasoning": "The phrase 'I don't see the point anymore' has no plausible benign interpretation in the context of a distress call."
  }
]
"""

MI_SCORING_PROMPT = """You are an expert evaluator of Motivational Interviewing (MI) techniques in crisis intervention contexts.

MI principles you must evaluate:
- Reflective Listening: volunteer accurately reflects the caller's emotional state
- Open-Ended Questions: volunteer asks questions that invite elaboration, not yes/no answers
- Affirmation: volunteer acknowledges the caller's strengths or efforts
- Avoiding Leading Questions: volunteer does not suggest answers or minimize feelings
- Appropriate Escalation: volunteer appropriately escalates when risk signals appear (explores further, does not pivot away)
- Summarizing: volunteer periodically summarizes what the caller has shared

Given a crisis hotline practice transcript, evaluate the VOLUNTEER's responses only.

Output:
- overall_mi_score: integer 0-100
- strengths: array of strings describing what the volunteer did well (specific, exchange-referenced)
- gaps: array of strings describing where MI principles were violated (specific, exchange-referenced)
- critical_misses: array of exchanges where a risk signal appeared and the volunteer failed to explore it

Output ONLY a JSON object. No preamble. No markdown.
"""

COACHING_PROMPT = """You are a senior crisis intervention training supervisor writing coaching feedback for a volunteer trainee.

You will receive:
1. The full transcript
2. Detected risk signals with confidence scores
3. MI scoring results

Write coaching feedback that is:
- Specific: reference exact exchange numbers and caller quotes
- Actionable: tell the volunteer what to do differently, not just what they did wrong
- Prioritized: lead with the most critical misses first
- Honest: do not soften serious misses with generic praise

Format your output as:
{
  "summary": "2-3 sentence overall assessment",
  "priority_feedback": [
    {
      "exchange": integer,
      "issue": "what went wrong",
      "caller_signal": "exact quote from caller",
      "volunteer_response": "what the volunteer said",
      "recommended_response": "what the volunteer should have said instead"
    }
  ],
  "mi_feedback": "2-3 sentences on overall MI technique",
  "score": integer 0-100
}

Output ONLY a JSON object. No preamble. No markdown.
"""

ADVERSARIAL_TRANSCRIPT_PROMPT = """You are a crisis intervention training designer creating adversarial practice transcripts for red-team evaluation.

Your job is to write a realistic crisis hotline practice transcript where the CALLER deliberately buries {num_signals} risk signals inside casual, surface-level conversation. The signals should not be obvious. They should require clinical training to catch.

Rules:
- The transcript must feel like a real conversation, not a clinical checklist
- Risk signals must be embedded in ordinary sentences (not standalone dramatic statements)
- The volunteer's responses should be generic and miss most signals (this is a training failure scenario)
- Each exchange is numbered starting from 1
- Label turns as "Caller:" and "Volunteer:"

Also output a ground truth list of exactly which exchanges contain planted signals and what category they are.

Output a JSON object:
{{
  "transcript": "full transcript as a string with newlines",
  "ground_truth": [
    {{
      "exchange_number": integer,
      "category": "C-SSRS category name",
      "planted_text": "exact phrase containing the signal"
    }}
  ]
}}

Output ONLY a JSON object. No preamble. No markdown.
"""
```

---

## Step 3: Create `session_store.py`

```python
# In-memory session store for longitudinal tracking across submissions in one session
# Resets when the app restarts — no external database, no PII stored

session_data = []

def add_session(volunteer_name: str, score: int, signals_found: int, mi_score: int):
    session_data.append({
        "volunteer": volunteer_name,
        "score": score,
        "signals_found": signals_found,
        "mi_score": mi_score,
        "session_number": len(session_data) + 1
    })

def get_sessions(volunteer_name: str):
    return [s for s in session_data if s["volunteer"] == volunteer_name]

def clear_sessions():
    session_data.clear()
```

---

## Step 4: Create `pipeline.py`

```python
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import (
    RISK_DETECTION_PROMPT,
    CONFIDENCE_SCORING_PROMPT,
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

def run_pipeline(transcript: str) -> dict:
    # Step 1: Risk signal detection
    raw_signals = call_gpt(RISK_DETECTION_PROMPT, f"TRANSCRIPT:\n{transcript}")
    signals = safe_parse(raw_signals)
    if isinstance(signals, dict) and "error" in signals:
        return {"error": "Risk detection failed", "details": signals}

    # Step 2: Confidence scoring
    raw_confidence = call_gpt(CONFIDENCE_SCORING_PROMPT, f"FLAGGED SIGNALS:\n{json.dumps(signals, indent=2)}")
    confidence_scores = safe_parse(raw_confidence)

    # Merge confidence into signals
    confidence_map = {}
    if isinstance(confidence_scores, list):
        for c in confidence_scores:
            confidence_map[c.get("exchange_number")] = c

    for signal in signals:
        ex = signal.get("exchange_number")
        if ex in confidence_map:
            signal["confidence"] = confidence_map[ex].get("confidence", "UNKNOWN")
            signal["confidence_reasoning"] = confidence_map[ex].get("confidence_reasoning", "")

    # Step 3: MI scoring
    raw_mi = call_gpt(MI_SCORING_PROMPT, f"TRANSCRIPT:\n{transcript}")
    mi_results = safe_parse(raw_mi)

    # Step 4: Coaching feedback
    coaching_input = f"""TRANSCRIPT:
{transcript}

DETECTED SIGNALS:
{json.dumps(signals, indent=2)}

MI SCORING:
{json.dumps(mi_results, indent=2)}
"""
    raw_coaching = call_gpt(COACHING_PROMPT, coaching_input)
    coaching = safe_parse(raw_coaching)

    return {
        "signals": signals,
        "mi_results": mi_results,
        "coaching": coaching
    }
```

---

## Step 5: Create `redteam.py`

```python
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import ADVERSARIAL_TRANSCRIPT_PROMPT, RISK_DETECTION_PROMPT

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
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def safe_parse(raw: str):
    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        return {"error": str(e), "raw": raw}

def generate_adversarial_transcript(num_signals: int = 3) -> dict:
    prompt = ADVERSARIAL_TRANSCRIPT_PROMPT.format(num_signals=num_signals)
    raw = call_gpt("You are a crisis training content designer.", prompt)
    result = safe_parse(raw)
    return result

def evaluate_recall(transcript: str, ground_truth: list) -> dict:
    # Run the detection step on the adversarial transcript
    raw_signals = call_gpt(RISK_DETECTION_PROMPT, f"TRANSCRIPT:\n{transcript}")
    detected = safe_parse(raw_signals)

    if isinstance(detected, dict) and "error" in detected:
        return {"error": "Detection failed", "details": detected}

    detected_exchanges = set()
    if isinstance(detected, list):
        for d in detected:
            detected_exchanges.add(d.get("exchange_number"))

    planted_exchanges = set()
    for gt in ground_truth:
        planted_exchanges.add(gt.get("exchange_number"))

    caught = planted_exchanges & detected_exchanges
    missed = planted_exchanges - detected_exchanges
    false_positives = detected_exchanges - planted_exchanges

    recall = len(caught) / len(planted_exchanges) if planted_exchanges else 0

    return {
        "total_planted": len(planted_exchanges),
        "total_detected": len(detected_exchanges),
        "caught": sorted(list(caught)),
        "missed": sorted(list(missed)),
        "false_positives": sorted(list(false_positives)),
        "recall_score": round(recall * 100, 1),
        "detected_signals": detected
    }
```

---

## Step 6: Create `app.py`

```python
import streamlit as st
import json
from pipeline import run_pipeline
from redteam import generate_adversarial_transcript, evaluate_recall
from session_store import add_session, get_sessions, clear_sessions

st.set_page_config(
    page_title="CrisisLens",
    page_icon="🔍",
    layout="wide"
)

# Header
st.title("🔍 CrisisLens")
st.caption("AI-powered coaching assistant for crisis hotline volunteer training")
st.divider()

# Sidebar
with st.sidebar:
    st.header("Navigation")
    mode = st.radio("Mode", ["Transcript Analysis", "Red-Team Mode", "Progress Tracker"])
    st.divider()
    volunteer_name = st.text_input("Volunteer Name", value="Trainee")
    st.caption("Used for longitudinal tracking within this session.")
    if st.button("Clear Session Data"):
        clear_sessions()
        st.success("Session cleared.")

# ── MODE 1: Transcript Analysis ──────────────────────────────────────────────
if mode == "Transcript Analysis":
    st.subheader("Submit a Practice Transcript")
    st.caption("Paste a simulated crisis call transcript below. Label turns as 'Caller:' and 'Volunteer:'.")

    sample_options = {
        "None": "",
        "Easy": open("sample_transcripts/easy.txt").read(),
        "Medium": open("sample_transcripts/medium.txt").read(),
        "Hard": open("sample_transcripts/hard.txt").read()
    }
    sample_choice = st.selectbox("Load a sample transcript", list(sample_options.keys()))
    transcript_input = st.text_area(
        "Transcript",
        value=sample_options[sample_choice],
        height=300,
        placeholder="Volunteer: Hi, thanks for calling. How are you doing today?\nCaller: Not great, honestly..."
    )

    if st.button("Analyze Transcript", type="primary"):
        if not transcript_input.strip():
            st.error("Please paste a transcript first.")
        else:
            with st.spinner("Running 4-step pipeline... this takes 20-30 seconds."):
                results = run_pipeline(transcript_input)

            if "error" in results:
                st.error(f"Pipeline error: {results['error']}")
            else:
                signals = results.get("signals", [])
                mi = results.get("mi_results", {})
                coaching = results.get("coaching", {})

                score = coaching.get("score", 0) if isinstance(coaching, dict) else 0
                mi_score = mi.get("overall_mi_score", 0) if isinstance(mi, dict) else 0

                # Save to session
                add_session(volunteer_name, score, len(signals), mi_score)

                # ── Summary Metrics ──
                st.subheader("Results")
                col1, col2, col3 = st.columns(3)
                col1.metric("Overall Score", f"{score}/100")
                col2.metric("Risk Signals Found", len(signals))
                col3.metric("MI Score", f"{mi_score}/100")

                # ── Risk Signals ──
                st.subheader("Risk Signals Detected")
                if not signals:
                    st.info("No risk signals detected.")
                else:
                    for sig in signals:
                        confidence = sig.get("confidence", "UNKNOWN")
                        color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(confidence, "⚪")
                        with st.expander(f"{color} Exchange {sig.get('exchange_number')} — {sig.get('category')} [{confidence}]"):
                            st.write(f"**Caller said:** \"{sig.get('caller_text')}\"")
                            st.write(f"**Reasoning:** {sig.get('reasoning')}")
                            st.write(f"**Confidence reasoning:** {sig.get('confidence_reasoning')}")

                # ── MI Feedback ──
                st.subheader("Motivational Interviewing Assessment")
                if isinstance(mi, dict) and "error" not in mi:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write("**Strengths**")
                        for s in mi.get("strengths", []):
                            st.success(s)
                    with col_b:
                        st.write("**Gaps**")
                        for g in mi.get("gaps", []):
                            st.warning(g)
                    if mi.get("critical_misses"):
                        st.write("**Critical Misses**")
                        for cm in mi.get("critical_misses", []):
                            st.error(str(cm))

                # ── Coaching Notes ──
                st.subheader("Coaching Feedback")
                if isinstance(coaching, dict) and "error" not in coaching:
                    st.info(coaching.get("summary", ""))
                    for pf in coaching.get("priority_feedback", []):
                        with st.expander(f"Exchange {pf.get('exchange')} — {pf.get('issue')}"):
                            st.write(f"**Caller said:** \"{pf.get('caller_signal')}\"")
                            st.write(f"**Volunteer said:** \"{pf.get('volunteer_response')}\"")
                            st.write(f"**Better response:** {pf.get('recommended_response')}")
                    st.write("**MI Feedback:**", coaching.get("mi_feedback", ""))

# ── MODE 2: Red-Team Mode ─────────────────────────────────────────────────────
elif mode == "Red-Team Mode":
    st.subheader("🎯 Red-Team Mode — Adversarial Transcript Evaluation")
    st.write(
        "Generate a practice transcript with deliberately buried risk signals, "
        "then test whether CrisisLens catches them. **Recall rate is the primary evaluation metric.**"
    )

    num_signals = st.slider("Number of planted signals", min_value=2, max_value=5, value=3)

    if st.button("Generate Adversarial Transcript", type="primary"):
        with st.spinner("Generating adversarial transcript..."):
            result = generate_adversarial_transcript(num_signals=num_signals)

        if isinstance(result, dict) and "error" not in result:
            st.session_state["adversarial_transcript"] = result.get("transcript", "")
            st.session_state["ground_truth"] = result.get("ground_truth", [])
            st.success("Adversarial transcript generated.")

    if "adversarial_transcript" in st.session_state:
        st.subheader("Generated Transcript")
        st.text_area("Adversarial Transcript", value=st.session_state["adversarial_transcript"], height=300)

        with st.expander("👁 Reveal Ground Truth (planted signals)"):
            for gt in st.session_state.get("ground_truth", []):
                st.write(f"- Exchange {gt.get('exchange_number')}: **{gt.get('category')}** — \"{gt.get('planted_text')}\"")

        if st.button("Run Recall Evaluation", type="primary"):
            with st.spinner("Evaluating recall..."):
                recall_results = evaluate_recall(
                    st.session_state["adversarial_transcript"],
                    st.session_state["ground_truth"]
                )

            if "error" in recall_results:
                st.error(f"Evaluation failed: {recall_results['error']}")
            else:
                st.subheader("Recall Evaluation Results")
                col1, col2, col3 = st.columns(3)
                col1.metric("Recall Score", f"{recall_results['recall_score']}%")
                col2.metric("Signals Planted", recall_results['total_planted'])
                col3.metric("Signals Caught", len(recall_results['caught']))

                if recall_results['caught']:
                    st.success(f"✅ Caught at exchanges: {recall_results['caught']}")
                if recall_results['missed']:
                    st.error(f"❌ Missed at exchanges: {recall_results['missed']}")
                if recall_results['false_positives']:
                    st.warning(f"⚠️ False positives at exchanges: {recall_results['false_positives']}")

                with st.expander("Full detected signals"):
                    st.json(recall_results.get("detected_signals", []))

# ── MODE 3: Progress Tracker ──────────────────────────────────────────────────
elif mode == "Progress Tracker":
    st.subheader("📈 Longitudinal Progress Tracker")
    sessions = get_sessions(volunteer_name)

    if not sessions:
        st.info(f"No sessions found for '{volunteer_name}'. Submit transcripts in Transcript Analysis mode first.")
    else:
        st.write(f"Showing {len(sessions)} session(s) for **{volunteer_name}**")

        # Table
        st.dataframe(
            [{
                "Session": s["session_number"],
                "Overall Score": s["score"],
                "Risk Signals Found": s["signals_found"],
                "MI Score": s["mi_score"]
            } for s in sessions],
            use_container_width=True
        )

        # Trend
        if len(sessions) > 1:
            import pandas as pd
            df = pd.DataFrame(sessions)
            st.line_chart(df.set_index("session_number")[["score", "mi_score"]])

        # Delta
        if len(sessions) >= 2:
            first = sessions[0]
            last = sessions[-1]
            delta_score = last["score"] - first["score"]
            delta_mi = last["mi_score"] - first["mi_score"]
            col1, col2 = st.columns(2)
            col1.metric("Score Change", f"{delta_score:+d} pts", delta=delta_score)
            col2.metric("MI Score Change", f"{delta_mi:+d} pts", delta=delta_mi)
```

---

## Step 7: Create Sample Transcripts

Create the folder `sample_transcripts/` and these three files:

### `sample_transcripts/easy.txt`
```
Volunteer: Hi, thanks for calling the helpline. How are you doing today?
Caller: Not good. I just feel like nothing matters anymore.
Volunteer: I'm sorry to hear that. Can you tell me more about what's going on?
Caller: I've been really depressed lately. I don't want to be here anymore.
Volunteer: That sounds really hard. Are you having thoughts of hurting yourself?
Caller: Yeah, honestly. I think about it a lot.
Volunteer: I'm glad you told me. You're not alone in this. Can we talk about what's been happening?
Caller: I guess. I just feel like everyone would be better off without me.
Volunteer: I hear you. Those feelings are real. Let's stay on the line together and figure out next steps.
```

### `sample_transcripts/medium.txt`
```
Volunteer: Thank you for calling. What's on your mind tonight?
Caller: I don't even know why I called. I just feel really off lately.
Volunteer: That's okay. I'm here. What does "off" feel like for you?
Caller: Like nothing's going to get better. I've been sleeping way too much, not eating. Just going through the motions.
Volunteer: How long have you been feeling this way?
Caller: Months. I started giving away some of my stuff last week, which is kind of weird I guess.
Volunteer: What made you decide to do that?
Caller: I don't know, I just figured I wouldn't need it. It felt freeing actually.
Volunteer: That's interesting. Are you working or in school?
Caller: I quit my job. Seemed pointless. I've been writing a lot too. Kind of like, wrapping things up in my head.
Volunteer: Writing can be really therapeutic. What do you like to write about?
Caller: Just thoughts. Things I want people to know. Like letters almost.
Volunteer: That sounds meaningful. Do you have people around you, family or friends?
Caller: Not really. I think they'll understand once I'm gone.
Volunteer: That phrase, once I'm gone, what do you mean by that?
Caller: Nothing. Forget I said it.
```

### `sample_transcripts/hard.txt`
```
Volunteer: Hi there, thanks for calling. What's going on for you today?
Caller: Oh I'm okay I guess. Just wanted to talk to someone.
Volunteer: Of course, I'm glad you called. How's your week been?
Caller: Pretty normal. I've been cleaning out my apartment actually, feels good to declutter.
Volunteer: That's a great feeling. Spring cleaning?
Caller: Something like that. I've been thinking about taking a long trip actually, somewhere far. Somewhere peaceful.
Volunteer: Oh nice, any destinations in mind?
Caller: Not really. Somewhere I won't have to think so much. My brain has been really loud lately.
Volunteer: What do you mean by loud?
Caller: Just like, constant noise. I've started taking evening walks to quiet it down. Really long walks.
Volunteer: Walking is great for that. Where do you usually go?
Caller: Near the bridge by my place. It's quiet there at night. I like looking at the water.
Volunteer: That sounds peaceful. Have things been stressful at work or home?
Caller: Not really. Actually things are surprisingly calm. I feel like I've made peace with a lot of stuff lately.
Volunteer: That sounds like a positive shift.
Caller: Yeah. I looked up some old friends online. Wanted to see how they were doing. Just in case.
Volunteer: That's sweet, staying connected.
Caller: I guess. I sent some of them messages. Told them what they meant to me. Figured it was time.
Volunteer: That's thoughtful of you.
Caller: Yeah. Anyway, I should probably let you go. I think I have everything I need.
```

---

## Step 8: Create `README.md`

```markdown
# CrisisLens

An AI-powered coaching assistant for mental health crisis hotline volunteer training.

## What It Does

CrisisLens analyzes simulated crisis call transcripts through a four-step agentic pipeline:

1. **Risk Signal Detection** — flags language mapping to Columbia Suicide Severity Rating Scale (C-SSRS) criteria
2. **Confidence Scoring** — rates certainty on every flagged signal with clinical reasoning
3. **MI Response Scoring** — evaluates volunteer responses against Motivational Interviewing principles
4. **Coaching Feedback** — generates exchange-level coaching notes with recommended responses

**Red-Team Mode** generates adversarial transcripts with buried risk signals and measures recall rate — the primary evaluation metric.

**Progress Tracker** shows a volunteer's improvement across multiple sessions.

## Setup

```bash
git clone https://github.com/Kavin-Jha/crisislens.git
cd crisislens
pip install -r requirements.txt
# Add your OpenAI API key to .env:
# OPENAI_API_KEY=your_key_here
streamlit run app.py
```

## Clinical Frameworks

- [Columbia Suicide Severity Rating Scale (C-SSRS)](https://cssrs.columbia.edu)
- [SAMHSA Motivational Interviewing Guidelines](https://www.samhsa.gov)

## Data & Privacy

All transcripts are synthetic. No real caller data is used at any point. Session data exists only in memory during a local run and is never persisted externally.

## Tech Stack

- Python 3.10+
- Streamlit
- OpenAI GPT-4o
- No vector database, no fine-tuning, no external deployment required

## Evaluation

Primary metric: **Recall rate on adversarial transcripts** — what percentage of deliberately buried C-SSRS signals does the system catch? Use Red-Team Mode to run this evaluation.
```

---

## Step 9: Git Commit and Push

After all files are created and verified:

```bash
git add .
git commit -m "feat: initial CrisisLens implementation with 4-step pipeline and red-team mode"
git push origin main
```

---

## Step 10: Final Verification Checklist

Before declaring done, verify each item:

- [ ] `requirements.txt` exists
- [ ] `app.py` exists and is complete
- [ ] `pipeline.py` exists and is complete
- [ ] `redteam.py` exists and is complete
- [ ] `session_store.py` exists and is complete
- [ ] `prompts.py` exists and is complete
- [ ] `sample_transcripts/easy.txt` exists
- [ ] `sample_transcripts/medium.txt` exists
- [ ] `sample_transcripts/hard.txt` exists
- [ ] `README.md` exists
- [ ] `.env` is in `.gitignore` (DO NOT push the API key)
- [ ] Run `streamlit run app.py` and confirm it launches without errors
- [ ] All files are pushed to GitHub

## Important Rules

- Never read, print, or expose the contents of `.env`
- Never hardcode any API key
- Do not add any files not listed above
- Do not install any packages not in `requirements.txt`
- If `streamlit run app.py` throws an import error, fix it before declaring done