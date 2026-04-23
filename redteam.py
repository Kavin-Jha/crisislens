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
