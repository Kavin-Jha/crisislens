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
