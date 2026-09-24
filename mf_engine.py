"""
MF India AI — Recommendation Engine
Pure calculation layer, deliberately kept free of any Streamlit / UI code
so that the UI (mf_recommendation_app.py) only ever renders numbers that
came out of here. Column names match MF_India_AI_Risk_Engine.csv exactly.
"""

import math
import numpy as np
import pandas as pd

DATA_FILE = "MF_India_AI_Risk_Engine.csv"

NUMERIC_COLS = [
    "min_sip", "min_lumpsum", "expense_ratio", "fund_size_cr",
    "fund_age_yr", "sortino", "alpha", "sd", "beta", "sharpe",
    "risk_level", "rating", "returns_1yr", "returns_3yr", "returns_5yr",
    "sd_risk", "beta_risk", "sharpe_risk", "sortino_risk",
    "risk_score", "calculated_risk_numeric", "return_score",
    "sharpe_quality", "sortino_quality", "fund_quality_score",
    "risk_gap", "risk_compatibility", "recommendation_score",
]

# Illustrative planning assumptions only — NOT guaranteed returns.
SCENARIO_RATES = {"Conservative": 8.0, "Expected": 10.0, "Optimistic": 12.0}
ASSET_EXPECTED_RETURN = {"Equity": 11.0, "Hybrid": 9.0, "Debt": 7.0}


# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────
def load_data(path=DATA_FILE):
    data = pd.read_csv(path)
    for col in NUMERIC_COLS:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    data["asset_class"] = data.apply(classify_asset_class, axis=1)
    return data


def classify_asset_class(row):
    category = str(row.get("category", "")).lower()
    if category == "equity":
        return "Equity"
    if category == "debt":
        return "Debt"
    if category == "hybrid":
        return "Hybrid"
    return "Other"


# ─────────────────────────────────────────────────────────────
# FORMATTING HELPERS (Indian numbering, NaN/Inf safe)
# ─────────────────────────────────────────────────────────────
def safe_num(value, default=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(value) or math.isinf(value):
        return default
    return value


def format_inr(value, decimals=2):
    """₹ value -> ₹X.XX Cr / ₹X.XX L / ₹X,XXX style string. Never NaN/Inf."""
    value = safe_num(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_00_00_000:
        return f"{sign}₹{value / 1_00_00_000:,.{decimals}f} Cr"
    if value >= 1_00_000:
        return f"{sign}₹{value / 1_00_000:,.{decimals}f} L"
    return f"{sign}₹{value:,.0f}"


def format_pct(value, decimals=1):
    value = safe_num(value)
    return f"{value:.{decimals}f}%"


# ─────────────────────────────────────────────────────────────
# RISK QUESTIONNAIRE -> INVESTOR RISK SCORE
# ─────────────────────────────────────────────────────────────
# Each behavioral question is answered A-E, mapped to 1-5.
RISK_WEIGHTS = {
    "loss_reaction": 0.25,     # Q1 - falls 20% temporarily
    "priority": 0.20,          # Q2 - what matters more
    "experience": 0.15,        # Q3 - investment experience
    "income_stability": 0.15,  # Q4 - income stability
    "comfort": 0.15,           # Q5 - comfort with fluctuations
    "primary_priority": 0.10,  # Q6 - primary priority
}


def get_risk_profile(score):
    if score < 20:
        return "Very Conservative", 1
    elif score < 40:
        return "Conservative", 2
    elif score < 60:
        return "Moderate", 3
    elif score < 80:
        return "Aggressive", 4
    return "Very Aggressive", 5


def calculate_investor_risk(answers: dict):
    """answers: dict with keys matching RISK_WEIGHTS, values 1-5."""
    total = 0.0
    for key, weight in RISK_WEIGHTS.items():
        total += weight * safe_num(answers.get(key, 3), 3)
    # total is on a 1-5 scale -> rescale to 0-100
    score = (total - 1) / 4 * 100
    return round(min(max(score, 0), 100), 1)


# ─────────────────────────────────────────────────────────────
# GOAL + HORIZON -> ASSET ALLOCATION
# ─────────────────────────────────────────────────────────────
def goal_strategy(goal, horizon):
    if goal == "Emergency / Short-Term":
        return {"Equity": 0, "Hybrid": 20, "Debt": 80}
    if horizon <= 3:
        return {"Equity": 10, "Hybrid": 20, "Debt": 70}
    elif horizon <= 7:
        return {"Equity": 40, "Hybrid": 30, "Debt": 30}
    elif horizon <= 15:
        return {"Equity": 60, "Hybrid": 25, "Debt": 15}
    return {"Equity": 75, "Hybrid": 20, "Debt": 5}


def adjust_for_risk(allocation, risk_level):
    allocation = allocation.copy()
    if risk_level <= 2:
        shift = allocation["Equity"] * 0.25
        allocation["Equity"] -= shift
        allocation["Debt"] += shift * 0.70
        allocation["Hybrid"] += shift * 0.30
    elif risk_level >= 4:
        shift = allocation["Debt"] * 0.40
        allocation["Debt"] -= shift
        allocation["Equity"] += shift * 0.70
        allocation["Hybrid"] += shift * 0.30
    total = sum(allocation.values())
    if total <= 0:
        return {"Equity": 0.0, "Hybrid": 0.0, "Debt": 100.0}
    return {k: round(v / total * 100, 1) for k, v in allocation.items()}


def calculate_sip_allocation(monthly_sip, allocation):
    return {asset: round(monthly_sip * pct / 100, 2) for asset, pct in allocation.items()}


# ─────────────────────────────────────────────────────────────
# FUND RANKING + PORTFOLIO CONSTRUCTION
# ─────────────────────────────────────────────────────────────
def rank_funds_for_bucket(data, asset_class, investor_risk_level, amount):
    funds = data[data["asset_class"] == asset_class].copy()
    funds = funds[funds["min_sip"].fillna(np.inf) <= amount]

    required = ["fund_quality_score", "calculated_risk_numeric", "returns_3yr", "sharpe", "sortino"]
    funds = funds.dropna(subset=[c for c in required if c in funds.columns])

    if funds.empty:
        return funds

    funds["risk_match"] = (100 - abs(funds["calculated_risk_numeric"] - investor_risk_level) * 25).clip(0, 100)

    funds["return_component"] = funds.groupby("sub_category")["returns_3yr"].rank(pct=True) * 100
    funds["sharpe_component"] = funds.groupby("sub_category")["sharpe"].rank(pct=True) * 100
    funds["sortino_component"] = funds.groupby("sub_category")["sortino"].rank(pct=True) * 100

    expense_min = funds["expense_ratio"].min()
    expense_max = funds["expense_ratio"].max()
    if pd.isna(expense_min) or pd.isna(expense_max) or expense_max == expense_min:
        funds["expense_component"] = 50.0
    else:
        funds["expense_component"] = (expense_max - funds["expense_ratio"]) / (expense_max - expense_min) * 100

    funds["portfolio_score"] = (
        0.35 * funds["risk_match"]
        + 0.25 * funds["fund_quality_score"]
        + 0.15 * funds["return_component"]
        + 0.10 * funds["sharpe_component"]
        + 0.10 * funds["sortino_component"]
        + 0.05 * funds["expense_component"]
    )

    return funds.sort_values(["portfolio_score", "fund_quality_score"], ascending=False)


def build_portfolio(data, allocation, sip_allocation, risk_level):
    rows = []
    for asset_class, percentage in allocation.items():
        amount = sip_allocation.get(asset_class, 0)
        if amount <= 0:
            continue
        ranked = rank_funds_for_bucket(data, asset_class, risk_level, amount)
        if ranked.empty:
            continue
        selected = ranked.iloc[0]
        rows.append({
            "Asset Class": asset_class,
            "Allocation %": percentage,
            "Monthly SIP": amount,
            "Fund": selected["scheme_name"],
            "AMC": selected["amc_name"],
            "Sub Category": selected["sub_category"],
            "Risk Score": safe_num(selected["risk_score"]),
            "Risk Level": selected["calculated_risk_level"],
            "Risk Match": safe_num(selected["risk_match"]),
            "Fund Quality": safe_num(selected["fund_quality_score"]),
            "3Y Return": safe_num(selected["returns_3yr"]),
            "Sharpe": safe_num(selected["sharpe"]),
            "Sortino": safe_num(selected["sortino"]),
            "Expense Ratio": safe_num(selected["expense_ratio"]),
            "Expense Component": safe_num(selected["expense_component"]),
            "Portfolio Score": safe_num(selected["portfolio_score"]),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────
# WEALTH PROJECTION
# ─────────────────────────────────────────────────────────────
def sip_future_value(monthly_sip, annual_return, years):
    monthly_sip = safe_num(monthly_sip)
    years = max(safe_num(years), 0)
    monthly_rate = annual_return / 12 / 100
    months = int(round(years * 12))
    if months <= 0:
        return 0.0
    if monthly_rate == 0:
        return monthly_sip * months
    return monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)


def lumpsum_future_value(lumpsum, annual_return, years):
    lumpsum = safe_num(lumpsum)
    years = max(safe_num(years), 0)
    return lumpsum * (1 + annual_return / 100) ** years


def wealth_projection(monthly_sip, lumpsum, annual_return, years):
    sip_value = sip_future_value(monthly_sip, annual_return, years)
    lump_value = lumpsum_future_value(lumpsum, annual_return, years)
    corpus = sip_value + lump_value
    invested = safe_num(monthly_sip) * years * 12 + safe_num(lumpsum)
    return {"invested": invested, "corpus": corpus, "gains": corpus - invested}


def blended_rate_for_allocation(sip_allocation):
    """Weighted expected return across asset classes, for the 'Expected' scenario table."""
    total = sum(sip_allocation.values())
    if total <= 0:
        return ASSET_EXPECTED_RETURN["Debt"]
    weighted = sum(
        safe_num(amount) * ASSET_EXPECTED_RETURN.get(asset, 8.0)
        for asset, amount in sip_allocation.items()
    )
    return weighted / total


def portfolio_projection(sip_allocation, lumpsum, years, rate_override=None):
    corpus = 0.0
    invested_sip = 0.0
    for asset, amount in sip_allocation.items():
        rate = rate_override if rate_override is not None else ASSET_EXPECTED_RETURN.get(asset, 8.0)
        corpus += sip_future_value(amount, rate, years)
        invested_sip += safe_num(amount) * years * 12
    blended_rate = rate_override if rate_override is not None else blended_rate_for_allocation(sip_allocation)
    corpus += lumpsum_future_value(lumpsum, blended_rate, years)
    invested = invested_sip + safe_num(lumpsum)
    return {"invested": invested, "corpus": corpus, "gains": corpus - invested}


def portfolio_age_projection(age, target_age, sip_allocation, lumpsum, rate_override=None):
    rows = []
    for current_age in range(int(age), int(target_age) + 1):
        years = current_age - age
        p = portfolio_projection(sip_allocation, lumpsum, years, rate_override)
        rows.append({"Age": current_age, "Years": years, "Invested": p["invested"],
                      "Corpus": p["corpus"], "Gains": p["gains"]})
    return pd.DataFrame(rows)


def required_sip_for_target(target_corpus, lumpsum, allocation_pct, years, annual_return=None):
    """Binary-search the monthly SIP (split per allocation_pct) needed to reach target_corpus."""
    target_corpus = safe_num(target_corpus)
    if target_corpus <= 0 or years <= 0:
        return 0.0

    def corpus_for_sip(total_sip):
        alloc = calculate_sip_allocation(total_sip, allocation_pct)
        rate = annual_return
        return portfolio_projection(alloc, lumpsum, years, rate)["corpus"]

    lo, hi = 0.0, 1.0
    # Expand hi until it comfortably exceeds the target (cap iterations for safety).
    for _ in range(60):
        if corpus_for_sip(hi) >= target_corpus:
            break
        hi *= 2
    else:
        return float("nan")  # Could not bracket a solution (e.g. absurdly high target).

    for _ in range(60):
        mid = (lo + hi) / 2
        if corpus_for_sip(mid) < target_corpus:
            lo = mid
        else:
            hi = mid
    return hi


# ─────────────────────────────────────────────────────────────
# PORTFOLIO QUALITY SCORE
# ─────────────────────────────────────────────────────────────
def portfolio_quality_score(portfolio_df, allocation):
    """Returns dict with Risk Fit / Diversification / Fund Quality / Cost Efficiency / Overall.
    All figures are derived only from what was actually selected — nothing fabricated."""
    if portfolio_df is None or portfolio_df.empty:
        return None

    weights = portfolio_df["Monthly SIP"]
    total_weight = weights.sum()
    if total_weight <= 0:
        return None

    def weighted(col):
        return float((portfolio_df[col] * weights).sum() / total_weight)

    risk_fit = weighted("Risk Match")
    fund_quality = weighted("Fund Quality")
    cost_efficiency = weighted("Expense Component")

    # Diversification: how many of the planned, non-zero asset-class buckets
    # actually got a fund, plus a bonus for spreading across sub-categories.
    planned_buckets = sum(1 for pct in allocation.values() if pct > 0)
    filled_buckets = portfolio_df["Asset Class"].nunique()
    bucket_coverage = (filled_buckets / planned_buckets * 100) if planned_buckets else 0
    sub_category_spread = min(portfolio_df["Sub Category"].nunique() / max(filled_buckets, 1), 1.0) * 100
    diversification = 0.7 * bucket_coverage + 0.3 * sub_category_spread

    overall = 0.35 * risk_fit + 0.30 * fund_quality + 0.20 * diversification + 0.15 * cost_efficiency

    return {
        "Risk Fit": round(risk_fit, 1),
        "Diversification": round(diversification, 1),
        "Fund Quality": round(fund_quality, 1),
        "Cost Efficiency": round(cost_efficiency, 1),
        "Overall": round(overall, 1),
    }
