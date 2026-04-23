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
