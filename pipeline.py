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
