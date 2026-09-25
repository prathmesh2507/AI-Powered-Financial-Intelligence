# ============================================================
# ◈ FinSight AI — Investment Intelligence Platform
# Landing page / launcher for:
#   • stock_app.py  (Manual Mode — Stock Intelligence)
#   • mf_app.py     (Automation Mode — MF Recommendation Engine)
#
# This file does NOT import, execute, or modify stock_app.py
# or mf_app.py in any way. It only links out to their deployed
# URLs. Stack: Streamlit only.
# ============================================================

import streamlit as st

# ── ROUTING CONSTANTS ───────────────────────────────────────
from stock_app import render_stock_app
from mf_app import render_mf_app

# Internal page routing — no external Streamlit URLs.
HOME_PAGE = "Home"
STOCK_PAGE = "Stock Intelligence"
MF_PAGE = "Mutual Fund Advisor"

if "page" not in st.session_state:
    st.session_state.page = HOME_PAGE

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="FinSight AI | Investment Intelligence Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

def render_nav():
    st.markdown("""
    <div class="fs-nav">
        <div class="fs-brand">
            <div class="fs-brand-name">◈ FinSight <span>AI</span></div>
            <div class="fs-brand-sub">FINANCIAL INTELLIGENCE PLATFORM</div>
        </div>
        <div class="fs-navlinks">
            <span>Markets</span><span>Intelligence</span><span>About</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


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
    st.markdown("""
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
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📈  Explore Stock Intelligence  →", key="home_stock", use_container_width=True, type="primary"):
            st.session_state.page = STOCK_PAGE
            st.rerun()
        st.caption("For investors who want to analyze the market themselves.")
    with c2:
        if st.button("🤖  Start AI Recommendation  →", key="home_mf", use_container_width=True):
            st.session_state.page = MF_PAGE
            st.rerun()
        st.caption("For users who want guidance instead of manually analyzing markets.")

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
    st.markdown("""
    <div class="fs-section">
        <div class="fs-ctaband">
            <h2>Your Financial Journey Starts Here.</h2>
            <p>Explore the market. Understand the data. Build a smarter investment path.</p>
        </div>
        <div class="fs-disclaimer">
            Educational &amp; informational platform only. Market data, projections and
            recommendations are intended for informational purposes and should not be
            considered personal financial advice or a guarantee of future returns.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Explore Markets", key="cta_stock", use_container_width=True, type="primary"):
            st.session_state.page = STOCK_PAGE
            st.rerun()
    with c2:
        if st.button("Get Personalized Guidance", key="cta_mf", use_container_width=True):
            st.session_state.page = MF_PAGE
            st.rerun()

def render_footer():
    st.markdown("""
    <div class="fs-footer">
        <div class="fbrand">◈ FinSight <span>AI</span></div>
        <div class="fsub">Financial Intelligence Platform</div>
        <div class="fsub">Market Analytics • Personalized Intelligence • Data-Driven Insights</div>
        <div class="fmeta">Built with Streamlit + Python + Plotly &nbsp;·&nbsp; © 2026</div>
    </div>
    """, unsafe_allow_html=True)


# ── PAGE ROUTING ─────────────────────────────────────────────

def render_home_page():
    render_nav()
    render_hero()
    render_path_cards()
    render_how_it_works()
    render_features()
    render_comparison()
    render_stats()
    render_cta_band()
    render_footer()


def render_app_nav():
    st.markdown("""
    <div style="text-align:center; padding: 0.4rem 0 0.8rem;">
        <div style="font-size:0.78rem; color:#6B7280; letter-spacing:.08em; text-transform:uppercase;">FinSight AI</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.page = HOME_PAGE
            st.rerun()
    with c2:
        if st.button("📈 Stock Intelligence", key="nav_stock", use_container_width=True):
            st.session_state.page = STOCK_PAGE
            st.rerun()
    with c3:
        if st.button("💰 Mutual Fund Advisor", key="nav_mf", use_container_width=True):
            st.session_state.page = MF_PAGE
            st.rerun()
    st.divider()


page = st.session_state.page

if page == HOME_PAGE:
    render_home_page()
elif page == STOCK_PAGE:
    render_app_nav()
    render_stock_app()
else:
    render_app_nav()
    render_mf_app()
