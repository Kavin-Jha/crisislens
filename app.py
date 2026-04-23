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
from export_utils import generate_markdown_report

st.set_page_config(
    page_title="CrisisLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(load_css(), unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 4px 0 12px 0;">
        <div style="font-family: 'Space Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #0FF4C6; line-height: 1;">CrisisLens</div>
        <div style="font-size: 0.65rem; color: #4A5568; text-transform: uppercase; letter-spacing: 0.14em; margin-top: 4px;">AI Training Coach</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    mode = st.radio(
        "Navigation",
        [
            "🏠  Overview",
            "📋  Transcript Analysis",
            "⚔️  Red-Team Mode",
            "🎯  Scenario Generator",
            "⚖️  Comparative Analysis",
            "📈  Progress Tracker",
        ],
        label_visibility="collapsed"
    )

    st.divider()

    volunteer_name = st.text_input("Volunteer Name", value="Trainee", help="Used for longitudinal tracking")
    st.session_state["_vol_name_cache"] = volunteer_name

    _sidebar_sessions = get_sessions(volunteer_name)
    _session_count = len(_sidebar_sessions)
    if _session_count > 0:
        st.markdown(
            f'<div class="session-count"><strong>{_session_count}</strong> sessions logged</div>',
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown('<div class="cl-label">C-SSRS REFERENCE</div>', unsafe_allow_html=True)
    for _title, _desc in [
        ("Passive Ideation", "Wishes to be dead, no plan"),
        ("Active Ideation", "Thinking about suicide, no method"),
        ("Ideation + Plan", "Has a method in mind"),
        ("Preparatory", "Taking steps toward attempt"),
        ("Veiled Signal", "Indirect language suggesting ideation"),
        ("Hopelessness", "Deep meaninglessness, clinically significant"),
    ]:
        st.markdown(f"""
        <div class="framework-item">
            <div class="framework-item-title">{_title}</div>
            <div class="framework-item-desc">{_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="cl-label" style="margin-top:16px;">MI PRINCIPLES</div>', unsafe_allow_html=True)
    for _title, _desc in [
        ("Reflective Listening", "Accurately reflects caller's emotional state"),
        ("Open-Ended Questions", "Invites elaboration, not yes/no"),
        ("Affirmation", "Acknowledges caller's strengths"),
        ("Avoid Leading", "Does not suggest answers or minimize"),
        ("Escalation", "Explores risk signals, does not pivot away"),
    ]:
        st.markdown(f"""
        <div class="framework-item">
            <div class="framework-item-title">{_title}</div>
            <div class="framework-item-desc">{_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
    if st.button("Clear Session Data"):
        clear_sessions()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


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
        <div class="signal-reasoning" style="margin-top: 4px; font-style: italic; color: #4A5568;">{sig.get('confidence_reasoning', '')}</div>
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


def render_metrics(score, signals_count, mi_score, export_data=None):
    col1, col2, col3, col_exp = st.columns([1, 1, 1, 0.8])
    with col1:
        st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{score}</div><div class="cl-metric-label">Overall Score</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{signals_count}</div><div class="cl-metric-label">Risk Signals</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="cl-metric"><div class="cl-metric-value">{mi_score}</div><div class="cl-metric-label">MI Score</div></div>', unsafe_allow_html=True)
    with col_exp:
        if export_data:
            vname, transcript, results = export_data
            _md = generate_markdown_report(vname, transcript, results)
            st.markdown('<div style="padding-top:10px;">', unsafe_allow_html=True)
            st.download_button(
                label="📄 Export",
                data=_md,
                file_name=f"crisislens_{vname.replace(' ', '_')}.md",
                mime="text/markdown",
                help="Download analysis as Markdown"
            )
            st.markdown('</div>', unsafe_allow_html=True)


def run_pipeline_with_progress(transcript):
    steps = [
        "Scanning for C-SSRS risk signals",
        "Calibrating confidence scores",
        "Evaluating MI technique",
        "Generating coaching feedback",
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
                html += f'<div class="pipeline-step" style="opacity:0.35;">○ &nbsp; {s}</div>'
        placeholder.markdown(f'<div style="margin:14px 0;">{html}</div>', unsafe_allow_html=True)
        time.sleep(0.35)
    results = run_pipeline(transcript)
    placeholder.empty()
    return results


# ── Overview ─────────────────────────────────────────────────────────────────
if "Overview" in mode:
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 16px 0; max-width: 720px; margin: 0 auto;">
        <div class="hero-wordmark cl-fadein">CrisisLens<span class="cursor-blink">|</span></div>
        <div class="hero-mission">Clinically grounded AI coaching for crisis hotline volunteer training</div>
        <div class="stats-bar">
            <div class="stats-pill">
                <span class="stats-pill-num">5M+</span>
                <span class="stats-pill-label">contacts handled by 988 in 2023</span>
            </div>
            <div class="stats-pill">
                <span class="stats-pill-num">50%+</span>
                <span class="stats-pill-label">annual staff turnover</span>
            </div>
            <div class="stats-pill">
                <span class="stats-pill-num">2–3 hrs</span>
                <span class="stats-pill-label">manual review per trainee per week</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cl-label">ANALYSIS PIPELINE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pipeline-flow">
        <div class="pipeline-flow-step">
            <div class="pipeline-flow-num">01</div>
            <div class="pipeline-flow-title">Risk Detection</div>
            <div class="pipeline-flow-desc">Scans every exchange for C-SSRS language markers — including veiled and embedded signals</div>
        </div>
        <div class="pipeline-flow-arrow">›</div>
        <div class="pipeline-flow-step">
            <div class="pipeline-flow-num">02</div>
            <div class="pipeline-flow-title">Confidence Scoring</div>
            <div class="pipeline-flow-desc">Rates each signal HIGH / MEDIUM / LOW with clinical reasoning and calibration</div>
        </div>
        <div class="pipeline-flow-arrow">›</div>
        <div class="pipeline-flow-step">
            <div class="pipeline-flow-num">03</div>
            <div class="pipeline-flow-title">MI Evaluation</div>
            <div class="pipeline-flow-desc">Scores volunteer responses against SAMHSA Motivational Interviewing principles</div>
        </div>
        <div class="pipeline-flow-arrow">›</div>
        <div class="pipeline-flow-step">
            <div class="pipeline-flow-num">04</div>
            <div class="pipeline-flow-title">Coaching Feedback</div>
            <div class="pipeline-flow-desc">Exchange-level coaching with ranked alternative responses and supervisor summary</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cl-label">MODES</div>', unsafe_allow_html=True)
    _features = [
        ("📋", "Transcript Analysis", "Full 4-step pipeline on any practice transcript. Load a sample or paste your own."),
        ("⚔️", "Red-Team Mode", "Generate adversarial transcripts with buried signals and measure pipeline recall."),
        ("🎯", "Scenario Generator", "Six targeted scenario types for specific clinical training gaps."),
        ("⚖️", "Comparative Analysis", "Head-to-head scoring of two volunteers on the same scenario."),
        ("📈", "Progress Tracker", "Longitudinal improvement curves and AI-written supervisor report cards."),
    ]
    _feat_cols = st.columns(len(_features))
    for col, (icon, title, desc) in zip(_feat_cols, _features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-card-icon">{icon}</div>
                <div class="feature-card-title">{title}</div>
                <div class="feature-card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="attribution-line">
        Grounded in <strong>C-SSRS</strong> (cssrs.columbia.edu) and <strong>SAMHSA Motivational Interviewing Guidelines</strong>
        &nbsp;·&nbsp; All data synthetic &nbsp;·&nbsp; No real caller data
    </div>
    """, unsafe_allow_html=True)


# ── Transcript Analysis ───────────────────────────────────────────────────────
elif "Transcript" in mode:
    _piped = st.session_state.pop("piped_transcript", None)

    st.markdown('<div class="cl-page-header cl-fadein"><div class="page-title">Transcript Analysis</div><div class="page-subtitle">Paste a practice transcript to receive clinically grounded coaching feedback across four analytical dimensions.</div></div>', unsafe_allow_html=True)
    st.divider()

    if _piped:
        st.markdown('<div class="pipe-banner">📋 Transcript pre-loaded from another mode — click <strong>Analyze Transcript</strong> to run the full pipeline.</div>', unsafe_allow_html=True)

    sample_options = {
        "— Select a sample —": "",
        "Easy — Explicit Signals": open("sample_transcripts/easy.txt").read(),
        "Medium — Mixed Signals": open("sample_transcripts/medium.txt").read(),
        "Hard — Buried Signals": open("sample_transcripts/hard.txt").read(),
        "Farewell — The Hardest to Catch": open("sample_transcripts/farewell.txt").read(),
    }

    col_left, col_right = st.columns([13, 7])
    with col_left:
        sample_choice = st.selectbox("Load a sample transcript", list(sample_options.keys()))
        _default_text = _piped if _piped else sample_options[sample_choice]
        transcript_input = st.text_area(
            "Transcript",
            value=_default_text,
            height=300,
            placeholder="Volunteer: Hi, thanks for calling. How are you doing today?\nCaller: Not great, honestly...",
            label_visibility="collapsed"
        )
        word_count = len(transcript_input.split()) if transcript_input.strip() else 0
        if word_count >= 150:
            wc_class, wc_hint = "word-count-ok", f"{word_count} words — good length for accurate analysis"
        elif word_count >= 50:
            wc_class, wc_hint = "word-count-warn", f"{word_count} words — longer transcripts produce better results"
        elif word_count > 0:
            wc_class, wc_hint = "word-count-error", f"{word_count} words — transcript may be too short for reliable analysis"
        else:
            wc_class, wc_hint = "word-count-error", "Paste a transcript or load a sample above"
        st.markdown(f'<div class="{wc_class}">{wc_hint}</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="cl-card">
            <div class="cl-label">FORMAT GUIDE</div>
            <div style="color: #8896B3; font-size: 0.85rem; line-height: 1.8;">
                Label each turn:<br>
                <code style="color: #0FF4C6; font-family: 'Space Mono', monospace; font-size: 0.8rem;">Volunteer: ...</code><br>
                <code style="color: #0FF4C6; font-family: 'Space Mono', monospace; font-size: 0.8rem;">Caller: ...</code><br><br>
                Number exchanges or keep sequential.<br><br>
                <strong style="color: #C8D0E0;">Tip:</strong> Try <em>Farewell — The Hardest to Catch</em> to see how calm, positive-sounding callers can hide the most severe risk signals.
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
                st.session_state["_last_results"] = results
                st.session_state["_last_transcript"] = transcript_input

                st.components.v1.html(
                    "<script>setTimeout(()=>window.scrollTo({top:600,behavior:'smooth'}),300)</script>",
                    height=0
                )

                st.divider()
                render_metrics(
                    score, len(signals), mi_score,
                    export_data=(volunteer_name, transcript_input, results)
                )
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
                                st.markdown(f'<div class="cl-label" style="margin-top:12px;">{level} CONFIDENCE</div>', unsafe_allow_html=True)
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
                            st.markdown('<div class="cl-label">STRENGTHS</div>', unsafe_allow_html=True)
                            for s in mi.get("strengths", []):
                                st.markdown(f'<div class="strength-item">✓ &nbsp; {s}</div>', unsafe_allow_html=True)
                        with col_g:
                            st.markdown('<div class="cl-label">GAPS</div>', unsafe_allow_html=True)
                            for g in mi.get("gaps", []):
                                st.markdown(f'<div class="gap-item">⚠ &nbsp; {g}</div>', unsafe_allow_html=True)
                        if mi.get("critical_misses"):
                            st.markdown('<div class="cl-label" style="margin-top:16px;">CRITICAL MISSES</div>', unsafe_allow_html=True)
                            for cm in mi.get("critical_misses", []):
                                st.markdown(f'<div class="critical-item">✕ &nbsp; {cm}</div>', unsafe_allow_html=True)

                with tab4:
                    st.markdown('<div class="cl-section-header">Coaching Feedback</div>', unsafe_allow_html=True)
                    if isinstance(coaching, dict):
                        st.markdown(f"""
                        <div class="report-card">
                            <div class="report-title">Supervisor Summary</div>
                            <div style="color: #C8D0E0; line-height: 1.7; font-size: 0.9rem;">{coaching.get('summary', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        for pf in coaching.get("priority_feedback", []):
                            render_coaching_card(pf)
                            btn_key = f"alt_{pf.get('exchange')}_{id(pf)}"
                            if st.button(f"Generate 3 Alternative Responses — Exchange {pf.get('exchange')}", key=btn_key, type="secondary"):
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
                                    <div class="cl-card" style="border-left: 3px solid {color}; margin-left: 20px; margin-top: 8px;">
                                        <div style="font-family:'Space Mono',monospace; font-size:0.72rem; color:{color}; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.06em;">Rank {alt.get('rank')}</div>
                                        <div style="color:#C8D0E0; margin-bottom:8px; font-size:0.9rem;">"{alt.get('response','')}"</div>
                                        <div style="color:#8896B3; font-size:0.82rem; line-height:1.5;">{alt.get('why','')}</div>
                                    </div>
                                    """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="cl-card" style="margin-top:16px;">
                            <div class="cl-label">MI FEEDBACK</div>
                            <div style="color:#C8D0E0; line-height:1.65; margin-top:4px; font-size:0.9rem;">{coaching.get('mi_feedback','')}</div>
                        </div>
                        """, unsafe_allow_html=True)


# ── Red-Team Mode ─────────────────────────────────────────────────────────────
elif "Red-Team" in mode:
    st.markdown('<div class="cl-page-header cl-fadein"><div class="page-title">Red-Team Mode</div><div class="page-subtitle">Generate transcripts with buried risk signals, then measure what percentage the pipeline catches.</div></div>', unsafe_allow_html=True)
    st.divider()

    col_ctrl, col_btn = st.columns([2, 1])
    with col_ctrl:
        num_signals = st.slider("Planted signals", min_value=2, max_value=5, value=3)
    with col_btn:
        st.markdown('<div style="padding-top: 28px;">', unsafe_allow_html=True)
        gen_pressed = st.button("Generate Adversarial Transcript", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    if gen_pressed:
        with st.spinner("Generating adversarial transcript..."):
            result = generate_adversarial_transcript(num_signals=num_signals)
        if isinstance(result, dict) and "error" not in result:
            st.session_state["adversarial_transcript"] = result.get("transcript", "")
            st.session_state["ground_truth"] = result.get("ground_truth", [])
            st.success(f"Generated with {num_signals} buried signals.")
        else:
            st.error(f"Generation failed: {result.get('error', 'Unknown error')}")

    if "adversarial_transcript" in st.session_state:
        st.text_area(
            "Generated Transcript",
            value=st.session_state["adversarial_transcript"],
            height=280,
            label_visibility="collapsed"
        )

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
                        <div class="cl-label">RECALL SCORE</div>
                        <div class="recall-score-big {score_class}">{score}%</div>
                        <div style="color:#8896B3; font-size:0.8rem; margin-top:8px;">{recall['total_planted']} planted &nbsp;·&nbsp; {len(recall['caught'])} caught</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_d:
                    if recall.get("caught"):
                        st.markdown(f'<div class="strength-item">✓ &nbsp; Caught at exchanges: {recall["caught"]}</div>', unsafe_allow_html=True)
                    if recall.get("missed"):
                        st.markdown(f'<div class="critical-item">✕ &nbsp; Missed at exchanges: {recall["missed"]}</div>', unsafe_allow_html=True)
                    if recall.get("false_positives"):
                        st.markdown(f'<div class="gap-item">⚠ &nbsp; False positives at exchanges: {recall["false_positives"]}</div>', unsafe_allow_html=True)

                with st.expander("Full detected signals"):
                    st.json(recall.get("detected_signals", []))

                st.divider()
                if st.button("→ Run Full Pipeline on This Transcript"):
                    st.session_state["piped_transcript"] = st.session_state["adversarial_transcript"]
                    st.markdown('<div class="pipe-banner">Transcript queued — switch to <strong>Transcript Analysis</strong> to run the full pipeline.</div>', unsafe_allow_html=True)


# ── Scenario Generator ────────────────────────────────────────────────────────
elif "Scenario" in mode:
    st.markdown('<div class="cl-page-header cl-fadein"><div class="page-title">Scenario Generator</div><div class="page-subtitle">Generate targeted practice transcripts for six specific clinical training gap scenarios.</div></div>', unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        scenario_type = st.selectbox("Scenario Type", list(SCENARIO_TYPES.keys()))
        difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Hard")
        gen_btn = st.button("Generate Scenario", type="primary")
    with col2:
        st.markdown(f"""
        <div class="cl-card">
            <div class="cl-label">{scenario_type.upper()}</div>
            <div style="color:#C8D0E0; font-size:0.88rem; line-height:1.65;">{SCENARIO_TYPES.get(scenario_type,'')}</div>
            <div style="margin-top:14px;">
                <span class="scenario-tag">{difficulty}</span>
                <span class="scenario-tag">Synthetic</span>
                <span class="scenario-tag">C-SSRS Grounded</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if gen_btn:
        with st.spinner("Generating scenario..."):
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

        col_analyze, col_send, _ = st.columns([1, 1, 1])
        with col_analyze:
            analyze_btn = st.button("Analyze This Scenario", type="primary")
        with col_send:
            if st.button("→ Send to Transcript Analysis"):
                st.session_state["piped_transcript"] = res.get("transcript", "")
                st.markdown('<div class="pipe-banner">Transcript queued — switch to <strong>Transcript Analysis</strong> to run the full pipeline.</div>', unsafe_allow_html=True)

        if analyze_btn:
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
                    st.markdown('<div class="cl-label">SIGNALS DETECTED</div>', unsafe_allow_html=True)
                    for sig in signals:
                        render_signal_card(sig)
                if isinstance(coaching, dict) and coaching.get("priority_feedback"):
                    st.markdown('<div class="cl-label" style="margin-top:16px;">COACHING</div>', unsafe_allow_html=True)
                    for pf in coaching.get("priority_feedback", []):
                        render_coaching_card(pf)
            else:
                st.error(f"Pipeline error: {results.get('error')}")


# ── Comparative Analysis ──────────────────────────────────────────────────────
elif "Comparative" in mode:
    st.markdown('<div class="cl-page-header cl-fadein"><div class="page-title">Comparative Analysis</div><div class="page-subtitle">Run the full pipeline on two volunteers handling the same scenario and get a head-to-head supervisor verdict.</div></div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("""
    <div class="compare-empty">
        <strong>Quick demo:</strong> Load the <em>Hard</em> sample into both fields, edit one volunteer's responses to be more engaged and empathetic, and run the comparison to see how response quality affects scoring across every dimension.
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="compare-header">VOLUNTEER A</div>', unsafe_allow_html=True)
        name_a = st.text_input("Name A", value="Volunteer A", label_visibility="collapsed")
        transcript_a = st.text_area("Transcript A", height=220, placeholder="Paste Volunteer A transcript...", label_visibility="collapsed")
    with col_b:
        st.markdown('<div class="compare-header">VOLUNTEER B</div>', unsafe_allow_html=True)
        name_b = st.text_input("Name B", value="Volunteer B", label_visibility="collapsed")
        transcript_b = st.text_area("Transcript B", height=220, placeholder="Paste Volunteer B transcript...", label_visibility="collapsed")

    if st.button("Run Comparative Analysis", type="primary"):
        if not transcript_a.strip() or not transcript_b.strip():
            st.error("Please provide both transcripts.")
        else:
            with st.spinner("Analyzing both transcripts in parallel..."):
                comp_results = run_comparative(transcript_a, transcript_b, name_a, name_b)

            res_a = comp_results.get("result_a", {})
            res_b = comp_results.get("result_b", {})
            comp = comp_results.get("comparison", {})

            winner = comp.get("winner", "")
            st.markdown(f"""
            <div class="report-card" style="text-align:center; border-top-color:#F5A623;">
                <div class="report-title" style="color:#F5A623;">Supervisor Verdict</div>
                <div style="font-family:'Space Mono',monospace; font-size:2rem; color:#F0F4FF; font-weight:700; margin-bottom:10px;">{winner}</div>
                <div style="color:#8896B3; font-size:0.88rem; line-height:1.6;">{comp.get('winner_reasoning','')}</div>
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
                        <div class="cl-metric-value" style="font-size:1.8rem;">{score}/100</div>
                        <div class="cl-metric-label">Overall Score</div>
                        <div style="margin-top:12px; color:#8896B3; font-size:0.84rem;">MI: {mi}/100 &nbsp;·&nbsp; Signals: {sigs}</div>
                        <div style="margin-top:10px; color:#C8D0E0; font-size:0.85rem; line-height:1.5;">{comp.get(strength_key,'')}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if comp.get("shared_gaps"):
                st.markdown(f'<div class="gap-item" style="margin-top:16px;">⚠ &nbsp; <strong>Shared Gap:</strong> &nbsp; {comp["shared_gaps"]}</div>', unsafe_allow_html=True)
            if comp.get("recommendation"):
                st.markdown(f"""
                <div class="cl-card" style="margin-top:12px; border-left: 3px solid rgba(15,244,198,0.4);">
                    <div class="cl-label">TRAINING RECOMMENDATION</div>
                    <div style="color:#C8D0E0; font-size:0.9rem; line-height:1.65;">{comp["recommendation"]}</div>
                </div>
                """, unsafe_allow_html=True)


# ── Progress Tracker ──────────────────────────────────────────────────────────
elif "Progress" in mode:
    st.markdown('<div class="cl-page-header cl-fadein"><div class="page-title">Progress Tracker</div><div class="page-subtitle">Track a volunteer\'s improvement across sessions and generate a formal supervisor report card.</div></div>', unsafe_allow_html=True)
    st.divider()

    sessions = get_sessions(volunteer_name)

    if not sessions:
        st.markdown(f"""
        <div class="cl-card" style="text-align:center; padding:48px 32px;">
            <div style="font-size:2.2rem; margin-bottom:16px;">📋</div>
            <div style="color:#8896B3; font-size:0.95rem;">No sessions found for <strong style="color:#F0F4FF;">{volunteer_name}</strong>.</div>
            <div style="color:#4A5568; font-size:0.84rem; margin-top:10px;">Submit a transcript in <strong style="color:#C8D0E0;">Transcript Analysis</strong> to start tracking progress.</div>
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
            st.markdown('<div class="cl-label">SCORE TREND</div>', unsafe_allow_html=True)
            st.line_chart(df.set_index("session_number")[["score", "mi_score"]], color=["#0FF4C6", "#F5A623"])

        st.markdown('<div class="cl-label" style="margin-top:20px;">SESSION HISTORY</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="cl-label">SUPERVISOR REPORT CARD</div>', unsafe_allow_html=True)

            if st.button("Generate Report Card", type="primary"):
                _trend = "improving" if sessions[-1]["score"] > sessions[0]["score"] else "variable"
                with st.spinner(f"Analyzing {len(sessions)} sessions for {volunteer_name} · Identifying performance patterns · Writing supervisor assessment..."):
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
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
                            <div class="report-title">Supervisor Report — {volunteer_name}</div>
                            <div style="font-family:'Space Mono',monospace; font-size:2.4rem; color:{grade_color}; font-weight:700; line-height:1;">{grade}</div>
                        </div>
                        <div style="color:#C8D0E0; line-height:1.7; margin-bottom:16px; font-size:0.9rem;">{report.get('narrative','')}</div>
                        <div style="display:inline-block; padding:5px 16px; background:rgba(15,244,198,0.06); border:1px solid rgba(15,244,198,0.18); border-radius:20px; font-size:0.8rem; color:{readiness_color};">
                            {readiness}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_s, col_g = st.columns(2)
                    with col_s:
                        st.markdown('<div class="cl-label">CONSISTENT STRENGTHS</div>', unsafe_allow_html=True)
                        for s in report.get("consistent_strengths", []):
                            st.markdown(f'<div class="strength-item">✓ &nbsp; {s}</div>', unsafe_allow_html=True)
                    with col_g:
                        st.markdown('<div class="cl-label">PERSISTENT GAPS</div>', unsafe_allow_html=True)
                        for g in report.get("persistent_gaps", []):
                            st.markdown(f'<div class="gap-item">⚠ &nbsp; {g}</div>', unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="cl-card" style="margin-top:16px; border-left:3px solid rgba(15,244,198,0.4);">
                        <div class="cl-label">PRIORITY RECOMMENDATION</div>
                        <div style="color:#C8D0E0; font-size:0.9rem; line-height:1.65;">{report.get('priority_recommendation','')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(report.get("error", "Report generation failed."))
