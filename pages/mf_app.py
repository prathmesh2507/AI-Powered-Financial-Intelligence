# ============================================================
# 💰 MF India AI — Personalized Mutual Fund Recommendation Engine
# Guided, multi-step investment questionnaire -> risk profile ->
# goal-based allocation -> fund recommendation -> wealth projection.
#
# Visual language matches the existing MF India AI dashboard
# (dark purple/blue/green glassmorphism, Inter, Plotly dark theme).
# Calculation logic lives in mf_engine.py so the UI never invents
# numbers on its own.
# ============================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import warnings

import mf_engine as eng

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MF India AI | Recommendation Engine",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS — dark purple/blue/green glassmorphism theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#MainMenu, footer { visibility: hidden; }
header { visibility: visible; background: transparent !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1260px; }
.stDeployButton { display: none !important; }

[data-testid="collapsedControl"] { color: #a78bfa !important; }
button[kind="header"] { color: #a78bfa !important; }

.stApp { background: linear-gradient(160deg, #0d0b1e 0%, #111827 100%); }

/* Hero */
.hero-banner {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 20px;
    padding: 2.4rem 3rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -80px; right: -70px;
    width: 330px; height: 330px;
    background: radial-gradient(circle, rgba(99,102,241,0.28) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle { color: rgba(255,255,255,0.65); font-size: 1rem; margin-top: 0.5rem; }

/* Step progress indicator */
.step-track {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 16px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.6rem;
}
.step-item { display:flex; align-items:center; gap:.55rem; flex:1; }
.step-circle {
    width: 30px; height: 30px; min-width:30px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: .82rem;
    border: 1px solid rgba(255,255,255,.18);
    color: rgba(255,255,255,.45);
    background: rgba(255,255,255,.04);
}
.step-circle.done { background: linear-gradient(135deg,#a78bfa,#7c3aed); color:#fff; border-color: transparent; }
.step-circle.active { background: linear-gradient(135deg,#60a5fa,#2563eb); color:#fff; border-color: transparent; box-shadow: 0 0 0 4px rgba(96,165,250,.18); }
.step-label { font-size: .78rem; font-weight: 600; color: rgba(255,255,255,.45); }
.step-label.active { color: #fff; }
.step-line { flex: 0.6; height: 2px; background: rgba(255,255,255,.1); margin: 0 .4rem; }
.step-line.done { background: linear-gradient(90deg,#a78bfa,#60a5fa); }

/* KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.5rem; }
.kpi-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.35rem 1.5rem;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}
.kpi-card::after { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.kpi-card.purple::after { background: linear-gradient(90deg,#a78bfa,#7c3aed); }
.kpi-card.blue::after { background: linear-gradient(90deg,#60a5fa,#2563eb); }
.kpi-card.green::after { background: linear-gradient(90deg,#34d399,#059669); }
.kpi-card.orange::after { background: linear-gradient(90deg,#fb923c,#ea580c); }
.kpi-label { color: rgba(255,255,255,0.5); font-size: 0.72rem; text-transform: uppercase; letter-spacing: .08em; }
.kpi-value { color: #fff; font-size: 1.75rem; font-weight: 900; margin-top: .25rem; }
.kpi-sub { color: rgba(255,255,255,.4); font-size: .75rem; }

/* Cards */
.glass-card {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 16px;
    padding: 1.35rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.profile-card {
    background: linear-gradient(135deg,rgba(99,102,241,.15),rgba(16,185,129,.08));
    border: 1px solid rgba(99,102,241,.28);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.section-header { font-size: 1.25rem; font-weight: 800; color: #e2e8f0; margin: 1.4rem 0 .9rem; }
.section-header span { color:#a78bfa; }
.step-title { font-size: 1.6rem; font-weight: 900; color: #fff; margin-bottom: .2rem; }
.step-help { color: rgba(255,255,255,.5); font-size: .88rem; margin-bottom: 1.2rem; }

/* Goal cards */
.goal-card {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 16px;
    padding: 1.1rem;
    text-align: center;
    height: 100%;
}
.goal-card.selected { border-color: #a78bfa; background: linear-gradient(135deg,rgba(167,139,250,.18),rgba(96,165,250,.08)); }
.goal-emoji { font-size: 1.8rem; }
.goal-name { color: #fff; font-weight: 700; font-size: .9rem; margin-top: .3rem; }

/* Risk */
.risk-score {
    font-size: 3rem; font-weight: 900;
    background: linear-gradient(135deg,#a78bfa,#60a5fa,#34d399);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.risk-pill { display:inline-block; padding:.4rem .9rem; border-radius:50px; font-size:.78rem; font-weight:700; border:1px solid rgba(255,255,255,.15); }

/* Fund cards */
.fund-card {
    background: linear-gradient(135deg,rgba(255,255,255,.055),rgba(255,255,255,.025));
    border:1px solid rgba(255,255,255,.1);
    border-radius:18px;
    padding:1.25rem;
    margin-bottom:1rem;
}
.fund-badge {
    display:inline-block;
    background: rgba(167,139,250,.15);
    color:#c4b5fd;
    border-radius:8px;
    padding:.25rem .6rem;
    font-size:.68rem;
    font-weight:800;
    letter-spacing:.06em;
    text-transform:uppercase;
    margin-bottom:.5rem;
}
.fund-name { color:#fff; font-size:1.1rem; font-weight:800; }
.fund-meta { color:rgba(255,255,255,.45); font-size:.78rem; margin-top:.15rem; }
.score { font-size:1.6rem; font-weight:900; color:#34d399; }
.mini-label { color:rgba(255,255,255,.42); font-size:.68rem; text-transform:uppercase; letter-spacing:.07em; }
.mini-value { color:#fff; font-size:.95rem; font-weight:700; }
.why-list { margin-top: .9rem; padding-top: .8rem; border-top: 1px solid rgba(255,255,255,.08); }
.why-item { color: rgba(255,255,255,.7); font-size: .82rem; margin-bottom: .3rem; }
.why-item span { color: #34d399; margin-right: .4rem; }

/* Allocation */
.alloc-card { background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.08); border-radius:14px; padding:1rem; }
.alloc-title { color:#fff; font-weight:800; }
.alloc-value { color:#a78bfa; font-size:1.4rem; font-weight:900; }

/* Insight / AI box */
.insight-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; }
.insight-card { background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08); border-left:3px solid #a78bfa; border-radius:12px; padding:1rem 1.2rem; }
.insight-title { color:#a78bfa; font-size:.73rem; font-weight:800; text-transform:uppercase; letter-spacing:.07em; }
.insight-text { color:rgba(255,255,255,.72); font-size:.86rem; line-height:1.5; margin-top:.35rem; }
.ai-box {
    background: linear-gradient(135deg, rgba(167,139,250,.12), rgba(52,211,153,.06));
    border: 1px solid rgba(167,139,250,.3);
    border-radius: 18px;
    padding: 1.5rem 1.7rem;
}
.ai-box .ai-label { color:#a78bfa; font-weight:800; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; }
.ai-box p { color: rgba(255,255,255,.8); font-size: .92rem; line-height: 1.7; margin: .6rem 0 0; }

/* Disclaimer */
.disclaimer-box {
    background: rgba(251,146,60,.08);
    border: 1px solid rgba(251,146,60,.3);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    color: rgba(255,255,255,.72);
    font-size: .82rem;
    line-height: 1.6;
}

/* Sidebar */
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0f0c29 0%,#1a1535 100%); border-right:1px solid rgba(255,255,255,.07); }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color:rgba(255,255,255,.75) !important; }

/* Tabs — flat underline nav bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 1.9rem;
    background: transparent;
    border-bottom: 1px solid rgba(255,255,255,.09);
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    border-radius: 0;
    color: rgba(255,255,255,.55);
    font-weight: 600;
    font-size: .93rem;
    padding: .55rem .1rem .8rem;
    margin-bottom: -1px;
}
.stTabs [data-baseweb="tab"]:hover { color: rgba(255,255,255,.85); }
.stTabs [aria-selected="true"] {
    background: transparent;
    color: #fff !important;
    border-bottom: 2.5px solid #fb7185;
}
.stTabs [data-baseweb="tab-highlight"] { background: transparent; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* Portfolio / showcase section */
.skill-badges { display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1rem; }
.skill-badge {
    display:inline-flex; align-items:center; gap:.4rem;
    background: rgba(99,102,241,.12);
    border: 1px solid rgba(99,102,241,.28);
    color:#ddd6fe;
    border-radius:50px;
    padding:.48rem .95rem;
    font-size:.78rem;
    font-weight:700;
    white-space: nowrap;
}
.skill-badge .check { color:#34d399; font-weight:900; }

.tech-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:1rem; margin-top:1rem; }
.tech-card {
    background: rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.1);
    border-radius:14px;
    padding:1.3rem .8rem;
    text-align:center;
}
.tech-icon { font-size:1.6rem; margin-bottom:.5rem; }
.tech-name { color:#fff; font-weight:800; font-size:.83rem; }
.tech-tag { color:rgba(255,255,255,.45); font-size:.68rem; margin-top:.15rem; }

@media (max-width: 900px) {
    .tech-grid { grid-template-columns: repeat(3,1fr); }
}

/* Inputs */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background:rgba(255,255,255,.045) !important; border-color:rgba(255,255,255,.1) !important;
}
.stNumberInput input, .stTextInput input { color:#fff !important; }

.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#a78bfa,#7c3aed) !important;
    border: none !important;
}

/* Responsive */
@media (max-width: 900px) {
    .kpi-grid { grid-template-columns:repeat(2,1fr); }
    .insight-grid { grid-template-columns:1fr; }
}
@media (max-width: 600px) {
    .kpi-grid { grid-template-columns:1fr; }
    .hero-banner { padding:1.5rem; }
    .hero-title { font-size:1.5rem; }
    .step-label { display:none; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0"),
    margin=dict(l=10, r=10, t=45, b=10),
    colorway=["#a78bfa", "#60a5fa", "#34d399", "#fb923c", "#f472b6", "#facc15"],
)


def style_fig(fig, title="", height=380):
    fig.update_layout(**PLOTLY_THEME, title=dict(text=title, font=dict(size=14, color="#e2e8f0")), height=height)
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False)
    return fig


# ─────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data():
    return eng.load_data(eng.DATA_FILE)


try:
    df = get_data()
    DATA_OK = True
except Exception as e:
    df = pd.DataFrame()
    DATA_OK = False
    DATA_ERROR = str(e)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "step": 1,
    "age": 28,
    "goal": "Wealth Creation",
    "target_age": 58,
    "monthly_sip": 10000,
    "lumpsum": 0,
    "has_target_corpus": "No",
    "target_corpus": 5000000,
    "q_loss_reaction": 3,
    "q_priority": 3,
    "q_experience": 3,
    "q_income_stability": 3,
    "q_comfort": 3,
    "q_primary_priority": 3,
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

STEP_LABELS = ["About You", "Goal", "Investment", "Risk", "Horizon", "Results"]
TOTAL_STEPS = len(STEP_LABELS)


def go_to(step):
    st.session_state.step = step


def render_progress():
    current = st.session_state.step
    html = ['<div class="step-track">']
    for i, label in enumerate(STEP_LABELS, start=1):
        state = "done" if i < current else ("active" if i == current else "")
        circle_content = "✓" if i < current else str(i)
        html.append('<div class="step-item">')
        html.append(f'<div class="step-circle {state}">{circle_content}</div>')
        html.append(f'<div class="step-label {"active" if i == current else ""}">{label}</div>')
        html.append('</div>')
        if i < TOTAL_STEPS:
            line_state = "done" if i < current else ""
            html.append(f'<div class="step-line {line_state}"></div>')
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def nav_buttons(back_step=None, next_step=None, next_label="Continue →", next_disabled=False, next_help=""):
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if back_step is not None:
            if st.button("← Back", use_container_width=True):
                go_to(back_step)
                st.rerun()
    with c3:
        if next_step is not None:
            if st.button(next_label, type="primary", use_container_width=True, disabled=next_disabled):
                go_to(next_step)
                st.rerun()
    if next_disabled and next_help:
        st.caption(next_help)


GOAL_OPTIONS = [
    ("🏖️", "Retirement"),
    ("💰", "Wealth Creation"),
    ("🎓", "Child Education"),
    ("🏠", "House Purchase"),
    ("🛡️", "Emergency / Short-Term"),
    ("🎯", "Other Goal"),
]

# ─────────────────────────────────────────────────────────────
# STEP 1 — ABOUT YOU
# ─────────────────────────────────────────────────────────────
def render_step1():
    st.markdown('<div class="step-title">👤 About You</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-help">Your age helps determine your investment horizon and goal '
        'strategy. It is not, on its own, used to set your risk tolerance.</div>',
        unsafe_allow_html=True,
    )

    col, _ = st.columns([1, 2])
    with col:
        st.session_state.age = st.number_input(
            "Current Age", min_value=18, max_value=80, value=int(st.session_state.age), step=1
        )

    st.write("")
    nav_buttons(back_step=None, next_step=2)


# ─────────────────────────────────────────────────────────────
# STEP 2 — INVESTMENT GOAL
# ─────────────────────────────────────────────────────────────
def render_step2():
    st.markdown('<div class="step-title">🎯 Investment Goal</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-help">What are you investing towards? This shapes the strategic '
        'asset mix before we look at your risk tolerance.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(GOAL_OPTIONS))
    for col, (emoji, name) in zip(cols, GOAL_OPTIONS):
        with col:
            selected = st.session_state.goal == name
            st.markdown(
                f"""<div class="goal-card {'selected' if selected else ''}">
                    <div class="goal-emoji">{emoji}</div>
                    <div class="goal-name">{name}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button("Select" if not selected else "Selected ✓", key=f"goal_{name}", use_container_width=True):
                st.session_state.goal = name
                st.rerun()

    st.write("")
    age = int(st.session_state.age)
    col1, col2 = st.columns(2)
    with col1:
        target_age = st.number_input(
            "Target Age (when you'll need this money)",
            min_value=age + 1, max_value=100,
            value=max(int(st.session_state.target_age), age + 1),
            step=1,
        )
        st.session_state.target_age = target_age
    with col2:
        horizon = target_age - age
        st.markdown(f"""
        <div class="kpi-card blue" style="margin-top:1.6rem;">
            <div class="kpi-label">Investment Horizon</div>
            <div class="kpi-value">{horizon} Years</div>
            <div class="kpi-sub">Age {age} → {target_age}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    nav_buttons(back_step=1, next_step=3)


# ─────────────────────────────────────────────────────────────
# STEP 3 — INVESTMENT CAPACITY
# ─────────────────────────────────────────────────────────────
def render_step3():
    st.markdown('<div class="step-title">💵 Investment Capacity</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-help">Tell us how much you can invest. You can change this anytime.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.monthly_sip = st.number_input(
            "Monthly SIP (₹)", min_value=500, max_value=10_000_000,
            value=int(st.session_state.monthly_sip), step=500,
        )
    with col2:
        st.session_state.lumpsum = st.number_input(
            "Initial Lumpsum (₹) — enter 0 if none",
            min_value=0, max_value=100_000_000,
            value=int(st.session_state.lumpsum), step=5000,
        )

    st.write("")
    st.session_state.has_target_corpus = st.radio(
        "Do you have a target corpus in mind?", ["No", "Yes"],
        index=["No", "Yes"].index(st.session_state.has_target_corpus),
        horizontal=True,
    )
    if st.session_state.has_target_corpus == "Yes":
        st.session_state.target_corpus = st.number_input(
            "Target Corpus (₹)", min_value=10000, max_value=1_000_000_000,
            value=int(st.session_state.target_corpus), step=100000,
            help="We'll show how close your plan gets you to this, and suggest an SIP top-up if there's a gap.",
        )

    if st.session_state.monthly_sip <= 0:
        st.warning("Monthly SIP must be greater than ₹0 to generate a recommendation.")

    st.write("")
    nav_buttons(back_step=2, next_step=4, next_disabled=st.session_state.monthly_sip <= 0)


# ─────────────────────────────────────────────────────────────
# STEP 4 — RISK ASSESSMENT
# ─────────────────────────────────────────────────────────────
RISK_QUESTIONS = [
    ("q_loss_reaction", "Your investment falls 20% temporarily. What would you do?",
     ["Sell immediately", "Sell some", "Hold", "Continue investing", "Invest more"]),
    ("q_priority", "What matters more to you?",
     ["Protecting my capital", "Stable growth", "Balanced growth", "Long-term growth", "Maximum long-term growth"]),
    ("q_experience", "How much investment experience do you have?",
     ["None", "Beginner", "Some experience", "Experienced", "Very experienced"]),
    ("q_income_stability", "How stable is your income?",
     ["Very unstable", "Unstable", "Stable", "Very stable", "Highly stable"]),
    ("q_comfort", "How comfortable are you with market fluctuations?",
     ["Not comfortable", "Slightly comfortable", "Moderately comfortable", "Comfortable", "Very comfortable"]),
    ("q_primary_priority", "What is your primary priority?",
     ["Capital preservation", "Low volatility", "Balanced risk and return", "Growth", "Aggressive growth"]),
]


def render_step4():
    st.markdown('<div class="step-title">🧠 Risk Assessment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-help">A few behavioral questions — these say far more about your real '
        'risk tolerance than simply asking "how risky do you want to be?"</div>',
        unsafe_allow_html=True,
    )

    for i, (key, question, options) in enumerate(RISK_QUESTIONS, start=1):
        current_value = int(st.session_state[key])
        chosen = st.radio(
            f"**Q{i}. {question}**",
            options=list(range(1, 6)),
            format_func=lambda v, opts=options: f"{chr(64+v)}. {opts[v-1]}",
            index=current_value - 1,
            key=f"widget_{key}",
        )
        st.session_state[key] = chosen
        st.write("")

    st.write("")
    nav_buttons(back_step=3, next_step=5)


# ─────────────────────────────────────────────────────────────
# STEP 5 — REVIEW / HORIZON CONFIRMATION
# ─────────────────────────────────────────────────────────────
def render_step5():
    st.markdown('<div class="step-title">📅 Review Your Inputs</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-help">Here is everything we will use to build your plan. Go back to '
        'change anything, or continue to see your personalized recommendation.</div>',
        unsafe_allow_html=True,
    )

    age = int(st.session_state.age)
    target_age = int(st.session_state.target_age)
    horizon = max(target_age - age, 1)

    answers = {
        "loss_reaction": st.session_state.q_loss_reaction,
        "priority": st.session_state.q_priority,
        "experience": st.session_state.q_experience,
        "income_stability": st.session_state.q_income_stability,
        "comfort": st.session_state.q_comfort,
        "primary_priority": st.session_state.q_primary_priority,
    }
    risk_score = eng.calculate_investor_risk(answers)
    risk_profile, risk_level = eng.get_risk_profile(risk_score)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card purple"><div class="kpi-label">Age</div>
        <div class="kpi-value">{age}</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card blue"><div class="kpi-label">Goal</div>
        <div class="kpi-value" style="font-size:1.15rem;">{st.session_state.goal}</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card green"><div class="kpi-label">Horizon</div>
        <div class="kpi-value">{horizon} Yrs</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card orange"><div class="kpi-label">Monthly SIP</div>
        <div class="kpi-value">{eng.format_inr(st.session_state.monthly_sip, 0)}</div></div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown(f"""
    <div class="profile-card">
        <div style="color:rgba(255,255,255,.45);font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;">
            Preliminary Risk Read
        </div>
        <div style="display:flex;align-items:baseline;gap:.8rem;">
            <div class="risk-score" style="font-size:2.4rem;">{risk_score:.0f}/100</div>
            <div class="risk-pill">{risk_profile}</div>
        </div>
        <div style="color:rgba(255,255,255,.55);font-size:.85rem;margin-top:.4rem;">
            Based on your questionnaire answers. Full breakdown on the results page.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    nav_buttons(back_step=4, next_step=6, next_label="See My Recommendation →")

# ─────────────────────────────────────────────────────────────
# RISK GAUGE (Plotly)
# ─────────────────────────────────────────────────────────────
def render_risk_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": " / 100", "font": {"size": 34, "color": "#fff"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "rgba(255,255,255,.3)", "tickfont": {"color": "rgba(255,255,255,.5)"}},
            "bar": {"color": "#a78bfa", "thickness": 0.3},
            "bgcolor": "rgba(255,255,255,.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 20], "color": "rgba(52,211,153,.35)"},
                {"range": [20, 40], "color": "rgba(96,165,250,.35)"},
                {"range": [40, 60], "color": "rgba(167,139,250,.35)"},
                {"range": [60, 80], "color": "rgba(251,146,60,.35)"},
                {"range": [80, 100], "color": "rgba(244,114,182,.35)"},
            ],
            "threshold": {
                "line": {"color": "#fff", "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        },
    ))
    theme = {k: v for k, v in PLOTLY_THEME.items() if k != "margin"}
    fig.update_layout(**theme, height=260, margin=dict(l=25, r=25, t=10, b=10))
    return fig


# ─────────────────────────────────────────────────────────────
# STEP 6 — RESULTS
# ─────────────────────────────────────────────────────────────
def render_step6():
    age = int(st.session_state.age)
    target_age = int(st.session_state.target_age)
    goal = st.session_state.goal
    monthly_sip = float(st.session_state.monthly_sip)
    lumpsum = float(st.session_state.lumpsum)
    horizon = max(target_age - age, 1)

    answers = {
        "loss_reaction": st.session_state.q_loss_reaction,
        "priority": st.session_state.q_priority,
        "experience": st.session_state.q_experience,
        "income_stability": st.session_state.q_income_stability,
        "comfort": st.session_state.q_comfort,
        "primary_priority": st.session_state.q_primary_priority,
    }
    risk_score = eng.calculate_investor_risk(answers)
    risk_profile, risk_level = eng.get_risk_profile(risk_score)

    base_allocation = eng.goal_strategy(goal, horizon)
    allocation = eng.adjust_for_risk(base_allocation, risk_level)
    sip_allocation = eng.calculate_sip_allocation(monthly_sip, allocation)

    portfolio = eng.build_portfolio(df, allocation, sip_allocation, risk_level) if DATA_OK else pd.DataFrame()

    # ---------- HERO ----------
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">💰 Your Personalized MF Plan</div>
        <div class="hero-subtitle">Built around your {goal.lower()} goal, a {horizon}-year horizon, and your {risk_profile.lower()} risk profile.</div>
    </div>
    """, unsafe_allow_html=True)

    top_l, top_r = st.columns([5, 1])
    with top_r:
        if st.button("✏️ Edit answers", use_container_width=True):
            go_to(1)
            st.rerun()

    if not DATA_OK:
        st.error(f"Could not load the fund dataset: {DATA_ERROR}")
        return

    # ---------- KPI ROW ----------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card purple"><div class="kpi-label">Risk Score</div>
        <div class="kpi-value">{risk_score:.0f}/100</div><div class="kpi-sub">{risk_profile}</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card blue"><div class="kpi-label">Horizon</div>
        <div class="kpi-value">{horizon} Yrs</div><div class="kpi-sub">Age {age} → {target_age}</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card green"><div class="kpi-label">Monthly SIP</div>
        <div class="kpi-value">{eng.format_inr(monthly_sip, 0)}</div><div class="kpi-sub">Goal: {goal}</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card orange"><div class="kpi-label">Funds Analysed</div>
        <div class="kpi-value">{len(df):,}</div><div class="kpi-sub">Equity · Hybrid · Debt</div></div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Your Plan", "🏆 Recommendations", "📈 Wealth Journey", "🔎 Fund Explorer", "🏆 Portfolio",
    ])

    # ═══════════════ TAB 1 — YOUR PLAN ═══════════════
    with tab1:
        c1, c2 = st.columns([1.1, .9])
        with c1:
            st.markdown('<div class="section-header">🎯 Risk Profile</div>', unsafe_allow_html=True)
            st.plotly_chart(render_risk_gauge(risk_score), use_container_width=True)
            st.markdown(f"""
            <div class="glass-card">
                <div class="risk-pill">{risk_profile}</div>
                <p style="color:rgba(255,255,255,.65);font-size:.85rem;margin-top:.7rem;line-height:1.6;">
                    Your profile suggests you can tolerate
                    {"meaningful" if risk_level >= 4 else "moderate" if risk_level == 3 else "limited"}
                    market fluctuations for potentially
                    {"higher" if risk_level >= 4 else "steady" if risk_level == 3 else "more stable"}
                    long-term outcomes. This is a planning input, not a promise of returns.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">🧩 Recommended Allocation</div>', unsafe_allow_html=True)
            ac1, ac2, ac3 = st.columns(3)
            allocation_cols = [("Equity", ac1, "#a78bfa"), ("Hybrid", ac2, "#60a5fa"), ("Debt", ac3, "#34d399")]
            for asset, col, color in allocation_cols:
                pct = allocation.get(asset, 0)
                amount = sip_allocation.get(asset, 0)
                with col:
                    st.markdown(f"""
                    <div class="alloc-card" style="border-top:3px solid {color};">
                        <div class="alloc-title">{asset}</div>
                        <div class="alloc-value">{pct:.1f}%</div>
                        <div style="color:rgba(255,255,255,.45);font-size:.75rem;">{eng.format_inr(amount, 0)}/month</div>
                    </div>
                    """, unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="section-header">🥧 Portfolio Mix</div>', unsafe_allow_html=True)
            pie = go.Figure(go.Pie(
                labels=list(allocation.keys()), values=list(allocation.values()), hole=.62,
                textinfo="label+percent",
                marker=dict(colors=["#a78bfa", "#60a5fa", "#34d399"], line=dict(color="#111827", width=2)),
            ))
            pie.update_layout(**PLOTLY_THEME, height=300, showlegend=False,
                               annotations=[dict(text="Your<br>Portfolio", showarrow=False, font=dict(size=13, color="#e2e8f0"))])
            st.plotly_chart(pie, use_container_width=True)

            score_breakdown = eng.portfolio_quality_score(portfolio, allocation)
            if score_breakdown:
                st.markdown('<div class="section-header">📊 Portfolio Score</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex;justify-content:space-between;align-items:baseline;">
                        <span class="mini-label">Overall</span>
                        <span class="score">{score_breakdown['Overall']:.0f}/100</span>
                    </div>
                    <hr style="border-color:rgba(255,255,255,.07);">
                    <div style="display:flex;justify-content:space-between;margin-top:.3rem;"><span class="mini-label">Risk Fit</span><span class="mini-value">{score_breakdown['Risk Fit']:.0f}</span></div>
                    <div style="display:flex;justify-content:space-between;margin-top:.4rem;"><span class="mini-label">Diversification</span><span class="mini-value">{score_breakdown['Diversification']:.0f}</span></div>
                    <div style="display:flex;justify-content:space-between;margin-top:.4rem;"><span class="mini-label">Fund Quality</span><span class="mini-value">{score_breakdown['Fund Quality']:.0f}</span></div>
                    <div style="display:flex;justify-content:space-between;margin-top:.4rem;"><span class="mini-label">Cost Efficiency</span><span class="mini-value">{score_breakdown['Cost Efficiency']:.0f}</span></div>
                </div>
                """, unsafe_allow_html=True)

    # ═══════════════ TAB 2 — RECOMMENDATIONS ═══════════════
    with tab2:
        st.markdown('<div class="section-header">🏆 Personalized Portfolio</div>', unsafe_allow_html=True)

        if portfolio.empty:
            st.warning(
                "No complete portfolio could be constructed with the current monthly SIP and risk "
                "constraints — some asset-class buckets may need a higher minimum SIP than what's "
                "currently allocated. Try increasing your monthly SIP in Step 3."
            )
        else:
            badge_map = {"Equity": "🏆 Recommended Equity", "Hybrid": "🏆 Recommended Hybrid", "Debt": "🏆 Recommended Debt"}
            for _, row in portfolio.iterrows():
                why = []
                if row["Risk Match"] >= 70:
                    why.append("Matches your risk profile closely")
                elif row["Risk Match"] >= 40:
                    why.append("Reasonably aligned with your risk profile")
                if row["Fund Quality"] >= 60:
                    why.append("Strong risk-adjusted quality metrics")
                why.append(f"Selected for your {horizon}-year horizon")
                if row["Expense Ratio"] <= df["expense_ratio"].median():
                    why.append("Below-median expense ratio for its category")

                why_html = "".join(f'<div class="why-item"><span>✓</span>{w}</div>' for w in why)

                st.markdown(f"""
                <div class="fund-card">
                    <div class="fund-badge">{badge_map.get(row['Asset Class'], 'Recommended')}</div>
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div class="fund-name">{row['Fund']}</div>
                            <div class="fund-meta">{row['AMC']} · {row['Sub Category']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="mini-label">Portfolio Score</div>
                            <div class="score">{row['Portfolio Score']:.0f}</div>
                        </div>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin-top:1.1rem;">
                        <div><div class="mini-label">Monthly SIP</div><div class="mini-value">{eng.format_inr(row['Monthly SIP'], 0)}</div></div>
                        <div><div class="mini-label">Risk Score</div><div class="mini-value">{row['Risk Score']:.0f}/100</div></div>
                        <div><div class="mini-label">Risk Match</div><div class="mini-value">{row['Risk Match']:.0f}/100</div></div>
                        <div><div class="mini-label">Fund Quality</div><div class="mini-value">{row['Fund Quality']:.0f}/100</div></div>
                        <div><div class="mini-label">3Y Return</div><div class="mini-value">{eng.format_pct(row['3Y Return'], 2)}</div></div>
                        <div><div class="mini-label">Sharpe</div><div class="mini-value">{row['Sharpe']:.2f}</div></div>
                        <div><div class="mini-label">Sortino</div><div class="mini-value">{row['Sortino']:.2f}</div></div>
                        <div><div class="mini-label">Expense Ratio</div><div class="mini-value">{eng.format_pct(row['Expense Ratio'], 2)}</div></div>
                        <div><div class="mini-label">Allocation</div><div class="mini-value">{row['Allocation %']:.1f}%</div></div>
                    </div>
                    <div class="why-list">
                        <div class="mini-label" style="margin-bottom:.4rem;">WHY THIS FUND?</div>
                        {why_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">📋 Portfolio Breakdown</div>', unsafe_allow_html=True)
            display_portfolio = portfolio[[
                "Asset Class", "Allocation %", "Monthly SIP", "Fund", "Risk Level",
                "3Y Return", "Sharpe", "Sortino", "Expense Ratio", "Portfolio Score",
            ]].copy()
            for col in ["3Y Return", "Sharpe", "Sortino", "Expense Ratio", "Portfolio Score"]:
                display_portfolio[col] = display_portfolio[col].round(2)
            st.dataframe(display_portfolio, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-header">🤖 Portfolio Intelligence</div>', unsafe_allow_html=True)
        alloc_summary = " + ".join(f"{v:.0f}% {k}" for k, v in allocation.items() if v > 0)
        st.markdown(f"""
        <div class="ai-box">
            <div class="ai-label">Portfolio Intelligence</div>
            <p>
                Your portfolio is designed around a <b>{horizon}-year {goal.lower()}</b> horizon and a
                <b>{risk_profile.lower()}</b> risk profile. The strategic mix is <b>{alloc_summary}</b>,
                balancing growth potential against the volatility you indicated you're comfortable with.
                Funds within each asset class were screened for risk compatibility first, then ranked
                by risk-adjusted quality, category-relative 3-year returns, Sharpe, Sortino and cost —
                so the portfolio isn't just chasing the highest historical return.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">💡 Why These Funds?</div>', unsafe_allow_html=True)
        reasons = [
            ("Risk compatibility", "Funds are screened against your investor risk level before ranking."),
            ("Risk-adjusted quality", "Fund quality incorporates risk-adjusted performance rather than relying on returns alone."),
            ("Category-relative returns", "3-year returns are ranked within sub-category to avoid misleading cross-category comparisons."),
            ("Cost awareness", "Lower expense ratios receive a positive contribution to the final ranking."),
        ]
        st.markdown('<div class="insight-grid">', unsafe_allow_html=True)
        for title, text in reasons:
            st.markdown(f"""<div class="insight-card"><div class="insight-title">{title}</div><div class="insight-text">{text}</div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════ TAB 3 — WEALTH JOURNEY ═══════════════
    with tab3:
        st.markdown('<div class="section-header">📈 Your Wealth Journey</div>', unsafe_allow_html=True)

        blended_rate = eng.blended_rate_for_allocation(sip_allocation) if sum(sip_allocation.values()) > 0 else 8.0
        scenario_rates = {"Conservative": 8.0, "Expected": round(blended_rate, 2), "Optimistic": 12.0}
        # keep scenarios ordered and sane even if blended rate is unusual
        scenario_rates["Expected"] = min(max(scenario_rates["Expected"], scenario_rates["Conservative"] + 0.5),
                                          scenario_rates["Optimistic"] - 0.5)

        scenarios = {}
        for name, rate in scenario_rates.items():
            scenarios[name] = eng.wealth_projection(monthly_sip, lumpsum, rate, horizon)

        c1, c2, c3 = st.columns(3)
        colors = {"Conservative": "#60a5fa", "Expected": "#34d399", "Optimistic": "#a78bfa"}
        for col, (name, data) in zip([c1, c2, c3], scenarios.items()):
            rate = scenario_rates[name]
            with col:
                st.markdown(f"""
                <div class="glass-card" style="border-top:3px solid {colors[name]};">
                    <div class="mini-label">{name} Scenario</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#fff;margin-top:.3rem;">{eng.format_inr(data['corpus'])}</div>
                    <div style="color:{colors[name]};font-size:.78rem;">Illustrative {rate:.1f}% annual return</div>
                    <hr style="border-color:rgba(255,255,255,.07);">
                    <div style="display:flex;justify-content:space-between;"><span class="mini-label">Invested</span><span class="mini-value">{eng.format_inr(data['invested'])}</span></div>
                    <div style="display:flex;justify-content:space-between;margin-top:.4rem;"><span class="mini-label">Est. Gains</span><span class="mini-value">{eng.format_inr(data['gains'])}</span></div>
                </div>
                """, unsafe_allow_html=True)

        st.caption("Illustrative projection — not a guaranteed return. Mutual fund investments are subject to market risk.")

        projection_df = eng.portfolio_age_projection(age, target_age, sip_allocation, lumpsum, rate_override=None)
        cons_df = eng.portfolio_age_projection(age, target_age, sip_allocation, lumpsum, rate_override=scenario_rates["Conservative"])
        opt_df = eng.portfolio_age_projection(age, target_age, sip_allocation, lumpsum, rate_override=scenario_rates["Optimistic"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=cons_df["Age"], y=cons_df["Corpus"], mode="lines", name="Conservative",
                                  line=dict(color="#60a5fa", width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=projection_df["Age"], y=projection_df["Corpus"], mode="lines", name="Expected",
                                  line=dict(color="#34d399", width=3), fill="tonexty", fillcolor="rgba(52,211,153,.06)"))
        fig.add_trace(go.Scatter(x=opt_df["Age"], y=opt_df["Corpus"], mode="lines", name="Optimistic",
                                  line=dict(color="#a78bfa", width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=projection_df["Age"], y=projection_df["Invested"], mode="lines", name="Amount Invested",
                                  line=dict(color="rgba(255,255,255,.35)", width=2, dash="dash")))
        fig = style_fig(fig, "📈 Age-wise Portfolio Growth (Conservative / Expected / Optimistic)", 460)
        fig.update_yaxes(tickprefix="₹")
        st.plotly_chart(fig, use_container_width=True)

        # ---------- GOAL METER ----------
        if st.session_state.has_target_corpus == "Yes":
            target_corpus = float(st.session_state.target_corpus)
            st.markdown('<div class="section-header">🎯 Goal Progress</div>', unsafe_allow_html=True)

            projected = scenarios["Expected"]["corpus"]
            coverage = (projected / target_corpus * 100) if target_corpus > 0 else 0
            gap = target_corpus - projected

            gauge_col, info_col = st.columns([1, 1.3])
            with gauge_col:
                goal_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=min(coverage, 150),
                    number={"suffix": "%", "font": {"size": 30, "color": "#fff"}},
                    gauge={
                        "axis": {"range": [0, 150], "tickcolor": "rgba(255,255,255,.3)"},
                        "bar": {"color": "#34d399" if coverage >= 100 else "#fb923c"},
                        "bgcolor": "rgba(255,255,255,.03)",
                        "steps": [
                            {"range": [0, 60], "color": "rgba(251,146,60,.3)"},
                            {"range": [60, 100], "color": "rgba(167,139,250,.3)"},
                            {"range": [100, 150], "color": "rgba(52,211,153,.3)"},
                        ],
                    },
                ))
                goal_theme = {k: v for k, v in PLOTLY_THEME.items() if k != "margin"}
                goal_fig.update_layout(**goal_theme, height=220, margin=dict(l=20, r=20, t=10, b=10))
                st.plotly_chart(goal_fig, use_container_width=True)

            with info_col:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex;justify-content:space-between;"><span class="mini-label">Target Corpus</span><span class="mini-value">{eng.format_inr(target_corpus)}</span></div>
                    <div style="display:flex;justify-content:space-between;margin-top:.5rem;"><span class="mini-label">Projected Corpus (Expected)</span><span class="mini-value">{eng.format_inr(projected)}</span></div>
                    <div style="display:flex;justify-content:space-between;margin-top:.5rem;">
                        <span class="mini-label">{"Potential Surplus" if gap < 0 else "Shortfall"}</span>
                        <span class="mini-value" style="color:{'#34d399' if gap < 0 else '#fb923c'};">{eng.format_inr(abs(gap))}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if gap > 0:
                    needed_sip_total = eng.required_sip_for_target(target_corpus, lumpsum, allocation, horizon, annual_return=None)
                    if not np.isnan(needed_sip_total) and needed_sip_total > monthly_sip:
                        additional = needed_sip_total - monthly_sip
                        st.markdown(f"""
                        <div class="glass-card" style="border-left:3px solid #facc15;margin-top:.8rem;">
                            <div class="mini-label">💡 SIP OPTIMIZER</div>
                            <div style="display:flex;justify-content:space-between;margin-top:.5rem;"><span class="mini-label">Current SIP</span><span class="mini-value">{eng.format_inr(monthly_sip, 0)}</span></div>
                            <div style="display:flex;justify-content:space-between;margin-top:.4rem;"><span class="mini-label">Estimated SIP Needed</span><span class="mini-value">{eng.format_inr(needed_sip_total, 0)}</span></div>
                            <div style="display:flex;justify-content:space-between;margin-top:.4rem;"><span class="mini-label">Additional SIP</span><span class="mini-value" style="color:#facc15;">{eng.format_inr(additional, 0)}/month</span></div>
                            <div style="color:rgba(255,255,255,.45);font-size:.72rem;margin-top:.5rem;">Based on the Expected-scenario return assumption for your current allocation mix.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("The target corpus may be very large relative to your horizon — even a substantially higher SIP may not close the gap under these assumptions.")
        else:
            st.caption("Tip: set a target corpus in Step 3 to see a goal-progress meter and SIP optimizer here.")

        st.markdown('<div class="section-header">📅 Age-by-Age Wealth Table</div>', unsafe_allow_html=True)
        table_df = projection_df.copy()
        table_df["Invested"] = table_df["Invested"].map(eng.format_inr)
        table_df["Corpus"] = table_df["Corpus"].map(eng.format_inr)
        table_df["Gains"] = table_df["Gains"].map(eng.format_inr)
        st.dataframe(table_df[["Age", "Years", "Invested", "Corpus", "Gains"]], use_container_width=True, hide_index=True, height=320)

    # ═══════════════ TAB 4 — FUND EXPLORER ═══════════════
    with tab4:
        st.markdown('<div class="section-header">🔎 Explore the Fund Universe</div>', unsafe_allow_html=True)
        e1, e2, e3 = st.columns(3)
        with e1:
            selected_asset = st.selectbox("Asset Class", ["All", "Equity", "Hybrid", "Debt", "Other"])
        with e2:
            selected_category = st.selectbox("Category", ["All"] + sorted(df["sub_category"].dropna().unique().tolist()))
        with e3:
            max_sip = st.number_input("Maximum Monthly SIP (₹)", min_value=500, value=int(monthly_sip), step=500)

        explorer = df.copy()
        if selected_asset != "All":
            explorer = explorer[explorer["asset_class"] == selected_asset]
        if selected_category != "All":
            explorer = explorer[explorer["sub_category"] == selected_category]
        explorer = explorer[explorer["min_sip"].fillna(np.inf) <= max_sip]
        explorer = explorer.sort_values("fund_quality_score", ascending=False)

        cols = ["scheme_name", "amc_name", "category", "sub_category", "min_sip", "risk_score",
                "calculated_risk_level", "returns_3yr", "sharpe", "sortino", "expense_ratio", "fund_quality_score"]
        cols = [c for c in cols if c in explorer.columns]
        st.dataframe(explorer[cols].head(100), use_container_width=True, hide_index=True, height=480)
        st.caption(f"Showing {min(len(explorer), 100):,} of {len(explorer):,} matching funds.")

    # ═══════════════ TAB 5 — PORTFOLIO ═══════════════
    with tab5:
        st.markdown('<div class="section-header">🏆 What This Dashboard Demonstrates</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="color:rgba(255,255,255,.65);font-size:.92rem;max-width:900px;">'
            'This recommendation engine showcases a professional-grade personal-finance analytics '
            'platform built with Python, Streamlit, and Plotly — reflecting skills across quantitative '
            'finance, data engineering, and full-stack app development.</div>',
            unsafe_allow_html=True,
        )

        skills = [
            "Data Cleaning & Wrangling", "Exploratory Data Analysis", "Business Intelligence",
            "Data Visualization", "Statistical Analysis", "Financial Analytics",
            "Streamlit Development", "Plotly Visualization", "Risk Profiling Engine",
            "Goal-Based Allocation", "Portfolio Construction", "Wealth Projection Modeling",
            "KPI Dashboard Design", "Responsive UI/UX", "Glassmorphism Design",
            "Multi-Step Wizard UX", "Session State Management", "Production Code Quality",
        ]
        badges_html = "".join(
            f'<div class="skill-badge"><span class="check">✔</span>{s}</div>' for s in skills
        )
        st.markdown(f'<div class="skill-badges">{badges_html}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🛠️ Technology Stack</div>', unsafe_allow_html=True)
        tech = [
            ("🐍", "Python 3", "Core Language"),
            ("📊", "Streamlit", "Web App Framework"),
            ("📈", "Plotly", "Interactive Charting"),
            ("🐼", "Pandas", "Data Manipulation"),
            ("🔢", "NumPy", "Numerical Computing"),
            ("🎨", "CSS3", "Custom Styling"),
        ]
        tech_html = "".join(
            f'<div class="tech-card"><div class="tech-icon">{icon}</div>'
            f'<div class="tech-name">{name}</div><div class="tech-tag">{tag}</div></div>'
            for icon, name, tag in tech
        )
        st.markdown(f'<div class="tech-grid">{tech_html}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">📊 Dataset Scope</div>', unsafe_allow_html=True)
        n_funds = len(df) if DATA_OK else 0
        n_amcs = df["amc_name"].nunique() if DATA_OK and "amc_name" in df.columns else 0
        n_categories = df["sub_category"].nunique() if DATA_OK and "sub_category" in df.columns else 0
        n_metrics = 8  # std dev, beta, sharpe, sortino, 3Y returns, expense ratio, fund quality score, risk score
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f"""<div class="kpi-card purple"><div class="kpi-label">Total Funds</div>
            <div class="kpi-value">{n_funds:,}</div><div class="kpi-sub">Across all AMCs</div></div>""", unsafe_allow_html=True)
        with d2:
            st.markdown(f"""<div class="kpi-card blue"><div class="kpi-label">AMCs Covered</div>
            <div class="kpi-value">{n_amcs:,}</div><div class="kpi-sub">Fund houses</div></div>""", unsafe_allow_html=True)
        with d3:
            st.markdown(f"""<div class="kpi-card green"><div class="kpi-label">Fund Categories</div>
            <div class="kpi-value">{n_categories:,}</div><div class="kpi-sub">Sub-categories tracked</div></div>""", unsafe_allow_html=True)
        with d4:
            st.markdown(f"""<div class="kpi-card orange"><div class="kpi-label">Metrics / Fund</div>
            <div class="kpi-value">{n_metrics}</div><div class="kpi-sub">Risk & performance stats</div></div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">🔬 How Your Recommendation Is Generated</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:800;color:#fff;">Quantitative Recommendation Engine</div>
            <div class="insight-text" style="margin-top:.7rem;">
                Your Inputs → Risk Assessment → Risk Score → Goal + Horizon → Asset Allocation
                → Fund Filtering → Risk Compatibility → Fund Quality → Portfolio Ranking.
                This is a rule-based, quantitative pipeline — not a machine-learning model.
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="glass-card">
                <div style="font-weight:800;color:#fff;">Risk Engine Weights</div><br>
                <div class="insight-text">
                    Loss reaction — 25%<br>What matters more — 20%<br>Investment experience — 15%<br>
                    Income stability — 15%<br>Comfort with fluctuations — 15%<br>Primary priority — 10%
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="glass-card">
                <div style="font-weight:800;color:#fff;">Fund Ranking Weights</div><br>
                <div class="insight-text">
                    Risk compatibility — 35%<br>Fund quality — 25%<br>3Y category-relative return — 15%<br>
                    Sharpe — 10%<br>Sortino — 10%<br>Expense ratio — 5%
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:800;color:#fff;">Metrics used by the engine</div>
            <div class="insight-text" style="margin-top:.6rem;">
                Standard Deviation · Beta · Sharpe · Sortino · 3Y Returns · Expense Ratio ·
                Fund Quality Score · Risk Score
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:800;color:#fff;">⚠️ Current model limitations</div>
            <div class="insight-text" style="margin-top:.6rem;">
                This version uses a point-in-time fund snapshot. It does not incorporate historical
                NAV time series, maximum drawdown, rolling volatility, VaR, benchmark tracking error,
                tax effects, exit loads, or live market conditions. The output is a quantitative
                research prototype and should not be treated as individualized financial advice.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------- DISCLAIMER ----------
    st.markdown('<div class="section-header">⚠️ Disclaimer</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="disclaimer-box">
        These recommendations are generated using historical fund metrics, user-provided preferences
        and illustrative assumptions. They are not guaranteed returns or personalized financial advice.
        Mutual fund investments are subject to market risks. Past performance does not guarantee
        future results. Please consult a registered investment advisor before making investment decisions.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 .6rem;">
        <div style="font-size:2rem;">💰</div>
        <div style="font-size:1.05rem;font-weight:800;color:#fff;">MF India AI</div>
        <div style="font-size:.73rem;color:rgba(255,255,255,.4);">Personalized Investment Engine</div>
    </div>
    <hr style="border-color:rgba(255,255,255,.08);">
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Navigation")
    nav_items = [
        (1, "🧑 About You"), (2, "🎯 Goal Planner"), (3, "💵 Investment Capacity"),
        (4, "🧠 Risk Assessment"), (5, "📅 Review"), (6, "📊 Recommendation"),
    ]
    current_step = st.session_state.step
    for step_num, label in nav_items:
        prefix = "▶ " if step_num == current_step else ""
        disabled = step_num > current_step
        if st.button(f"{prefix}{label}", key=f"nav_{step_num}", use_container_width=True, disabled=disabled):
            go_to(step_num)
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        for key in DEFAULTS:
            st.session_state[key] = DEFAULTS[key]
        st.rerun()

    st.markdown("---")
    st.caption("Planning tool only. Projections are illustrative and do not guarantee future returns.")

# ─────────────────────────────────────────────────────────────
# MAIN ROUTING
# ─────────────────────────────────────────────────────────────
render_progress()

step = st.session_state.step
if step == 1:
    render_step1()
elif step == 2:
    render_step2()
elif step == 3:
    render_step3()
elif step == 4:
    render_step4()
elif step == 5:
    render_step5()
else:
    render_step6()

st.markdown("""
<div style="text-align:center;padding:1.8rem;color:rgba(255,255,255,.25);
font-size:.75rem;border-top:1px solid rgba(255,255,255,.06);margin-top:1rem;">
    💰 MF India AI &nbsp;|&nbsp; Personalized Mutual Fund Intelligence
    &nbsp;|&nbsp; Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)