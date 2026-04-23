def load_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #F0F4FF;
}

body {
    background: radial-gradient(ellipse at 50% 30%, #0C1422 0%, #070C18 65%) !important;
    background-attachment: fixed !important;
}

/* Noise texture overlay */
body::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");
    opacity: 0.03;
    pointer-events: none;
    z-index: 9999;
}

.stApp {
    background: transparent !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
header { visibility: hidden; }

/* ── Top padding ─────────────────────────────────────────────────── */
[data-testid="stMainBlockContainer"] {
    padding-top: 1rem !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #070C18 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

[data-testid="stSidebar"] > div {
    padding-top: 24px;
}

/* ── Kill tab checkmarks — all selectors ─────────────────────────── */
[data-baseweb="tab"][aria-selected="true"] svg { display: none !important; }
[data-testid="stTab"] svg { display: none !important; }
button[role="tab"] svg { display: none !important; }
[data-baseweb="tab"] svg { display: none !important; }
.stTabs svg { display: none !important; }
[data-baseweb="tab-list"] svg { display: none !important; }

/* ── Tabs — pill segmented control ──────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13, 21, 40, 0.9);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    gap: 2px;
}

.stTabs [data-baseweb="tab"] {
    color: #8896B3;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    border-radius: 7px;
    padding: 7px 16px;
    border: none;
    background: transparent;
    transition: all 0.15s;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #C8D0E0;
    background: rgba(255, 255, 255, 0.04);
}

.stTabs [aria-selected="true"] {
    background: rgba(30, 45, 78, 0.9) !important;
    color: #F0F4FF !important;
    font-weight: 500 !important;
}

/* hide the tab underline indicator */
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* ── Radio — hide dots, style as text links ──────────────────────── */
[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
    display: none;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 2px;
    display: flex;
    flex-direction: column;
}

[data-testid="stSidebar"] .stRadio label {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: 8px;
    transition: background 0.15s, color 0.15s;
    cursor: pointer;
    margin: 0;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(15, 244, 198, 0.06);
}

[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    position: absolute !important;
}

/* Hide the radio button circle proxy div */
[data-testid="stSidebar"] .stRadio label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] .stRadio label span {
    color: #8896B3;
    font-size: 0.88rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 400;
}

/* Selected radio item */
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(15, 244, 198, 0.07);
}

[data-testid="stSidebar"] .stRadio label:has(input:checked) span {
    color: #0FF4C6 !important;
    font-weight: 500;
}

/* ── Divider ─────────────────────────────────────────────────────── */
hr {
    border-color: rgba(255, 255, 255, 0.06) !important;
    margin: 16px 0 !important;
}

/* ── Buttons ─────────────────────────────────────────────────────── */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #0FF4C6 0%, #00C9A7 100%) !important;
    color: #070C18 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.02em !important;
    box-shadow: none !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(15, 244, 198, 0.3) !important;
}

/* Default / secondary buttons */
.stButton > button:not([kind="primary"]),
.stButton > button[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: #8896B3 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.85rem !important;
    padding: 7px 16px !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
}

.stButton > button:not([kind="primary"]):hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    border-color: rgba(255, 255, 255, 0.22) !important;
    color: #C8D0E0 !important;
    transform: none !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background: transparent !important;
    color: #8896B3 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    padding: 6px 14px !important;
    transition: all 0.15s !important;
}

[data-testid="stDownloadButton"] button:hover {
    border-color: rgba(255, 255, 255, 0.22) !important;
    color: #C8D0E0 !important;
}

/* Danger button wrapper */
.danger-btn > div > button,
.danger-btn button {
    background: transparent !important;
    border: 1px solid rgba(255, 75, 110, 0.35) !important;
    color: #FF4B6E !important;
    font-size: 0.78rem !important;
    padding: 5px 14px !important;
    box-shadow: none !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    transform: none !important;
}

.danger-btn > div > button:hover,
.danger-btn button:hover {
    background: rgba(255, 75, 110, 0.08) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Inputs & Textareas ───────────────────────────────────────────── */
.stTextArea textarea, .stTextInput input {
    background: rgba(13, 21, 40, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #F0F4FF !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.65 !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(15, 244, 198, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(15, 244, 198, 0.08) !important;
}

/* ── Selectbox ───────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: rgba(13, 21, 40, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #F0F4FF !important;
}

.stSelectbox [data-baseweb="select"] > div {
    background: rgba(13, 21, 40, 0.8) !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
}

/* ── Slider ──────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
    background: #0FF4C6 !important;
    border-color: #0FF4C6 !important;
}

[data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: #0FF4C6;
}

/* ── Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }

/* ── Dataframe ───────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] th {
    background: rgba(13, 21, 40, 0.9) !important;
    color: #4A5568 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stDataFrame"] td {
    color: #F0F4FF !important;
    font-size: 0.88rem !important;
}

/* ── Expander ────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(13, 21, 40, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 10px !important;
}

[data-testid="stExpander"] summary {
    color: #8896B3 !important;
    font-size: 0.88rem !important;
}

/* ── Alerts ──────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(13, 21, 40, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #8896B3 !important;
}

/* ── Chart ───────────────────────────────────────────────────────── */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: transparent !important;
}

/* ── Animations ──────────────────────────────────────────────────── */
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

@keyframes fadein {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* ── Page Header ─────────────────────────────────────────────────── */
.cl-page-header {
    padding: 4px 0 16px 0;
}

.page-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #F0F4FF;
    line-height: 1.2;
    margin-bottom: 6px;
}

.page-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 300;
    color: #8896B3;
    line-height: 1.5;
    max-width: 640px;
}

/* ── Section Label ───────────────────────────────────────────────── */
.cl-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.68rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #4A5568;
    margin-bottom: 14px;
    margin-top: 8px;
}

/* Legacy section header — grey not teal */
.cl-section-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #4A5568;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* ── Cards ───────────────────────────────────────────────────────── */
.cl-card {
    background: rgba(13, 21, 40, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
    transition: border-color 0.2s, box-shadow 0.2s;
}

.cl-card:hover {
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 0 20px rgba(15, 244, 198, 0.04);
}

.cl-card-accent {
    border-left: 3px solid rgba(15, 244, 198, 0.6);
}

/* ── Metrics ─────────────────────────────────────────────────────── */
.cl-metric {
    background: rgba(13, 21, 40, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
}

.cl-metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: #0FF4C6;
    line-height: 1;
    margin-bottom: 6px;
}

.cl-metric-label {
    font-family: 'DM Sans', sans-serif;
    color: #8896B3;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Fade-in animation ───────────────────────────────────────────── */
.cl-fadein {
    animation: fadein 0.35s ease forwards;
}

/* ── Confidence Badges ───────────────────────────────────────────── */
.badge-high {
    display: inline-block;
    background: rgba(255, 75, 110, 0.12);
    color: #FF4B6E;
    border: 1px solid rgba(255, 75, 110, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.badge-medium {
    display: inline-block;
    background: rgba(245, 166, 35, 0.12);
    color: #F5A623;
    border: 1px solid rgba(245, 166, 35, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.badge-low {
    display: inline-block;
    background: rgba(136, 150, 179, 0.12);
    color: #8896B3;
    border: 1px solid rgba(136, 150, 179, 0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* ── Signal Cards ────────────────────────────────────────────────── */
.signal-card {
    background: rgba(13, 21, 40, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}

.signal-card-high  { border-left: 3px solid #FF4B6E; }
.signal-card-medium { border-left: 3px solid #F5A623; }
.signal-card-low   { border-left: 3px solid #8896B3; }

.signal-exchange {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #4A5568;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.signal-quote {
    font-style: italic;
    color: #C8D0E0;
    font-size: 0.9rem;
    margin-bottom: 10px;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 6px;
    border-left: 2px solid rgba(255, 255, 255, 0.08);
    line-height: 1.5;
}

.signal-meta {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #4A5568;
    margin-bottom: 6px;
}

.signal-reasoning {
    color: #8896B3;
    font-size: 0.84rem;
    line-height: 1.55;
}

/* ── Pipeline Progress Steps ─────────────────────────────────────── */
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 16px;
    border-radius: 8px;
    margin-bottom: 6px;
    background: rgba(13, 21, 40, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.88rem;
    color: #8896B3;
    font-family: 'DM Sans', sans-serif;
}

.pipeline-step-active {
    border-color: rgba(15, 244, 198, 0.4) !important;
    color: #0FF4C6 !important;
    background: rgba(15, 244, 198, 0.04) !important;
}

.pipeline-step-done {
    color: #4A5568;
}

.pipeline-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #0FF4C6;
    animation: pulse 1s infinite;
    flex-shrink: 0;
}

/* ── Coaching Cards ──────────────────────────────────────────────── */
.coaching-card {
    background: rgba(13, 21, 40, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 3px solid #FF4B6E;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
}

.coaching-issue {
    color: #FF4B6E;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
    font-family: 'DM Sans', sans-serif;
}

.coaching-exchange {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #4A5568;
    margin-bottom: 12px;
}

.coaching-quote {
    font-style: italic;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 6px;
    font-size: 0.88rem;
    margin-bottom: 8px;
    color: #C8D0E0;
    line-height: 1.5;
    border-left: 2px solid rgba(255, 255, 255, 0.08);
}

.coaching-label {
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4A5568;
    margin-bottom: 4px;
    font-family: 'DM Sans', sans-serif;
}

.coaching-better {
    color: #0FF4C6;
    font-size: 0.88rem;
    padding: 10px 14px;
    background: rgba(15, 244, 198, 0.04);
    border-radius: 8px;
    border: 1px solid rgba(15, 244, 198, 0.12);
    line-height: 1.55;
}

/* ── Strength / Gap / Critical ───────────────────────────────────── */
.strength-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(15, 244, 198, 0.04);
    border: 1px solid rgba(15, 244, 198, 0.12);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.87rem;
    color: #C8D0E0;
    line-height: 1.5;
}

.gap-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(245, 166, 35, 0.04);
    border: 1px solid rgba(245, 166, 35, 0.12);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.87rem;
    color: #C8D0E0;
    line-height: 1.5;
}

.critical-item {
    display: flex;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(255, 75, 110, 0.04);
    border: 1px solid rgba(255, 75, 110, 0.15);
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 0.87rem;
    color: #C8D0E0;
    line-height: 1.5;
}

/* ── Timeline ────────────────────────────────────────────────────── */
.timeline-container {
    position: relative;
    padding-left: 28px;
}

.timeline-line {
    position: absolute;
    left: 9px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, rgba(15, 244, 198, 0.4), transparent);
}

.timeline-item {
    position: relative;
    margin-bottom: 16px;
}

.timeline-dot {
    position: absolute;
    left: -23px;
    top: 8px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.timeline-dot-high   { background: #FF4B6E; box-shadow: 0 0 8px rgba(255,75,110,0.5); }
.timeline-dot-medium { background: #F5A623; box-shadow: 0 0 8px rgba(245,166,35,0.4); }
.timeline-dot-low    { background: #4A5568; }

/* ── Recall Score ────────────────────────────────────────────────── */
.recall-score-big {
    font-family: 'Space Mono', monospace;
    font-size: 4.2rem;
    font-weight: 700;
    line-height: 1;
    margin: 8px 0;
}

.recall-good { color: #0FF4C6; }
.recall-mid  { color: #F5A623; }
.recall-bad  { color: #FF4B6E; }

/* ── Compare ─────────────────────────────────────────────────────── */
.compare-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* ── Report Card ─────────────────────────────────────────────────── */
.report-card {
    background: rgba(13, 21, 40, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-top: 3px solid #0FF4C6;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
}

.report-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #0FF4C6;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Pipe Banner ─────────────────────────────────────────────────── */
.pipe-banner {
    background: rgba(15, 244, 198, 0.05);
    border: 1px solid rgba(15, 244, 198, 0.2);
    border-radius: 8px;
    padding: 12px 18px;
    color: #0FF4C6;
    font-size: 0.86rem;
    margin-bottom: 16px;
    line-height: 1.5;
}

/* ── Word Count ──────────────────────────────────────────────────── */
.word-count-ok   { color: #0FF4C6; font-size: 0.8rem; margin-top: 6px; }
.word-count-warn { color: #F5A623; font-size: 0.8rem; margin-top: 6px; }
.word-count-error { color: #FF4B6E; font-size: 0.8rem; margin-top: 6px; }

/* ── Hero ────────────────────────────────────────────────────────── */
.hero-wordmark {
    font-family: 'Space Mono', monospace;
    font-size: 3.2rem;
    font-weight: 700;
    color: #0FF4C6;
    line-height: 1;
    margin-bottom: 12px;
}

.cursor-blink {
    animation: blink 1.1s ease-in-out infinite;
    color: #0FF4C6;
}

.hero-mission {
    color: #8896B3;
    font-size: 1rem;
    font-weight: 300;
    margin-bottom: 32px;
    font-family: 'DM Sans', sans-serif;
}

.hero-stat {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 244, 198, 0.05);
    border: 1px solid rgba(15, 244, 198, 0.15);
    border-radius: 24px;
    padding: 8px 20px;
    font-size: 0.85rem;
    margin: 4px;
}

.hero-stat-num {
    font-family: 'Space Mono', monospace;
    color: #0FF4C6;
    font-weight: 700;
}

.hero-stat-label {
    color: #8896B3;
}

/* ── Stats bar (legacy) ──────────────────────────────────────────── */
.stats-bar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 48px;
}

.stats-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 244, 198, 0.05);
    border: 1px solid rgba(15, 244, 198, 0.15);
    border-radius: 24px;
    padding: 8px 18px;
    font-size: 0.85rem;
}

.stats-pill-num {
    font-family: 'Space Mono', monospace;
    color: #0FF4C6;
    font-weight: 700;
}

.stats-pill-label {
    color: #8896B3;
}

/* ── Pipeline flow (overview) ────────────────────────────────────── */
.pipeline-flow {
    display: flex;
    align-items: stretch;
    gap: 0;
    margin: 20px 0 40px 0;
    flex-wrap: wrap;
}

.pipeline-flow-step {
    flex: 1;
    min-width: 150px;
    background: rgba(13, 21, 40, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 3px solid rgba(15, 244, 198, 0.4);
    border-radius: 10px;
    padding: 18px 16px;
    margin: 4px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.pipeline-flow-step:hover {
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 0 20px rgba(15, 244, 198, 0.04);
}

.pipeline-flow-num {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    color: #0FF4C6;
    font-weight: 700;
    margin-bottom: 6px;
}

.pipeline-flow-title {
    font-weight: 500;
    color: #F0F4FF;
    font-size: 0.9rem;
    margin-bottom: 4px;
    font-family: 'DM Sans', sans-serif;
}

.pipeline-flow-desc {
    color: #8896B3;
    font-size: 0.78rem;
    line-height: 1.45;
    font-family: 'DM Sans', sans-serif;
}

.pipeline-flow-arrow {
    display: flex;
    align-items: center;
    color: rgba(255, 255, 255, 0.15);
    font-size: 1.2rem;
    padding: 0 2px;
    align-self: center;
}

/* ── Feature grid (overview modes) ──────────────────────────────── */
.feature-card {
    background: rgba(13, 21, 40, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 20px 18px;
    margin-bottom: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
    cursor: default;
}

.feature-card:hover {
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 0 20px rgba(15, 244, 198, 0.04);
}

.feature-card-icon {
    font-size: 1.3rem;
    margin-bottom: 10px;
}

.feature-card-title {
    font-weight: 500;
    color: #F0F4FF;
    font-size: 0.88rem;
    margin-bottom: 5px;
    font-family: 'DM Sans', sans-serif;
}

.feature-card-desc {
    color: #8896B3;
    font-size: 0.8rem;
    line-height: 1.5;
    font-family: 'DM Sans', sans-serif;
}

.feature-card-arrow {
    color: rgba(255, 255, 255, 0.2);
    font-size: 0.8rem;
    margin-top: 8px;
}

/* ── Attribution ─────────────────────────────────────────────────── */
.attribution-line {
    color: #4A5568;
    font-size: 0.75rem;
    text-align: center;
    margin-top: 32px;
    line-height: 1.7;
    padding: 12px 0;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    font-family: 'DM Sans', sans-serif;
}

/* ── Framework items (sidebar) ───────────────────────────────────── */
.framework-item {
    padding: 8px 10px;
    background: rgba(13, 21, 40, 0.5);
    border-radius: 7px;
    margin-bottom: 6px;
    border: 1px solid rgba(255, 255, 255, 0.04);
}

.framework-item-title {
    font-weight: 500;
    font-size: 0.82rem;
    color: #C8D0E0;
    margin-bottom: 2px;
    font-family: 'DM Sans', sans-serif;
}

.framework-item-desc {
    font-size: 0.75rem;
    color: #4A5568;
    line-height: 1.4;
    font-family: 'DM Sans', sans-serif;
}

/* ── Scenario Tags ───────────────────────────────────────────────── */
.scenario-tag {
    display: inline-block;
    background: rgba(15, 244, 198, 0.07);
    color: #0FF4C6;
    border: 1px solid rgba(15, 244, 198, 0.18);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.74rem;
    font-family: 'Space Mono', monospace;
    margin: 3px 2px;
}

/* ── Compare empty state ─────────────────────────────────────────── */
.compare-empty {
    background: rgba(13, 21, 40, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 20px 24px;
    color: #8896B3;
    font-size: 0.87rem;
    line-height: 1.7;
    margin-bottom: 20px;
    font-family: 'DM Sans', sans-serif;
}

.compare-empty strong {
    color: #C8D0E0;
}

.compare-empty em {
    color: #0FF4C6;
    font-style: normal;
}

/* ── Session count badge ─────────────────────────────────────────── */
.session-count {
    font-size: 0.75rem;
    color: #8896B3;
    padding: 4px 0;
    font-family: 'DM Sans', sans-serif;
}

.session-count strong {
    font-family: 'Space Mono', monospace;
    color: #0FF4C6;
    font-size: 0.78rem;
}

/* ── Onboarding steps ────────────────────────────────────────────── */
.onboard-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 16px 20px;
    background: rgba(13, 21, 40, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    margin-bottom: 10px;
}

.onboard-num {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    color: #0FF4C6;
    font-weight: 700;
    min-width: 28px;
}

.onboard-step-title {
    font-weight: 500;
    color: #F0F4FF;
    margin-bottom: 3px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
}

.onboard-step-desc {
    color: #8896B3;
    font-size: 0.84rem;
    line-height: 1.5;
    font-family: 'DM Sans', sans-serif;
}
</style>
"""
