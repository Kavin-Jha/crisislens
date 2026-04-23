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
