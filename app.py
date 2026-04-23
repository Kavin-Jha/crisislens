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
