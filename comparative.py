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
