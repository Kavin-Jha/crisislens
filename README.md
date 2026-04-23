# CrisisLens

An AI-powered coaching assistant for mental health crisis hotline volunteer training.

## What It Does

CrisisLens analyzes simulated crisis call transcripts through a four-step agentic pipeline:

1. **Risk Signal Detection** — flags language mapping to Columbia Suicide Severity Rating Scale (C-SSRS) criteria
2. **Confidence Scoring** — rates certainty on every flagged signal with clinical reasoning
3. **MI Response Scoring** — evaluates volunteer responses against Motivational Interviewing principles
4. **Coaching Feedback** — generates exchange-level coaching notes with recommended responses

**Red-Team Mode** generates adversarial transcripts with buried risk signals and measures recall rate — the primary evaluation metric.

**Progress Tracker** shows a volunteer's improvement across multiple sessions.

## Setup

```bash
git clone https://github.com/Kavin-Jha/crisislens.git
cd crisislens
pip install -r requirements.txt
# Add your OpenAI API key to .env:
# OPENAI_API_KEY=your_key_here
streamlit run app.py
```

## Clinical Frameworks

- [Columbia Suicide Severity Rating Scale (C-SSRS)](https://cssrs.columbia.edu)
- [SAMHSA Motivational Interviewing Guidelines](https://www.samhsa.gov)

## Data & Privacy

All transcripts are synthetic. No real caller data is used at any point. Session data exists only in memory during a local run and is never persisted externally.

## Tech Stack

- Python 3.10+
- Streamlit
- OpenAI GPT-4o
- No vector database, no fine-tuning, no external deployment required

## Evaluation

Primary metric: **Recall rate on adversarial transcripts** — what percentage of deliberately buried C-SSRS signals does the system catch? Use Red-Team Mode to run this evaluation.
