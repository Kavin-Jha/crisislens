"""
CrisisLens Test Suite
Tests the four-step pipeline, confidence scoring, and Red-Team recall evaluation
against sample transcripts to verify system correctness.

Run with:
    python tests.py
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# ── Helpers ───────────────────────────────────────────────────────────────────

PASS = "\033[92m PASS\033[0m"
FAIL = "\033[91m FAIL\033[0m"
INFO = "\033[94m INFO\033[0m"

def check(condition, label):
    status = PASS if condition else FAIL
    print(f"  [{status}] {label}")
    return condition

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ── Sample transcript for testing ─────────────────────────────────────────────

SAMPLE_TRANSCRIPT = open("sample_transcripts/easy.txt").read()

FAREWELL_TRANSCRIPT = open("sample_transcripts/farewell.txt").read()

ADVERSARIAL_TRANSCRIPT = """
Volunteer: Hi, thanks for calling. How are you doing today?
Caller: I'm okay I guess. Just wanted to talk. I've been thinking a lot lately.
Volunteer: Of course, I'm here. What's been on your mind?
Caller: I don't know. I feel like I'm just going through the motions. Like nothing really matters anymore.
Volunteer: That sounds really hard. How long have you been feeling this way?
Caller: A while. I've started giving some of my stuff away actually. Feels good to simplify.
Volunteer: That's a great idea, decluttering can be really therapeutic.
Caller: Yeah. I also wrote some letters to people I care about. Just things I wanted them to know.
Volunteer: That's really thoughtful of you.
Caller: I hope so. Anyway, I should let you go. I think I have everything sorted now.
"""

ADVERSARIAL_GROUND_TRUTH = [
    {"exchange_number": 4, "category": "Hopelessness Marker", "planted_text": "nothing really matters anymore"},
    {"exchange_number": 6, "category": "Preparatory Behavior", "planted_text": "giving some of my stuff away"},
    {"exchange_number": 8, "category": "Preparatory Behavior", "planted_text": "wrote some letters to people I care about"},
]

# ── Test 1: Environment ───────────────────────────────────────────────────────

section("TEST 1: Environment and Dependencies")

api_key = os.getenv("OPENAI_API_KEY")
has_key = api_key is not None and api_key != "your-key-here" and len(api_key) > 10
check(has_key, "OPENAI_API_KEY is set and non-empty")

try:
    import openai
    check(True, "openai package is importable")
except ImportError:
    check(False, "openai package is importable")

try:
    import streamlit
    check(True, "streamlit package is importable")
except ImportError:
    check(False, "streamlit package is importable")

try:
    import dotenv
    check(True, "python-dotenv package is importable")
except ImportError:
    check(False, "python-dotenv package is importable")

# ── Test 2: Sample files ──────────────────────────────────────────────────────

section("TEST 2: Sample Transcripts")

for fname in ["easy.txt", "medium.txt", "hard.txt", "farewell.txt"]:
    path = f"sample_transcripts/{fname}"
    exists = os.path.exists(path)
    if exists:
        content = open(path).read()
        has_content = len(content.strip()) > 50
        check(has_content, f"sample_transcripts/{fname} exists and has content")
    else:
        check(False, f"sample_transcripts/{fname} exists and has content")

# ── Test 3: Module imports ────────────────────────────────────────────────────

section("TEST 3: Module Imports")

modules = ["pipeline", "redteam", "session_store", "prompts",
           "styles", "scenario_generator", "comparative",
           "report_generator", "export_utils"]

import_results = {}
for mod in modules:
    try:
        m = __import__(mod)
        import_results[mod] = True
        check(True, f"{mod}.py imports without errors")
    except Exception as e:
        import_results[mod] = False
        check(False, f"{mod}.py imports without errors — {e}")

# ── Test 4: Prompt structure ──────────────────────────────────────────────────

section("TEST 4: Prompt Structure Validation")

if import_results.get("prompts"):
    import prompts

    check(hasattr(prompts, "RISK_DETECTION_PROMPT"), "RISK_DETECTION_PROMPT defined")
    check(hasattr(prompts, "CONFIDENCE_SCORING_PROMPT"), "CONFIDENCE_SCORING_PROMPT defined")
    check(hasattr(prompts, "MI_SCORING_PROMPT"), "MI_SCORING_PROMPT defined")
    check(hasattr(prompts, "COACHING_PROMPT"), "COACHING_PROMPT defined")
    check(hasattr(prompts, "ADVERSARIAL_TRANSCRIPT_PROMPT"), "ADVERSARIAL_TRANSCRIPT_PROMPT defined")

    check("C-SSRS" in prompts.RISK_DETECTION_PROMPT, "RISK_DETECTION_PROMPT references C-SSRS")
    check("Motivational Interviewing" in prompts.MI_SCORING_PROMPT, "MI_SCORING_PROMPT references Motivational Interviewing")
    check("JSON" in prompts.COACHING_PROMPT or "json" in prompts.COACHING_PROMPT, "COACHING_PROMPT requests JSON output")
    check(len(prompts.RISK_DETECTION_PROMPT) > 300, "RISK_DETECTION_PROMPT has sufficient detail (>300 chars)")
else:
    print("  [SKIP] prompts.py failed to import, skipping prompt tests")

# ── Test 5: Session store ─────────────────────────────────────────────────────

section("TEST 5: Session Store")

if import_results.get("session_store"):
    import session_store

    session_store.clear_sessions()
    initial = session_store.get_sessions("test_volunteer")
    check(initial == [], "get_sessions returns empty list for new volunteer")

    session_store.add_session("test_volunteer", 75, 3, 80)
    session_store.add_session("test_volunteer", 85, 4, 90)
    sessions = session_store.get_sessions("test_volunteer")
    check(len(sessions) == 2, "add_session correctly stores two sessions")
    check(sessions[0]["score"] == 75, "first session score is correct")
    check(sessions[1]["score"] == 85, "second session score is correct")
    check(sessions[0]["session_number"] == 1, "session numbers are sequential")

    other = session_store.get_sessions("other_volunteer")
    check(other == [], "sessions are isolated per volunteer name")

    session_store.clear_sessions()
    cleared = session_store.get_sessions("test_volunteer")
    check(cleared == [], "clear_sessions empties all session data")
else:
    print("  [SKIP] session_store.py failed to import")

# ── Test 6: Export utils ──────────────────────────────────────────────────────

section("TEST 6: Export Utils")

if import_results.get("export_utils"):
    import export_utils

    check(hasattr(export_utils, "generate_markdown_report"), "generate_markdown_report function exists")

    mock_results = {
        "signals": [
            {
                "exchange_number": 3,
                "caller_text": "I don't see the point anymore",
                "category": "Passive Ideation",
                "confidence": "HIGH",
                "reasoning": "Caller expresses loss of purpose.",
                "confidence_reasoning": "Unambiguous passive ideation."
            }
        ],
        "mi_results": {
            "overall_mi_score": 70,
            "strengths": ["Good reflective listening in exchange 1"],
            "gaps": ["Failed to explore risk signal at exchange 3"],
            "critical_misses": ["Exchange 3: missed passive ideation indicator"]
        },
        "coaching": {
            "summary": "The volunteer showed some MI technique but missed a critical signal.",
            "priority_feedback": [
                {
                    "exchange": 3,
                    "issue": "Missed passive ideation signal",
                    "caller_signal": "I don't see the point anymore",
                    "volunteer_response": "That sounds tough.",
                    "recommended_response": "When you say you don't see the point, can you tell me more about what you mean?"
                }
            ],
            "mi_feedback": "Overall MI technique needs improvement around signal exploration.",
            "score": 65
        }
    }

    try:
        report = export_utils.generate_markdown_report("Test Volunteer", SAMPLE_TRANSCRIPT, mock_results)
        check(isinstance(report, str), "generate_markdown_report returns a string")
        check(len(report) > 100, "report has substantial content (>100 chars)")
        check("Test Volunteer" in report, "report includes volunteer name")
        check("Risk" in report or "Signal" in report, "report includes risk signal section")
    except Exception as e:
        check(False, f"generate_markdown_report runs without error — {e}")
else:
    print("  [SKIP] export_utils.py failed to import")

# ── Test 7: Pipeline (live API call) ──────────────────────────────────────────

section("TEST 7: Pipeline — Live API Call")
print("  [INFO] This test makes real API calls. It may take 30-60 seconds.")

if not has_key:
    print("  [SKIP] No valid API key found. Set OPENAI_API_KEY to run live tests.")
elif not import_results.get("pipeline"):
    print("  [SKIP] pipeline.py failed to import")
else:
    try:
        from pipeline import run_pipeline

        print("  [INFO] Running pipeline on easy sample transcript...")
        results = run_pipeline(SAMPLE_TRANSCRIPT)

        check("error" not in results, "pipeline returns without error")
        check("signals" in results, "pipeline returns 'signals' key")
        check("mi_results" in results, "pipeline returns 'mi_results' key")
        check("coaching" in results, "pipeline returns 'coaching' key")

        signals = results.get("signals", [])
        check(isinstance(signals, list), "signals is a list")
        check(len(signals) > 0, f"pipeline detected at least 1 signal (found {len(signals)})")

        if signals:
            s = signals[0]
            check("exchange_number" in s, "signal has exchange_number field")
            check("caller_text" in s, "signal has caller_text field")
            check("category" in s, "signal has category field")
            check("confidence" in s, "signal has confidence field (from step 2)")
            check(s.get("confidence") in ["HIGH", "MEDIUM", "LOW"], "confidence is valid value")

        mi = results.get("mi_results", {})
        check(isinstance(mi, dict), "mi_results is a dict")
        check("overall_mi_score" in mi, "mi_results has overall_mi_score")
        if "overall_mi_score" in mi:
            score = mi["overall_mi_score"]
            check(isinstance(score, (int, float)) and 0 <= score <= 100, f"MI score is 0-100 (got {score})")

        coaching = results.get("coaching", {})
        check(isinstance(coaching, dict), "coaching is a dict")
        check("score" in coaching, "coaching has score field")
        check("summary" in coaching, "coaching has summary field")
        check("priority_feedback" in coaching, "coaching has priority_feedback field")

        print(f"\n  [INFO] Pipeline results summary:")
        print(f"         Signals found:  {len(signals)}")
        print(f"         MI score:       {mi.get('overall_mi_score', 'N/A')}/100")
        print(f"         Overall score:  {coaching.get('score', 'N/A')}/100")

    except Exception as e:
        check(False, f"pipeline runs without exception — {e}")

# ── Test 8: Red-Team recall ───────────────────────────────────────────────────

section("TEST 8: Red-Team Recall Evaluation")
print("  [INFO] This test makes real API calls.")

if not has_key:
    print("  [SKIP] No valid API key found.")
elif not import_results.get("redteam"):
    print("  [SKIP] redteam.py failed to import")
else:
    try:
        from redteam import evaluate_recall

        print("  [INFO] Running recall evaluation on known adversarial transcript...")
        recall = evaluate_recall(ADVERSARIAL_TRANSCRIPT, ADVERSARIAL_GROUND_TRUTH)

        check("error" not in recall, "recall evaluation returns without error")
        check("recall_score" in recall, "recall result has recall_score")
        check("total_planted" in recall, "recall result has total_planted")
        check("caught" in recall, "recall result has caught")
        check("missed" in recall, "recall result has missed")

        if "total_planted" in recall:
            check(recall["total_planted"] == 3, f"total_planted is 3 (got {recall.get('total_planted')})")

        if "recall_score" in recall:
            score = recall["recall_score"]
            check(0 <= score <= 100, f"recall score is 0-100 (got {score})")
            print(f"\n  [INFO] Recall score on adversarial transcript: {score}%")
            print(f"         Caught:          {recall.get('caught', [])}")
            print(f"         Missed:          {recall.get('missed', [])}")
            print(f"         False positives: {recall.get('false_positives', [])}")

    except Exception as e:
        check(False, f"recall evaluation runs without exception — {e}")

# ── Test 9: Farewell transcript signal count ──────────────────────────────────

section("TEST 9: Farewell Transcript — Clinical Validation")
print("  [INFO] Tests that the Farewell transcript yields meaningful signal detection.")

if not has_key:
    print("  [SKIP] No valid API key found.")
elif not import_results.get("pipeline"):
    print("  [SKIP] pipeline.py failed to import")
else:
    try:
        from pipeline import run_pipeline

        print("  [INFO] Running pipeline on Farewell transcript (hardest test case)...")
        results = run_pipeline(FAREWELL_TRANSCRIPT)

        signals = results.get("signals", [])
        coaching = results.get("coaching", {})

        check(len(signals) >= 4, f"Farewell transcript yields at least 4 signals (found {len(signals)})")

        high_conf = [s for s in signals if s.get("confidence") == "HIGH"]
        check(len(high_conf) >= 1, f"At least 1 HIGH confidence signal detected (found {len(high_conf)})")

        score = coaching.get("score", 0) if isinstance(coaching, dict) else 0
        check(score < 80, f"Volunteer score reflects missed signals (score {score}/100, expected <80)")

        print(f"\n  [INFO] Farewell transcript results:")
        print(f"         Total signals:   {len(signals)}")
        print(f"         HIGH confidence: {len(high_conf)}")
        print(f"         Volunteer score: {score}/100")

    except Exception as e:
        check(False, f"Farewell pipeline runs without exception — {e}")

# ── Summary ───────────────────────────────────────────────────────────────────

section("TEST SUITE COMPLETE")
print("\n  Tests 1-6 validate structure and imports without API calls.")
print("  Tests 7-9 make live API calls and validate output correctness.")
print("\n  To run only structural tests (no API calls):")
print("  Comment out Tests 7-9 or unset OPENAI_API_KEY.\n")
