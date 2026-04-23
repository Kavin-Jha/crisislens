def load_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0A0F1E;
    color: #E8EDF5;
}

.stApp {
    background-color: #0A0F1E;
}

/* ── Hide default streamlit elements ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
header {visibility: hidden;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0D1428;
    border-right: 1px solid #2A3350;
}

[data-testid="stSidebar"] .stRadio label {
    color: #8896B3;
    font-size: 0.9rem;
    padding: 8px 0;
    transition: color 0.2s;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: #0FF4C6;
}

/* ── Cards ── */
.cl-card {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(15, 244, 198, 0.04);
    transition: border-color 0.2s;
}

.cl-card:hover {
    border-color: #3A4570;
}

.cl-card-accent {
    border-left: 3px solid #0FF4C6;
}

/* ── Metric Cards ── */
.cl-metric {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}

.cl-metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #0FF4C6;
    line-height: 1;
    margin-bottom: 6px;
}

.cl-metric-label {
    color: #8896B3;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Confidence Badges ── */
.badge-high {
    display: inline-block;
    background: rgba(255, 75, 110, 0.15);
    color: #FF4B6E;
    border: 1px solid rgba(255, 75, 110, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.badge-medium {
    display: inline-block;
    background: rgba(245, 166, 35, 0.15);
    color: #F5A623;
    border: 1px solid rgba(245, 166, 35, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.badge-low {
    display: inline-block;
    background: rgba(136, 150, 179, 0.15);
    color: #8896B3;
    border: 1px solid rgba(136, 150, 179, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* ── Signal Cards ── */
.signal-card {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
}

.signal-card-high { border-left: 3px solid #FF4B6E; }
.signal-card-medium { border-left: 3px solid #F5A623; }
.signal-card-low { border-left: 3px solid #8896B3; }

.signal-exchange {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #8896B3;
    margin-bottom: 6px;
}

.signal-quote {
    font-style: italic;
    color: #E8EDF5;
    font-size: 0.95rem;
    margin-bottom: 10px;
    padding: 8px 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
}

.signal-reasoning {
    color: #8896B3;
    font-size: 0.85rem;
    line-height: 1.5;
}

/* ── Pipeline Steps ── */
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    background: #1A2035;
    border: 1px solid #2A3350;
    font-size: 0.9rem;
}

.pipeline-step-active {
    border-color: #0FF4C6;
    color: #0FF4C6;
}

.pipeline-step-done {
    border-color: #2A3350;
    color: #8896B3;
}

.pipeline-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #0FF4C6;
    animation: pulse 1s infinite;
    flex-shrink: 0;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* ── Coaching Cards ── */
.coaching-card {
    background: #1A2035;
    border: 1px solid #2A3350;
    border-left: 3px solid #FF4B6E;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 14px;
}

.coaching-issue {
    color: #FF4B6E;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}

.coaching-exchange {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #8896B3;
    margin-bottom: 12px;
}

.coaching-quote {
    font-style: italic;
    padding: 8px 12px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.coaching-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #8896B3;
    margin-bottom: 4px;
}

.coaching-better {
    color: #0FF4C6;
    font-size: 0.9rem;
    padding: 8px 12px;
    background: rgba(15, 244, 198, 0.05);
    border-radius: 6px;
    border: 1px solid rgba(15, 244, 198, 0.15);
}

/* ── Section Headers ── */
.cl-section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #0FF4C6;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2A3350;
}

/* ── Recall Gauge ── */
.recall-score-big {
    font-family: 'Space Mono', monospace;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
}

.recall-good { color: #0FF4C6; }
.recall-mid { color: #F5A623; }
.recall-bad { color: #FF4B6E; }

/* ── Strength / Gap / Critical items ── */
.strength-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(15, 244, 198, 0.05);
    border: 1px solid rgba(15, 244, 198, 0.15);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #C8D0E0;
}

.gap-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(245, 166, 35, 0.05);
    border: 1px solid rgba(245, 166, 35, 0.15);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #C8D0E0;
}

.critical-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(255, 75, 110, 0.05);
    border: 1px solid rgba(255, 75, 110, 0.15);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #C8D0E0;
}

/* ── Timeline ── */
.timeline-container {
    position: relative;
    padding-left: 24px;
}

.timeline-line {
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, #0FF4C6, transparent);
}

.timeline-item {
    position: relative;
    margin-bottom: 16px;
}

.timeline-dot {
    position: absolute;
    left: -20px;
    top: 6px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.timeline-dot-high { background: #FF4B6E; box-shadow: 0 0 8px rgba(255,75,110,0.5); }
.timeline-dot-medium { background: #F5A623; box-shadow: 0 0 8px rgba(245,166,35,0.5); }
.timeline-dot-low { background: #8896B3; }

/* ── Comparison ── */
.compare-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #0FF4C6;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #2A3350;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0FF4C6 0%, #00C9A7 100%);
    color: #0A0F1E;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 10px 24px;
    transition: all 0.2s;
    letter-spacing: 0.02em;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(15, 244, 198, 0.3);
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #1A2035 !important;
    border: 1px solid #2A3350 !important;
    border-radius: 8px !important;
    color: #E8EDF5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #0FF4C6 !important;
    box-shadow: 0 0 0 2px rgba(15, 244, 198, 0.1) !important;
}

.stSelectbox > div > div {
    background: #1A2035 !important;
    border: 1px solid #2A3350 !important;
    border-radius: 8px !important;
    color: #E8EDF5 !important;
}

hr {
    border-color: #2A3350 !important;
    margin: 24px 0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1A2035;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #2A3350;
}

.stTabs [data-baseweb="tab"] {
    color: #8896B3;
    font-family: 'DM Sans', sans-serif;
}

.stTabs [aria-selected="true"] {
    background: #2A3350;
    color: #0FF4C6 !important;
    border-radius: 6px;
}

/* ── Onboarding ── */
.onboard-container {
    max-width: 680px;
    margin: 40px auto 32px auto;
    text-align: center;
}

.onboard-title {
    font-family: 'Space Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    color: #0FF4C6;
    margin-bottom: 8px;
}

.onboard-sub {
    color: #8896B3;
    font-size: 1.05rem;
    margin-bottom: 40px;
    font-weight: 300;
}

.onboard-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px 20px;
    background: #1A2035;
    border: 1px solid #2A3350;
    border-radius: 10px;
    margin-bottom: 12px;
    text-align: left;
}

.onboard-num {
    font-family: 'Space Mono', monospace;
    font-size: 1.2rem;
    color: #0FF4C6;
    font-weight: 700;
    min-width: 32px;
}

.onboard-step-title {
    font-weight: 600;
    color: #E8EDF5;
    margin-bottom: 4px;
}

.onboard-step-desc {
    color: #8896B3;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* ── Report card ── */
.report-card {
    background: linear-gradient(135deg, #1A2035 0%, #141929 100%);
    border: 1px solid #2A3350;
    border-top: 3px solid #0FF4C6;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
}

.report-title {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    color: #0FF4C6;
    margin-bottom: 16px;
}

/* ── Framework reference ── */
.framework-item {
    padding: 10px 14px;
    background: #141929;
    border-radius: 8px;
    margin-bottom: 8px;
    border: 1px solid #2A3350;
}

.framework-item-title {
    font-weight: 600;
    font-size: 0.85rem;
    color: #E8EDF5;
    margin-bottom: 4px;
}

.framework-item-desc {
    font-size: 0.8rem;
    color: #8896B3;
    line-height: 1.4;
}

/* ── Scenario tags ── */
.scenario-tag {
    display: inline-block;
    background: rgba(15, 244, 198, 0.1);
    color: #0FF4C6;
    border: 1px solid rgba(15, 244, 198, 0.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-family: 'Space Mono', monospace;
    margin: 4px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A0F1E; }
::-webkit-scrollbar-thumb { background: #2A3350; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3A4570; }
</style>
"""
