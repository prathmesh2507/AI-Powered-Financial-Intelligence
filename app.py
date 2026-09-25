# ============================================================
# ◈ FinSight AI — Investment Intelligence Platform
# Unified Streamlit app combining:
#   • Landing Page      (formerly dashboard_app.py)
#   • Stock Intelligence (formerly stock_app.py)
#   • MF Recommendation Engine (formerly mf_app.py)
#
# Navigation between the three sections is done via the
# ?page= query parameter (home / stock / mf), so each
# section keeps its own st.set_page_config metadata and
# its own CSS, exactly as in the original standalone files.
# ============================================================

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import mf_engine as eng

# ── ROUTING ──────────────────────────────────────────────────
# The whole script reruns on every interaction/navigation, so we
# read the "page" query param first and use it to pick the right
# st.set_page_config(...) (must be the first Streamlit command)
# before rendering that page's body.
_params = st.query_params
_page = _params.get("page", "home")
if _page not in ("home", "stock", "mf"):
    _page = "home"

_PAGE_CONFIG = {
    "home": dict(
        page_title="FinSight AI | Investment Intelligence Platform",
        page_icon="◈", layout="wide", initial_sidebar_state="collapsed",
    ),
    "stock": dict(
        page_title="Stock Intelligence",
        page_icon="📈", layout="wide", initial_sidebar_state="expanded",
    ),
    "mf": dict(
        page_title="MF India AI | Recommendation Engine",
        page_icon="💰", layout="wide", initial_sidebar_state="expanded",
    ),
}
st.set_page_config(**_PAGE_CONFIG[_page])


def render_home_page():
    # ── ROUTING CONSTANTS (internal query-param links) ─────────────
    STOCK_APP_URL = "?page=stock"
    MF_APP_URL = "?page=mf"

    # ── GLOBAL CSS ───────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }
    .stDeployButton { display: none !important; }
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    [data-testid="stSidebar"] { display: none; }

    * { box-sizing: border-box; }

    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(167,139,250,0.16), transparent 42%),
            radial-gradient(circle at 88% 15%, rgba(52,211,153,0.13), transparent 40%),
            radial-gradient(circle at 50% 85%, rgba(96,165,250,0.14), transparent 45%),
            linear-gradient(180deg, #070812 0%, #0B1020 45%, #111827 100%);
        background-attachment: fixed;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: rgba(167,139,250,0.35); border-radius: 8px; }

    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; }
    }

    /* ── Shared containers ── */
    .fs-wrap { max-width: 1180px; margin: 0 auto; padding: 0 1.5rem; }
    .fs-eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.72rem;
        font-weight: 700;
        color: #A78BFA;
        text-align: center;
        margin-bottom: 0.6rem;
    }

    /* ── Nav ── */
    .fs-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.4rem 1.5rem 1.2rem 1.5rem;
        max-width: 1180px;
        margin: 0 auto;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .fs-brand { display: flex; flex-direction: column; line-height: 1.1; }
    .fs-brand-name {
        font-size: 1.25rem;
        font-weight: 800;
        color: #F3F4F6;
        letter-spacing: -0.01em;
    }
    .fs-brand-name span { color: #A78BFA; }
    .fs-brand-sub { font-size: 0.68rem; color: #6B7280; letter-spacing: 0.04em; margin-top: 2px; }
    .fs-navlinks { display: flex; gap: 2rem; font-size: 0.86rem; color: #9CA3AF; font-weight: 500; }
    .fs-navlinks a { color: #9CA3AF; text-decoration: none; transition: color 0.15s ease; }
    .fs-navlinks a:hover { color: #E5E7EB; }
    @media (max-width: 720px) { .fs-navlinks { display: none; } }

    /* ── Hero ── */
    .fs-hero { text-align: center; padding: 4.2rem 1.5rem 2.2rem 1.5rem; }
    .fs-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(167,139,250,0.09);
        border: 1px solid rgba(167,139,250,0.28);
        color: #C4B5FD;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-bottom: 1.6rem;
    }
    .fs-hero h1 {
        font-size: clamp(2.4rem, 6vw, 4.2rem);
        font-weight: 900;
        line-height: 1.08;
        letter-spacing: -0.02em;
        color: #F9FAFB;
        margin: 0 0 1.3rem 0;
    }
    .fs-hero h1 .grad {
        background: linear-gradient(90deg, #A78BFA, #60A5FA 55%, #34D399);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .fs-hero p.sub {
        max-width: 640px;
        margin: 0 auto;
        color: #9CA3AF;
        font-size: 1.05rem;
        line-height: 1.65;
        font-weight: 400;
    }
    .fs-trustline {
        margin-top: 2.1rem;
        color: #6B7280;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.01em;
    }

    /* ── Section heading ── */
    .fs-section { padding: 3.4rem 1.5rem; max-width: 1180px; margin: 0 auto; }
    .fs-section-head { text-align: center; margin-bottom: 2.6rem; }
    .fs-section-head h2 {
        font-size: clamp(1.6rem, 3.4vw, 2.2rem);
        font-weight: 800;
        color: #F3F4F6;
        letter-spacing: -0.01em;
        margin: 0.3rem 0 0 0;
    }

    /* ── Path cards ── */
    .fs-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; }
    @media (max-width: 860px) { .fs-cards { grid-template-columns: 1fr; } }

    .fs-card {
        position: relative;
        border-radius: 22px;
        padding: 2.3rem 2.1rem;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, background 0.25s ease;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .fs-card.purple { background: linear-gradient(160deg, rgba(167,139,250,0.10), rgba(255,255,255,0.03)); }
    .fs-card.green { background: linear-gradient(160deg, rgba(52,211,153,0.10), rgba(34,211,238,0.05)); }

    .fs-card:hover {
        transform: translateY(-6px);
        border-color: rgba(255,255,255,0.18);
    }
    .fs-card.purple:hover { box-shadow: 0 20px 60px rgba(124,58,237,0.28); background: linear-gradient(160deg, rgba(167,139,250,0.16), rgba(255,255,255,0.04)); }
    .fs-card.green:hover { box-shadow: 0 20px 60px rgba(16,185,129,0.24); background: linear-gradient(160deg, rgba(52,211,153,0.16), rgba(34,211,238,0.08)); }

    .fs-card-icon { font-size: 2.1rem; margin-bottom: 1rem; transition: filter 0.25s ease; }
    .fs-card:hover .fs-card-icon { filter: drop-shadow(0 0 10px rgba(167,139,250,0.6)); }

    .fs-card-label {
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.7rem;
        font-weight: 700;
        margin-bottom: 0.7rem;
    }
    .fs-card.purple .fs-card-label { color: #A78BFA; }
    .fs-card.green .fs-card-label { color: #34D399; }

    .fs-card h3 { font-size: 1.5rem; font-weight: 800; color: #F9FAFB; margin: 0 0 0.7rem 0; }
    .fs-card p.desc { color: #9CA3AF; font-size: 0.92rem; line-height: 1.6; margin: 0 0 1.3rem 0; }

    .fs-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.7rem; }
    .fs-chip {
        font-size: 0.76rem;
        font-weight: 600;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        color: #D1D5DB;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.09);
    }

    .fs-cta {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 0.85rem 1.4rem;
        border-radius: 12px;
        width: 100%;
        justify-content: center;
        transition: transform 0.2s ease, gap 0.2s ease, box-shadow 0.2s ease;
        margin-top: auto;
    }
    .fs-cta .arrow { transition: transform 0.2s ease; display: inline-block; }
    .fs-cta:hover .arrow { transform: translateX(4px); }
    .fs-card.purple .fs-cta { background: linear-gradient(90deg, #A78BFA, #60A5FA); color: #0B1020 !important; }
    .fs-card.green .fs-cta { background: linear-gradient(90deg, #34D399, #22D3EE); color: #0B1020 !important; }
    .fs-card.purple .fs-cta:hover { box-shadow: 0 10px 30px rgba(167,139,250,0.4); }
    .fs-card.green .fs-cta:hover { box-shadow: 0 10px 30px rgba(52,211,153,0.35); }

    .fs-card-foot { font-size: 0.78rem; color: #6B7280; margin-top: 0.9rem; text-align: center; }

    /* ── How it works ── */
    .fs-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.4rem; }
    @media (max-width: 780px) { .fs-steps { grid-template-columns: 1fr; } }
    .fs-step {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1.7rem 1.5rem;
    }
    .fs-step .num {
        font-size: 0.8rem;
        font-weight: 800;
        color: #A78BFA;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
    }
    .fs-step h4 { color: #F3F4F6; font-size: 1.05rem; font-weight: 700; margin: 0 0 0.5rem 0; }
    .fs-step p { color: #9CA3AF; font-size: 0.87rem; line-height: 1.55; margin: 0; }

    /* ── Feature grid ── */
    .fs-feat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; }
    @media (max-width: 860px) { .fs-feat-grid { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 560px) { .fs-feat-grid { grid-template-columns: 1fr; } }
    .fs-feat {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .fs-feat:hover { border-color: rgba(167,139,250,0.3); transform: translateY(-3px); }
    .fs-feat .ic { font-size: 1.4rem; margin-bottom: 0.55rem; }
    .fs-feat h5 { color: #F3F4F6; font-size: 0.98rem; font-weight: 700; margin: 0 0 0.4rem 0; }
    .fs-feat p { color: #9CA3AF; font-size: 0.84rem; line-height: 1.5; margin: 0; }

    /* ── Comparison table ── */
    .fs-compare {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        overflow: hidden;
    }
    .fs-compare table { width: 100%; border-collapse: collapse; }
    .fs-compare th {
        text-align: left;
        padding: 1rem 1.4rem;
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 700;
    }
    .fs-compare th:first-child { color: #A78BFA; background: rgba(167,139,250,0.08); }
    .fs-compare th:last-child { color: #34D399; background: rgba(52,211,153,0.08); }
    .fs-compare td {
        padding: 0.85rem 1.4rem;
        font-size: 0.88rem;
        color: #D1D5DB;
        border-top: 1px solid rgba(255,255,255,0.06);
    }
    .fs-compare-foot {
        text-align: center;
        color: #6B7280;
        font-size: 0.85rem;
        margin-top: 1.2rem;
        font-style: italic;
    }

    /* ── Stats ── */
    .fs-stats-group { margin-bottom: 1.6rem; }
    .fs-stats-label { text-align: center; color: #6B7280; font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 700; margin-bottom: 1rem; }
    .fs-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; }
    @media (max-width: 720px) { .fs-stats { grid-template-columns: 1fr 1fr; } }
    .fs-stat { text-align: center; padding: 1.2rem 0.6rem; }
    .fs-stat .n { font-size: 1.9rem; font-weight: 900; color: #F9FAFB; }
    .fs-stat .l { font-size: 0.8rem; color: #9CA3AF; margin-top: 0.2rem; }

    /* ── CTA banner ── */
    .fs-ctaband {
        text-align: center;
        border-radius: 26px;
        padding: 3.2rem 2rem;
        background: linear-gradient(135deg, rgba(167,139,250,0.14), rgba(96,165,250,0.10), rgba(52,211,153,0.12));
        border: 1px solid rgba(255,255,255,0.09);
    }
    .fs-ctaband h2 { font-size: clamp(1.6rem, 3.6vw, 2.4rem); font-weight: 900; color: #F9FAFB; margin: 0 0 0.7rem 0; }
    .fs-ctaband p { color: #9CA3AF; font-size: 0.98rem; margin: 0 0 1.8rem 0; }
    .fs-ctaband-btns { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
    .fs-btn {
        text-decoration: none !important;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 0.85rem 1.6rem;
        border-radius: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .fs-btn.solid { background: linear-gradient(90deg, #A78BFA, #34D399); color: #0B1020 !important; }
    .fs-btn.outline { border: 1px solid rgba(255,255,255,0.22); color: #F3F4F6 !important; background: rgba(255,255,255,0.03); }
    .fs-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(167,139,250,0.28); }

    /* ── Disclaimer ── */
    .fs-disclaimer {
        max-width: 820px;
        margin: 2.4rem auto 0 auto;
        text-align: center;
        color: #6B7280;
        font-size: 0.76rem;
        line-height: 1.6;
        padding: 0 1.5rem;
    }

    /* ── About / System Portfolio ── */
    .fs-about-lead { color: #9CA3AF; font-size: 0.94rem; line-height: 1.7; max-width: 760px; margin: 0 auto 2.2rem auto; text-align: center; }
    .fs-skill-badges { display: flex; flex-wrap: wrap; gap: 0.6rem; justify-content: center; margin-bottom: 2.6rem; }
    .fs-skill-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09);
        border-radius: 999px; padding: 0.45rem 0.95rem; font-size: 0.78rem;
        color: #D1D5DB; font-weight: 500;
    }
    .fs-skill-badge .check { color: #34D399; }
    .fs-tech-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; margin-bottom: 2.6rem; }
    @media (max-width: 860px) { .fs-tech-grid { grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 560px) { .fs-tech-grid { grid-template-columns: 1fr 1fr; } }
    .fs-tech-card {
        text-align: center; padding: 1.1rem 0.6rem; border-radius: 14px;
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    }
    .fs-tech-card .icon { font-size: 1.4rem; }
    .fs-tech-card .name { color: #F3F4F6; font-weight: 700; font-size: 0.84rem; margin-top: 0.3rem; }
    .fs-tech-card .tag { color: #6B7280; font-size: 0.72rem; margin-top: 0.1rem; }
    .fs-about-groups { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; }
    @media (max-width: 860px) { .fs-about-groups { grid-template-columns: 1fr; } }

    /* ── Footer ── */
    .fs-footer {
        border-top: 1px solid rgba(255,255,255,0.06);
        padding: 2.4rem 1.5rem 2.6rem 1.5rem;
        text-align: center;
        margin-top: 2.5rem;
    }
    .fs-footer .fbrand { font-size: 1.05rem; font-weight: 800; color: #F3F4F6; }
    .fs-footer .fbrand span { color: #A78BFA; }
    .fs-footer .fsub { color: #6B7280; font-size: 0.82rem; margin-top: 0.4rem; }
    .fs-footer .fmeta { color: #4B5563; font-size: 0.75rem; margin-top: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)


    # ── SECTION FUNCTIONS ────────────────────────────────────────
    def render_hero():
        st.markdown("""
        <div class="fs-hero">
            <div class="fs-badge">✦ AI-POWERED FINANCIAL INTELLIGENCE</div>
            <h1>Make Better<br><span class="grad">Financial Decisions.</span></h1>
            <p class="sub">Explore global markets manually or let intelligent recommendations
            build a personalized investment path for you.</p>
            <div class="fs-trustline">📊 Market Analytics &nbsp;•&nbsp; 🤖 Personalized Intelligence &nbsp;•&nbsp; 📈 Data-Driven Insights</div>
        </div>
        """, unsafe_allow_html=True)


    def render_path_cards():
        st.markdown(f"""
        <div class="fs-section" style="padding-top: 0.5rem;">
            <div class="fs-cards">
                <div class="fs-card purple">
                    <div class="fs-card-icon">📈</div>
                    <div class="fs-card-label">Manual Mode</div>
                    <h3>Explore the Markets</h3>
                    <p class="desc">Analyze stocks, countries and market trends yourself with
                    interactive financial intelligence.</p>
                    <div class="fs-chips">
                        <span class="fs-chip">300+ Stocks</span>
                        <span class="fs-chip">20 Countries</span>
                        <span class="fs-chip">Interactive Charts</span>
                        <span class="fs-chip">Market Analytics</span>
                    </div>
                    <a class="fs-cta" href="{STOCK_APP_URL}" target="_self">
                        Explore Stock Intelligence <span class="arrow">→</span>
                    </a>
                    <div class="fs-card-foot">For investors who want to analyze the market themselves.</div>
                </div>
                <div class="fs-card green">
                    <div class="fs-card-icon">🤖</div>
                    <div class="fs-card-label">Automation Mode</div>
                    <h3>Get a Personalized Investment Path</h3>
                    <p class="desc">Answer a few questions about your goals, horizon and risk
                    tolerance to receive a personalized mutual fund strategy.</p>
                    <div class="fs-chips">
                        <span class="fs-chip">Risk Profiling</span>
                        <span class="fs-chip">Goal-Based Planning</span>
                        <span class="fs-chip">Fund Recommendations</span>
                        <span class="fs-chip">Wealth Projection</span>
                    </div>
                    <a class="fs-cta" href="{MF_APP_URL}" target="_self">
                        Start AI Recommendation <span class="arrow">→</span>
                    </a>
                    <div class="fs-card-foot">For users who want guidance instead of manually analyzing markets.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    def render_how_it_works():
        st.markdown("""
        <div class="fs-section">
            <div class="fs-section-head">
                <div class="fs-eyebrow">How It Works</div>
                <h2>One Platform. Two Intelligent Paths.</h2>
            </div>
            <div class="fs-steps">
                <div class="fs-step">
                    <div class="num">01 — CHOOSE</div>
                    <h4>Choose Your Path</h4>
                    <p>Decide whether you want to explore markets manually or receive a
                    personalized investment plan.</p>
                </div>
                <div class="fs-step">
                    <div class="num">02 — ANALYZE</div>
                    <h4>Explore or Personalize</h4>
                    <p>Manual: explore stocks, markets, countries, trends and analytics.
                    Automation: share your goals, investment capacity and risk preferences.</p>
                </div>
                <div class="fs-step">
                    <div class="num">03 — DECIDE</div>
                    <h4>Make Data-Driven Decisions</h4>
                    <p>Use insights and analytics to better understand your investment choices.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    def render_features():
        st.markdown("""
        <div class="fs-section">
            <div class="fs-section-head">
                <div class="fs-eyebrow">Platform Capabilities</div>
                <h2>Built for Modern Investors</h2>
            </div>
            <div class="fs-feat-grid">
                <div class="fs-feat"><div class="ic">📊</div><h5>Market Intelligence</h5><p>Explore global stock markets with interactive analytics.</p></div>
                <div class="fs-feat"><div class="ic">🌍</div><h5>Global Coverage</h5><p>Analyze stocks across multiple countries and markets.</p></div>
                <div class="fs-feat"><div class="ic">🧠</div><h5>Risk Intelligence</h5><p>Understand your investment risk profile through structured behavioral questions.</p></div>
                <div class="fs-feat"><div class="ic">🎯</div><h5>Goal-Based Planning</h5><p>Align your investment strategy with your financial goals.</p></div>
                <div class="fs-feat"><div class="ic">🤖</div><h5>Personalized Recommendations</h5><p>Generate recommendations based on your inputs, risk profile and investment horizon.</p></div>
                <div class="fs-feat"><div class="ic">📈</div><h5>Wealth Projection</h5><p>Visualize potential long-term investment outcomes.</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    def render_comparison():
        st.markdown("""
        <div class="fs-section">
            <div class="fs-section-head">
                <div class="fs-eyebrow">Compare</div>
                <h2>Which Journey Fits You?</h2>
            </div>
            <div class="fs-compare">
                <table>
                    <tr><th>Manual Mode</th><th>Automation Mode</th></tr>
                    <tr><td>Explore stocks</td><td>Personalized recommendations</td></tr>
                    <tr><td>Analyze markets</td><td>Risk assessment</td></tr>
                    <tr><td>Interactive charts</td><td>Goal-based planning</td></tr>
                    <tr><td>Country analytics</td><td>Fund recommendations</td></tr>
                    <tr><td>Market insights</td><td>Wealth projection</td></tr>
                    <tr><td>Self-directed analysis</td><td>Guided investment journey</td></tr>
                </table>
            </div>
            <div class="fs-compare-foot">Different journeys. One financial intelligence platform.</div>
        </div>
        """, unsafe_allow_html=True)


    def render_stats():
        st.markdown("""
        <div class="fs-section">
            <div class="fs-stats-group">
                <div class="fs-stats-label">Manual Mode — Stock Intelligence</div>
                <div class="fs-stats">
                    <div class="fs-stat"><div class="n">300+</div><div class="l">Stocks</div></div>
                    <div class="fs-stat"><div class="n">20</div><div class="l">Countries</div></div>
                    <div class="fs-stat"><div class="n">OHLCV</div><div class="l">Market Data</div></div>
                    <div class="fs-stat"><div class="n">Interactive</div><div class="l">Analytics</div></div>
                </div>
            </div>
            <div class="fs-stats-group">
                <div class="fs-stats-label">Automation Mode — MF Intelligence</div>
                <div class="fs-stats">
                    <div class="fs-stat"><div class="n">6-Step</div><div class="l">Investor Journey</div></div>
                    <div class="fs-stat"><div class="n">Risk</div><div class="l">Profiling</div></div>
                    <div class="fs-stat"><div class="n">Goal-Based</div><div class="l">Planning</div></div>
                    <div class="fs-stat"><div class="n">Fund</div><div class="l">Recommendations</div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    def render_cta_band():
        st.markdown(f"""
        <div class="fs-section">
            <div class="fs-ctaband">
                <h2>Your Financial Journey Starts Here.</h2>
                <p>Explore the market. Understand the data. Build a smarter investment path.</p>
                <div class="fs-ctaband-btns">
                    <a class="fs-btn solid" href="{STOCK_APP_URL}" target="_self">Explore Markets</a>
                    <a class="fs-btn outline" href="{MF_APP_URL}" target="_self">Get Personalized Guidance</a>
                </div>
            </div>
            <div class="fs-disclaimer">
                Educational &amp; informational platform only. Market data, projections and
                recommendations are intended for informational purposes and should not be
                considered personal financial advice or a guarantee of future returns.
            </div>
        </div>
        """, unsafe_allow_html=True)


    def render_about_section():
        skills = [
            "Data Cleaning & Wrangling", "Exploratory Data Analysis", "Business Intelligence",
            "Data Visualization", "Statistical Analysis", "Financial Analytics",
            "Streamlit Development", "Plotly Visualization", "Time-Series Analysis",
            "Risk Profiling Engine", "Goal-Based Allocation", "Portfolio Construction",
            "Wealth Projection Modeling", "KPI Dashboard Design", "Responsive UI/UX",
            "Glassmorphism Design", "Session State Management", "Production Code Quality",
        ]
        skill_html = "".join(f'<div class="fs-skill-badge"><span class="check">✔</span>{s}</div>' for s in skills)

        tech = [
            ("🐍", "Python 3", "Core Language"),
            ("📊", "Streamlit", "Web App Framework"),
            ("📈", "Plotly", "Interactive Charting"),
            ("🐼", "Pandas", "Data Manipulation"),
            ("🔢", "NumPy", "Numerical Computing"),
            ("🎨", "CSS3", "Custom Styling"),
        ]
        tech_html = "".join(
            f'<div class="fs-tech-card"><div class="icon">{icon}</div>'
            f'<div class="name">{name}</div><div class="tag">{tag}</div></div>'
            for icon, name, tag in tech
        )

        st.markdown(f"""
        <div class="fs-section" id="fs-about">
            <div class="fs-section-head">
                <div class="fs-eyebrow">About</div>
                <h2>One System. Two Engines.</h2>
            </div>
            <p class="fs-about-lead">
                FinSight AI is a single financial intelligence system spanning manual market
                exploration and automated fund recommendations — built end-to-end with Python,
                Streamlit and Plotly, reflecting skills across data engineering, quantitative
                finance and full-stack analytics.
            </p>
            <div class="fs-skill-badges">{skill_html}</div>
            <div class="fs-section-head" style="margin-bottom: 1.4rem;">
                <div class="fs-eyebrow">Technology Stack</div>
            </div>
            <div class="fs-tech-grid">{tech_html}</div>
            <div class="fs-about-groups">
                <div class="fs-card">
                    <div class="fs-card-label">MANUAL MODE</div>
                    <h3 style="font-size:1.15rem;">Stock Intelligence</h3>
                    <p class="desc">300+ global stocks across 20 countries, with OHLCV market
                    data, country analytics and interactive market-overview insights.</p>
                </div>
                <div class="fs-card">
                    <div class="fs-card-label">AUTOMATION MODE</div>
                    <h3 style="font-size:1.15rem;">MF Recommendation Engine</h3>
                    <p class="desc">A rule-based quantitative pipeline — risk assessment, goal-based
                    allocation, fund filtering and ranking — across a full mutual fund universe.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    def render_footer():
        st.markdown("""
        <div class="fs-footer">
            <div class="fbrand">◈ FinSight <span>AI</span></div>
            <div class="fsub">Financial Intelligence Platform</div>
            <div class="fsub">Market Analytics • Personalized Intelligence • Data-Driven Insights</div>
            <div class="fmeta">Built with Streamlit + Python + Plotly &nbsp;·&nbsp; © 2026</div>
        </div>
        """, unsafe_allow_html=True)


    # ── PAGE ASSEMBLY ────────────────────────────────────────────

    render_hero()
    render_path_cards()
    render_how_it_works()
    render_features()
    render_comparison()
    render_stats()
    render_cta_band()
    render_about_section()
    render_footer()


def render_stock_page():
    # ── GLOBAL CSS ───────────────────────────────────────────────
    st.markdown("""
    <style>
    /* ── Base & Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit chrome — keep header visible so sidebar toggle works */
    #MainMenu, footer { visibility: hidden; }
    header { visibility: visible; background: transparent !important; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .stDeployButton { display: none !important; }
    /* Style the sidebar collapse/expand arrow */
    [data-testid="collapsedControl"] { color: #a78bfa !important; }
    button[kind="header"] { color: #a78bfa !important; }

    /* ── Hero Banner ── */
    .hero-banner {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2.4rem; font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0; line-height: 1.2;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.65); font-size: 1.05rem;
        font-weight: 400; margin-top: 0.4rem;
    }

    /* ── KPI Cards ── */
    .kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.5rem; }
    .kpi-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        backdrop-filter: blur(10px);
        transition: all 0.25s ease;
        position: relative; overflow: hidden;
    }
    .kpi-card::after {
        content: ''; position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        border-radius: 16px 16px 0 0;
    }
    .kpi-card.purple::after { background: linear-gradient(90deg, #a78bfa, #7c3aed); }
    .kpi-card.blue::after   { background: linear-gradient(90deg, #60a5fa, #2563eb); }
    .kpi-card.green::after  { background: linear-gradient(90deg, #34d399, #059669); }
    .kpi-card.orange::after { background: linear-gradient(90deg, #fb923c, #ea580c); }
    .kpi-card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,0.2); box-shadow: 0 12px 40px rgba(0,0,0,0.4); }
    .kpi-label { color: rgba(255,255,255,0.5); font-size: 0.78rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; }
    .kpi-value { color: #ffffff; font-size: 2rem; font-weight: 800; margin: 0.3rem 0 0.1rem; }
    .kpi-sub   { color: rgba(255,255,255,0.4); font-size: 0.78rem; }

    /* ── Section Headers ── */
    .section-header {
        font-size: 1.3rem; font-weight: 700; color: #e2e8f0;
        margin: 1.5rem 0 1rem;
        display: flex; align-items: center; gap: 0.5rem;
    }
    .section-header span { color: #a78bfa; }

    /* ── Glass Cards ── */
    .glass-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }

    /* ── Stock Profile Card ── */
    .stock-profile {
        background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(16,185,129,0.1));
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 20px; padding: 1.8rem 2rem; margin-bottom: 1.5rem;
    }
    .stock-name { font-size: 1.8rem; font-weight: 800; color: #fff; }
    .stock-ticker { font-size: 0.9rem; color: #a78bfa; font-weight: 600; letter-spacing: 0.05em; }
    .stock-country { font-size: 0.85rem; color: rgba(255,255,255,0.5); margin-top: 0.2rem; }

    /* ── Metric Mini Cards ── */
    .metric-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin-top: 1rem; }
    .metric-card {
        background: rgba(0,0,0,0.25); border-radius: 12px;
        padding: 1rem; border: 1px solid rgba(255,255,255,0.07);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-label { font-size: 0.7rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.06em; }
    .metric-val   { font-size: 1.25rem; font-weight: 700; color: #fff; margin-top: 0.2rem; }
    .metric-val.green { color: #34d399; }
    .metric-val.red   { color: #f87171; }
    .metric-val.blue  { color: #60a5fa; }

    /* ── Insight Cards ── */
    .insight-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
    .insight-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.09);
        border-left: 3px solid;
        border-radius: 12px; padding: 1rem 1.2rem;
        transition: all 0.2s;
    }
    .insight-card:hover { background: rgba(255,255,255,0.06); transform: translateX(3px); }
    .insight-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.4rem; }
    .insight-text  { font-size: 0.9rem; color: rgba(255,255,255,0.75); line-height: 1.5; }

    /* ── Skill Badges ── */
    .badge-grid { display: flex; flex-wrap: wrap; gap: 0.7rem; }
    .badge {
        background: rgba(99,102,241,0.15);
        border: 1px solid rgba(99,102,241,0.35);
        border-radius: 50px; padding: 0.45rem 1.1rem;
        font-size: 0.82rem; font-weight: 600; color: #a78bfa;
        transition: all 0.2s;
    }
    .badge:hover { background: rgba(99,102,241,0.3); transform: scale(1.04); }

    /* ── AI Insight Box ── */
    .ai-box {
        background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(99,102,241,0.15));
        border: 1px solid rgba(16,185,129,0.3);
        border-radius: 16px; padding: 1.5rem 2rem;
    }
    .ai-label { font-size: 0.7rem; font-weight: 700; color: #34d399; letter-spacing: 0.1em; text-transform: uppercase; }
    .ai-value  { font-size: 1.1rem; font-weight: 600; color: #fff; margin-top: 0.2rem; }
    .ai-desc   { font-size: 0.85rem; color: rgba(255,255,255,0.55); margin-top: 0.3rem; }

    /* ── Data Quality ── */
    .quality-ring { text-align: center; }
    .quality-score { font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg,#34d399,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .quality-label { font-size: 0.85rem; color: rgba(255,255,255,0.5); }

    /* ── Sidebar Styling ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1535 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] p { color: rgba(255,255,255,0.75) !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #fff !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px; color: rgba(255,255,255,0.6);
        font-weight: 500; padding: 0.5rem 1.2rem;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(60,130,245,0.2));
        border-color: rgba(99,102,241,0.5);
        color: #fff !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f0c29; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.5); border-radius: 10px; }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .kpi-grid { grid-template-columns: repeat(2, 1fr); }
        .metric-row { grid-template-columns: repeat(2, 1fr); }
        .insight-grid { grid-template-columns: 1fr; }
    }

    /* Background */
    .stApp {
        background: linear-gradient(160deg, #0d0b1e 0%, #111827 100%);
    }
    </style>
    """, unsafe_allow_html=True)

    # ── PLOTLY THEME ─────────────────────────────────────────────
    PLOTLY_THEME = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#e2e8f0"),
        margin=dict(l=10, r=10, t=40, b=10),
        colorway=["#a78bfa","#60a5fa","#34d399","#fb923c","#f472b6","#facc15","#2dd4bf","#e879f9"],
    )

    def apply_theme(fig, title="", height=380):
        fig.update_layout(**PLOTLY_THEME, title=dict(text=title, font=dict(size=14, color="#e2e8f0")), height=height)
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)", showgrid=True, zeroline=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", showgrid=True, zeroline=False)
        return fig

    # ── DATA LOADING ─────────────────────────────────────────────
    @st.cache_data(show_spinner=False)
    def load_data():
        df = pd.read_csv("final_data.csv", parse_dates=["Date"])
        df = df.sort_values(["Stock_Name", "Date"]).reset_index(drop=True)
        df["Daily_Return"] = df.groupby("Stock_Name")["Close"].pct_change() * 100
        df["MA20"] = df.groupby("Stock_Name")["Close"].transform(lambda x: x.rolling(20, min_periods=1).mean())
        df["MA50"] = df.groupby("Stock_Name")["Close"].transform(lambda x: x.rolling(50, min_periods=1).mean())
        df["Volatility"] = df.groupby("Stock_Name")["Daily_Return"].transform(lambda x: x.rolling(20, min_periods=1).std())
        return df

    @st.cache_data(show_spinner=False)
    def compute_stock_stats(df):
        stats = df.groupby(["Stock_Name","Country"]).agg(
            Latest_Close=("Close","last"),
            Max_High=("High","max"),
            Min_Low=("Low","min"),
            Avg_Close=("Close","mean"),
            Total_Volume=("Volume","sum"),
            Std_Close=("Close","std"),
            Start_Close=("Close","first"),
        ).reset_index()
        stats["Total_Return_Pct"] = ((stats["Latest_Close"] - stats["Start_Close"]) / stats["Start_Close"]) * 100
        stats["Volatility_Score"] = (stats["Std_Close"] / stats["Avg_Close"]) * 100
        return stats

    @st.cache_data(show_spinner=False)
    def country_stats(df, stock_stats):
        cstats = stock_stats.groupby("Country").agg(
            Num_Stocks=("Stock_Name","count"),
            Avg_Return=("Total_Return_Pct","mean"),
            Avg_Volatility=("Volatility_Score","mean"),
            Total_Volume=("Total_Volume","sum"),
        ).reset_index()
        return cstats.sort_values("Total_Volume", ascending=False)

    # ── LOAD ─────────────────────────────────────────────────────
    with st.spinner("Loading market data…"):
        df = load_data()

    stock_stats = compute_stock_stats(df)
    cstats = country_stats(df, stock_stats)

    all_stocks    = sorted(df["Stock_Name"].unique())
    all_countries = sorted(df["Country"].unique())
    date_min, date_max = df["Date"].min().date(), df["Date"].max().date()

    # ── SIDEBAR ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 1rem 0 0.5rem;'>
            <div style='font-size:2rem;'>📈</div>
            <div style='font-size:1.05rem; font-weight:700; color:#fff;'>StockVision Pro</div>
            <div style='font-size:0.75rem; color:rgba(255,255,255,0.4); margin-top:0.2rem;'>Global Market Analytics</div>
        </div>
        <hr style='border-color:rgba(255,255,255,0.08); margin:0.8rem 0;'/>
        """, unsafe_allow_html=True)

        st.markdown("**🌍 Country Filter**")
        sel_countries = st.multiselect("", options=all_countries, default=all_countries[:5], label_visibility="collapsed")

        st.markdown("**🔍 Stock Search**")
        search_q = st.text_input("", placeholder="Type stock name…", label_visibility="collapsed")

        available_stocks = sorted(
            df[df["Country"].isin(sel_countries)]["Stock_Name"].unique()
            if sel_countries else all_stocks
        )
        if search_q:
            available_stocks = [s for s in available_stocks if search_q.lower() in s.lower()]

        st.markdown("**📊 Select Stock**")
        sel_stock = st.selectbox("", options=available_stocks if available_stocks else all_stocks, label_visibility="collapsed")

        st.markdown("**📅 Date Range**")
        date_from = st.date_input("From", value=date_min, min_value=date_min, max_value=date_max, label_visibility="collapsed")
        date_to   = st.date_input("To",   value=date_max, min_value=date_min, max_value=date_max, label_visibility="collapsed")

        st.markdown("""
        <hr style='border-color:rgba(255,255,255,0.08); margin-top:1.5rem;'/>
        <div style='font-size:0.7rem; color:rgba(255,255,255,0.3); text-align:center; padding-bottom:1rem;'>
            Data spans Jan 2025 – May 2026<br/>300 stocks · 20 countries
        </div>
        """, unsafe_allow_html=True)

    # ── FILTER DATA ──────────────────────────────────────────────
    mask = (
        (df["Date"] >= pd.Timestamp(date_from)) &
        (df["Date"] <= pd.Timestamp(date_to))
    )
    if sel_countries:
        mask &= df["Country"].isin(sel_countries)
    df_filtered = df[mask]

    stock_df = df[(df["Stock_Name"] == sel_stock) & (df["Date"] >= pd.Timestamp(date_from)) & (df["Date"] <= pd.Timestamp(date_to))]
    stock_info = stock_stats[stock_stats["Stock_Name"] == sel_stock].iloc[0] if not stock_stats[stock_stats["Stock_Name"] == sel_stock].empty else None

    # ── HERO BANNER ──────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📈 Stock Intelligence Dashboard</div>
        <div class="hero-subtitle">Interactive Financial Intelligence Platform · Real-Time Insights · 300+ Stocks · 20 Markets</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI CARDS ────────────────────────────────────────────────
    total_stocks = df["Stock_Name"].nunique()
    total_countries = df["Country"].nunique()
    total_rows = len(df)
    best_stock = stock_stats.loc[stock_stats["Total_Return_Pct"].idxmax(), "Stock_Name"]

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card purple">
            <div class="kpi-label">Total Stocks</div>
            <div class="kpi-value">{total_stocks}</div>
            <div class="kpi-sub">Across all markets</div>
        </div>
        <div class="kpi-card blue">
            <div class="kpi-label">Countries Covered</div>
            <div class="kpi-value">{total_countries}</div>
            <div class="kpi-sub">Global coverage</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-label">Total Data Points</div>
            <div class="kpi-value">{total_rows:,}</div>
            <div class="kpi-sub">OHLCV records</div>
        </div>
        <div class="kpi-card orange">
            <div class="kpi-label">Top Performer</div>
            <div class="kpi-value" style="font-size:1.3rem;">{best_stock}</div>
            <div class="kpi-sub">Highest total return</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Stock Explorer",
        "🌍 Country Analytics",
        "📉 Market Overview",
        "💡 Market Insights",
    ])

    # ════════════════════════════════════════════════════════════
    # TAB 1 – STOCK EXPLORER
    # ════════════════════════════════════════════════════════════
    with tab1:
        if stock_info is not None:
            ret_color = "#34d399" if stock_info["Total_Return_Pct"] >= 0 else "#f87171"
            ret_sign  = "+" if stock_info["Total_Return_Pct"] >= 0 else ""
            ticker    = df[df["Stock_Name"] == sel_stock]["Ticker"].iloc[0]

            st.markdown(f"""
            <div class="stock-profile">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
                    <div>
                        <div class="stock-name">{sel_stock}</div>
                        <div class="stock-ticker">NYSE: {ticker}</div>
                        <div class="stock-country">🌐 {stock_info['Country']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.75rem; color:rgba(255,255,255,0.4); text-transform:uppercase; letter-spacing:0.07em;">Latest Close</div>
                        <div style="font-size:2.2rem; font-weight:900; color:#fff;">{stock_info['Latest_Close']:,.2f}</div>
                        <div style="font-size:1rem; font-weight:600; color:{ret_color};">{ret_sign}{stock_info['Total_Return_Pct']:.2f}% total return</div>
                    </div>
                </div>
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-label">All-Time High</div>
                        <div class="metric-val green">{stock_info['Max_High']:,.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">All-Time Low</div>
                        <div class="metric-val red">{stock_info['Min_Low']:,.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Average Close</div>
                        <div class="metric-val blue">{stock_info['Avg_Close']:,.2f}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Volume</div>
                        <div class="metric-val">{stock_info['Total_Volume']/1e6:.1f}M</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Volatility Score</div>
                        <div class="metric-val" style="color:#facc15;">{stock_info['Volatility_Score']:.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Data Points</div>
                        <div class="metric-val">{len(stock_df):,}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if not stock_df.empty:
            c1, c2 = st.columns(2)

            with c1:
                # Price Trend + MAs
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["Close"],
                    mode="lines", name="Close",
                    line=dict(color="#a78bfa", width=2),
                    fill="tozeroy", fillcolor="rgba(167,139,250,0.08)"))
                fig.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["MA20"],
                    mode="lines", name="MA 20", line=dict(color="#60a5fa", width=1.5, dash="dot")))
                fig.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["MA50"],
                    mode="lines", name="MA 50", line=dict(color="#fb923c", width=1.5, dash="dash")))
                fig = apply_theme(fig, f"📈 {sel_stock} — Price & Moving Averages", 400)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                # Candlestick
                fig2 = go.Figure(data=[go.Candlestick(
                    x=stock_df["Date"],
                    open=stock_df["Open"], high=stock_df["High"],
                    low=stock_df["Low"],  close=stock_df["Close"],
                    increasing_line_color="#34d399", decreasing_line_color="#f87171",
                    name="OHLC"
                )])
                fig2 = apply_theme(fig2, f"🕯️ {sel_stock} — Candlestick Chart", 400)
                st.plotly_chart(fig2, use_container_width=True)

            c3, c4 = st.columns(2)

            with c3:
                # Daily Returns
                returns_df = stock_df.dropna(subset=["Daily_Return"])
                fig3 = go.Figure()
                colors = ["#34d399" if r >= 0 else "#f87171" for r in returns_df["Daily_Return"]]
                fig3.add_trace(go.Bar(x=returns_df["Date"], y=returns_df["Daily_Return"],
                    marker_color=colors, name="Daily Return %"))
                fig3 = apply_theme(fig3, f"📊 {sel_stock} — Daily Returns (%)", 350)
                st.plotly_chart(fig3, use_container_width=True)

            with c4:
                # Return Distribution
                fig4 = go.Figure()
                fig4.add_trace(go.Histogram(x=returns_df["Daily_Return"],
                    nbinsx=50, name="Return Dist.",
                    marker_color="#a78bfa", opacity=0.8))
                fig4.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
                mean_r = returns_df["Daily_Return"].mean()
                fig4.add_vline(x=mean_r, line_dash="dot", line_color="#34d399",
                    annotation_text=f"μ={mean_r:.2f}%", annotation_font_color="#34d399")
                fig4 = apply_theme(fig4, f"📉 {sel_stock} — Return Distribution", 350)
                st.plotly_chart(fig4, use_container_width=True)

            # Volume Chart
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(x=stock_df["Date"], y=stock_df["Volume"],
                name="Volume", marker_color="rgba(96,165,250,0.6)"))
            fig5.add_trace(go.Scatter(x=stock_df["Date"],
                y=stock_df["Volume"].rolling(20, min_periods=1).mean(),
                mode="lines", name="20-Day MA Vol",
                line=dict(color="#facc15", width=2)))
            fig5 = apply_theme(fig5, f"📦 {sel_stock} — Volume Analysis", 320)
            st.plotly_chart(fig5, use_container_width=True)

    # ════════════════════════════════════════════════════════════
    # TAB 2 – COUNTRY ANALYTICS
    # ════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-header">🌍 Country Performance Overview</div>', unsafe_allow_html=True)

        disp_cstats = cstats[cstats["Country"].isin(sel_countries)] if sel_countries else cstats

        c1, c2 = st.columns(2)

        with c1:
            fig = px.bar(disp_cstats.sort_values("Total_Volume"), x="Total_Volume", y="Country",
                orientation="h", color="Total_Volume", color_continuous_scale="Viridis",
                labels={"Total_Volume": "Total Volume Traded"})
            fig.update_layout(**PLOTLY_THEME, title="Total Trading Volume by Country",
                height=450, showlegend=False, coloraxis_showscale=False)
            fig.update_yaxes(tickfont=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = px.scatter(disp_cstats, x="Avg_Return", y="Avg_Volatility",
                size="Num_Stocks", color="Avg_Return",
                text="Country", color_continuous_scale="RdYlGn",
                labels={"Avg_Return": "Avg Return (%)", "Avg_Volatility": "Avg Volatility (%)"})
            fig2.update_traces(textposition="top center", textfont_size=10)
            fig2.update_layout(**PLOTLY_THEME, title="Risk vs. Return by Country",
                height=450, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)

        with c3:
            top10_vol = disp_cstats.nlargest(10, "Total_Volume")
            fig3 = px.pie(top10_vol, names="Country", values="Total_Volume",
                hole=0.55, color_discrete_sequence=px.colors.qualitative.Vivid)
            fig3.update_layout(**PLOTLY_THEME, title="Volume Share — Top 10 Countries", height=380)
            fig3.update_traces(textinfo="percent+label", textfont_size=11)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            fig4 = px.bar(disp_cstats.sort_values("Avg_Return", ascending=False),
                x="Country", y="Avg_Return",
                color="Avg_Return", color_continuous_scale="RdYlGn",
                labels={"Avg_Return": "Avg Return (%)"})
            fig4.update_layout(**PLOTLY_THEME, title="Average Stock Return by Country",
                height=380, coloraxis_showscale=False)
            st.plotly_chart(fig4, use_container_width=True)

        # Country stats table
        st.markdown('<div class="section-header">📋 Country Summary Table</div>', unsafe_allow_html=True)
        display_df = disp_cstats.copy()
        display_df["Avg_Return"] = display_df["Avg_Return"].map("{:.2f}%".format)
        display_df["Avg_Volatility"] = display_df["Avg_Volatility"].map("{:.2f}%".format)
        display_df["Total_Volume"] = display_df["Total_Volume"].map("{:,.0f}".format)
        display_df.columns = ["Country", "# Stocks", "Avg Return", "Avg Volatility", "Total Volume"]
        st.dataframe(display_df.reset_index(drop=True), use_container_width=True, height=350)

    # ════════════════════════════════════════════════════════════
    # TAB 3 – MARKET OVERVIEW
    # ════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-header">📉 Broad Market Analysis</div>', unsafe_allow_html=True)

        # Top 15 by return
        top_performers = stock_stats.nlargest(15, "Total_Return_Pct")
        bot_performers = stock_stats.nsmallest(10, "Total_Return_Pct")

        c1, c2 = st.columns(2)

        with c1:
            fig = px.bar(top_performers.sort_values("Total_Return_Pct"),
                x="Total_Return_Pct", y="Stock_Name", orientation="h",
                color="Total_Return_Pct", color_continuous_scale="Greens",
                labels={"Total_Return_Pct": "Total Return (%)"})
            fig.update_layout(**PLOTLY_THEME, title="🏆 Top 15 Performers", height=480, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = px.bar(bot_performers.sort_values("Total_Return_Pct", ascending=False),
                x="Total_Return_Pct", y="Stock_Name", orientation="h",
                color="Total_Return_Pct", color_continuous_scale="Reds_r",
                labels={"Total_Return_Pct": "Total Return (%)"})
            fig2.update_layout(**PLOTLY_THEME, title="📉 Bottom 10 Performers", height=480, coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Volatility vs Return scatter
        fig3 = px.scatter(stock_stats, x="Volatility_Score", y="Total_Return_Pct",
            color="Country", size="Total_Volume",
            hover_name="Stock_Name",
            labels={"Volatility_Score": "Volatility (%)", "Total_Return_Pct": "Total Return (%)"},
            size_max=35)
        fig3.update_layout(**PLOTLY_THEME, title="🎯 Risk vs. Return — All Stocks (bubble = volume)",
            height=480)
        st.plotly_chart(fig3, use_container_width=True)

        # Correlation heatmap (top 20 US stocks close prices)
        st.markdown('<div class="section-header">🔗 Correlation Heatmap — Top Stocks</div>', unsafe_allow_html=True)
        top20 = stock_stats.nlargest(20, "Total_Volume")["Stock_Name"].tolist()
        pivot = df[df["Stock_Name"].isin(top20)].pivot_table(index="Date", columns="Stock_Name", values="Close")
        corr = pivot.pct_change().corr()
        fig4 = px.imshow(corr, color_continuous_scale="RdBu_r", aspect="auto",
            labels=dict(color="Correlation"), zmin=-1, zmax=1)
        fig4.update_layout(**PLOTLY_THEME, title="Price Return Correlation — Top 20 by Volume",
            height=600)
        st.plotly_chart(fig4, use_container_width=True)

    # ════════════════════════════════════════════════════════════
    # TAB 4 – MARKET INSIGHTS
    # ════════════════════════════════════════════════════════════
    with tab4:
        # Dataset quality score (used in the Coverage Quality insight below)
        missing_count = df.isnull().sum().sum()
        dup_count     = df.duplicated().sum()
        completeness  = round(100 - (missing_count / df.size * 100), 1)
        uniqueness    = round(100 - (dup_count / len(df) * 100), 1)
        quality_score = round((completeness * 0.5 + uniqueness * 0.5), 1)

        st.markdown('<div class="section-header">💡 Dynamic Market Insights</div>', unsafe_allow_html=True)

        # Auto-generate 12 insights
        best_return_stock = stock_stats.loc[stock_stats["Total_Return_Pct"].idxmax()]
        worst_return_stock = stock_stats.loc[stock_stats["Total_Return_Pct"].idxmin()]
        lowest_vol_stock  = stock_stats.loc[stock_stats["Volatility_Score"].idxmin()]
        highest_vol_stock = stock_stats.loc[stock_stats["Volatility_Score"].idxmax()]
        top_country_vol   = cstats.iloc[0]
        best_country_ret  = cstats.loc[cstats["Avg_Return"].idxmax()]
        worst_country_ret = cstats.loc[cstats["Avg_Return"].idxmin()]
        usa_stocks        = len(stock_stats[stock_stats["Country"]=="USA"])
        overall_bull_bear = "Bullish" if stock_stats["Total_Return_Pct"].mean() > 0 else "Bearish"
        tech_stocks       = ["Apple","Microsoft","NVIDIA","Alphabet","Meta","Oracle","Netflix"]
        tech_avg_ret      = stock_stats[stock_stats["Stock_Name"].isin(tech_stocks)]["Total_Return_Pct"].mean()
        overall_avg_ret   = stock_stats["Total_Return_Pct"].mean()
        top_vol_stock     = stock_stats.loc[stock_stats["Total_Volume"].idxmax()]

        INSIGHT_COLORS = ["#a78bfa","#60a5fa","#34d399","#fb923c","#f472b6","#facc15","#2dd4bf","#e879f9","#a78bfa","#60a5fa","#34d399","#fb923c"]

        insights = [
            ("🏆 Top Performer", f"{best_return_stock['Stock_Name']} leads with an outstanding {best_return_stock['Total_Return_Pct']:.2f}% total return over the analysis period.", INSIGHT_COLORS[0]),
            ("📉 Worst Performer", f"{worst_return_stock['Stock_Name']} recorded the steepest decline at {worst_return_stock['Total_Return_Pct']:.2f}% total return.", INSIGHT_COLORS[1]),
            ("🧊 Most Stable Stock", f"{lowest_vol_stock['Stock_Name']} exhibits the lowest volatility score of {lowest_vol_stock['Volatility_Score']:.2f}%, ideal for risk-averse investors.", INSIGHT_COLORS[2]),
            ("🌋 Most Volatile Stock", f"{highest_vol_stock['Stock_Name']} carries the highest volatility score at {highest_vol_stock['Volatility_Score']:.2f}% — high risk, high reward.", INSIGHT_COLORS[3]),
            ("🌍 Trading Volume Giant", f"{top_country_vol['Country']} dominates trading volumes with {top_country_vol['Total_Volume']/1e9:.2f}B total shares traded.", INSIGHT_COLORS[4]),
            ("🚀 Best Country Returns", f"{best_country_ret['Country']} stocks generated the highest average return of {best_country_ret['Avg_Return']:.2f}%.", INSIGHT_COLORS[5]),
            ("⚠️ Weakest Market", f"{worst_country_ret['Country']} underperformed with an average return of {worst_country_ret['Avg_Return']:.2f}%.", INSIGHT_COLORS[6]),
            ("🇺🇸 US Dominance", f"USA contributes {usa_stocks} stocks to the dataset — the largest single-country representation.", INSIGHT_COLORS[7]),
            ("📈 Market Sentiment", f"Overall market sentiment is {overall_bull_bear}, with the average stock return at {overall_avg_ret:.2f}% across all covered equities.", INSIGHT_COLORS[8]),
            ("💻 Technology Sector", f"Tech stocks average {tech_avg_ret:.2f}% return, {'outperforming' if tech_avg_ret > overall_avg_ret else 'underperforming'} the broad market by {abs(tech_avg_ret-overall_avg_ret):.2f}%.", INSIGHT_COLORS[9]),
            ("📦 Volume Leader", f"{top_vol_stock['Stock_Name']} is the most actively traded stock with {top_vol_stock['Total_Volume']/1e9:.2f}B shares traded.", INSIGHT_COLORS[10]),
            ("🔢 Dataset Scale", f"With {total_rows:,} rows across {total_stocks} stocks and {total_countries} countries, this is an enterprise-grade multi-market dataset.", INSIGHT_COLORS[11]),
        ]

        st.markdown('<div class="insight-grid">', unsafe_allow_html=True)
        for title, text, color in insights:
            st.markdown(f"""
            <div class="insight-card" style="border-left-color:{color};">
                <div class="insight-title" style="color:{color};">{title}</div>
                <div class="insight-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # AI Style Summary Box
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">🤖 AI-Style Market Intelligence</div>', unsafe_allow_html=True)
        risk_label = "High" if stock_stats["Volatility_Score"].mean() > 20 else "Moderate" if stock_stats["Volatility_Score"].mean() > 10 else "Low"

        st.markdown(f"""
        <div class="ai-box">
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; flex-wrap:wrap;">
                <div>
                    <div class="ai-label">Market Trend</div>
                    <div class="ai-value">{'🟢 Bullish' if overall_avg_ret > 0 else '🔴 Bearish'}</div>
                    <div class="ai-desc">Based on average stock returns across the full dataset period</div>
                </div>
                <div>
                    <div class="ai-label">Highest Returning Stock</div>
                    <div class="ai-value">🏆 {best_return_stock['Stock_Name']}</div>
                    <div class="ai-desc">+{best_return_stock['Total_Return_Pct']:.2f}% total return over the analysis window</div>
                </div>
                <div>
                    <div class="ai-label">Risk Category</div>
                    <div class="ai-value">⚡ {risk_label} Risk</div>
                    <div class="ai-desc">Average market volatility score: {stock_stats['Volatility_Score'].mean():.2f}%</div>
                </div>
                <div>
                    <div class="ai-label">Dominant Country</div>
                    <div class="ai-value">🌍 {top_country_vol['Country']}</div>
                    <div class="ai-desc">Leads in total trading volume with {top_country_vol['Num_Stocks']} stocks</div>
                </div>
                <div>
                    <div class="ai-label">Investment Observation</div>
                    <div class="ai-value" style="font-size:0.95rem;">{'Tech stocks outperform the market.' if tech_avg_ret > overall_avg_ret else 'Tech stocks lag the market average.'}</div>
                    <div class="ai-desc">Technology sector avg: {tech_avg_ret:.2f}% vs market avg: {overall_avg_ret:.2f}%</div>
                </div>
                <div>
                    <div class="ai-label">Coverage Quality</div>
                    <div class="ai-value">✅ {quality_score}/100</div>
                    <div class="ai-desc">Excellent dataset completeness — zero missing values</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Footer (full breakdown of skills, tech stack & dataset scope now lives
    # in the common "About" section on the home page)
    st.markdown("""
    <br>
    <div style="text-align:center; padding: 2rem; color:rgba(255,255,255,0.25); font-size:0.8rem; border-top: 1px solid rgba(255,255,255,0.06);">
        📈 Global Stock Intelligence Dashboard &nbsp;|&nbsp; Built with Streamlit & Plotly &nbsp;|&nbsp; Data: 2025–2026
    </div>
    """, unsafe_allow_html=True)

def render_mf_page():
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

        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Your Plan", "🏆 Recommendations", "📈 Wealth Journey", "🔎 Fund Explorer",
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

        # ---------- HOW YOUR RECOMMENDATION IS GENERATED ----------
        # (kept outside the tabs now that the "Portfolio" showcase tab has
        # been removed; skills/tech-stack/dataset-scope content now lives in
        # the common "About" section on the home page)
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

        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""
            <div class="glass-card">
                <div style="font-weight:800;color:#fff;">Risk Engine Weights</div><br>
                <div class="insight-text">
                    Loss reaction — 25%<br>What matters more — 20%<br>Investment experience — 15%<br>
                    Income stability — 15%<br>Comfort with fluctuations — 15%<br>Primary priority — 10%
                </div>
            </div>
            """, unsafe_allow_html=True)
        with rc2:
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

# ── PAGE DISPATCH ────────────────────────────────────────────
if _page == "stock":
    render_stock_page()
elif _page == "mf":
    render_mf_page()
else:
    render_home_page()
