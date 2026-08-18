"""
Heavy-Duty Fleet Decarbonization Evaluation Model
--------------------------------------------------
Physics-based powertrain comparison for urban municipal (refuse) trucks.

Model parameters, energy densities, efficiencies, emissions factors and the
weighted-scoring method are taken from the Energy Analysis workbook
(Sheets: Assumptions, Diesel/Hydrogen/Battery Calculations, Decision Logic).
"""

import base64

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Fleet Decarbonization Model",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# DESIGN TOKENS
# ==========================================================
INK = "#1d1d1f"          # primary text
SUBTLE = "#6e6e73"       # secondary text
HAIRLINE = "#d2d2d7"     # dividers
CANVAS = "#f5f5f7"       # page background
SURFACE = "#ffffff"      # card background
ACCENT = "#0071e3"       # system blue

C_DIESEL = "#8e8e93"     # graphite
C_HYDROGEN = "#5e5ce6"   # indigo
C_BATTERY = "#30b158"    # green

TECH_COLORS = {
    "Diesel": C_DIESEL,
    "Hydrogen Fuel Cell": C_HYDROGEN,
    "Battery Electric": C_BATTERY,
}

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

      html, body, [class*="css"], .stApp {{
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                     "SF Pro Text", "Inter", "Helvetica Neue", Arial, sans-serif;
        color: {INK};
      }}

      .stApp {{ background: {CANVAS}; }}

      .block-container {{
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        max-width: 1320px;
      }}

      #MainMenu, footer, header {{ visibility: hidden; }}

      /* ---------- Typography ---------- */
      .eyebrow {{
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        color: {SUBTLE};
        margin-bottom: 0.55rem;
      }}
      .headline {{
        font-size: 3.15rem;
        font-weight: 600;
        letter-spacing: -0.028em;
        line-height: 1.05;
        margin: 0 0 0.55rem 0;
      }}
      .subhead {{
        font-size: 1.16rem;
        font-weight: 400;
        color: {SUBTLE};
        letter-spacing: -0.01em;
        line-height: 1.5;
        max-width: 62ch;
        margin-bottom: 2.1rem;
      }}
      .section-title {{
        font-size: 1.55rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        margin: 0 0 0.25rem 0;
      }}
      .section-note {{
        font-size: 0.95rem;
        color: {SUBTLE};
        margin-bottom: 1.1rem;
      }}

      /* ---------- Cards ---------- */
      .card {{
        background: {SURFACE};
        border-radius: 20px;
        padding: 1.6rem 1.75rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 28px rgba(0,0,0,0.05);
        margin-bottom: 1.1rem;
      }}

      /* ---------- Hero: the recommendation ---------- */
      .hero {{
        background: linear-gradient(160deg, #ffffff 0%, #f0f4fb 100%);
        border-radius: 26px;
        padding: 2.1rem 2.3rem 1.9rem 2.3rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05), 0 18px 44px rgba(0,0,0,0.07);
        margin-bottom: 1.35rem;
      }}
      .hero-label {{
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.1em;
        text-transform: uppercase; color: {SUBTLE};
      }}
      .hero-tech {{
        font-size: 2.55rem; font-weight: 600; letter-spacing: -0.03em;
        line-height: 1.1; margin: 0.35rem 0 0.15rem 0;
      }}
      .hero-reason {{
        font-size: 1.0rem; color: {SUBTLE}; line-height: 1.55;
        max-width: 52ch; margin-top: 0.5rem;
      }}
      .hero-score {{
        font-size: 5.6rem; font-weight: 600; letter-spacing: -0.045em;
        line-height: 0.92; text-align: right;
      }}
      .hero-score-unit {{
        font-size: 1.6rem; font-weight: 500; color: {SUBTLE};
        letter-spacing: -0.02em;
      }}
      .hero-score-cap {{
        text-align: right; font-size: 0.78rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase; color: {SUBTLE};
        margin-top: 0.45rem;
      }}

      /* ---------- Score cards ---------- */
      .score-card {{
        background: {SURFACE};
        border-radius: 20px;
        padding: 1.35rem 1.5rem 1.5rem 1.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 26px rgba(0,0,0,0.05);
        height: 100%;
      }}
      .score-card.win {{ box-shadow: 0 0 0 2px {ACCENT}, 0 10px 30px rgba(0,113,227,0.16); }}
      .score-tech {{
        font-size: 1.02rem; font-weight: 600; letter-spacing: -0.01em;
        display: flex; align-items: center; gap: 0.5rem;
      }}
      .dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; }}
      .score-value {{
        font-size: 3.3rem; font-weight: 600; letter-spacing: -0.04em;
        line-height: 1.05; margin-top: 0.5rem;
      }}
      .score-sub {{ font-size: 0.83rem; color: {SUBTLE}; letter-spacing: 0.01em; }}
      .bar-track {{
        height: 6px; border-radius: 99px; background: #e8e8ed;
        margin: 0.95rem 0 0.85rem 0; overflow: hidden;
      }}
      .bar-fill {{ height: 6px; border-radius: 99px; }}
      .kv {{
        display: flex; justify-content: space-between;
        font-size: 0.88rem; padding: 0.28rem 0;
        border-bottom: 1px solid #f0f0f2;
      }}
      .kv:last-child {{ border-bottom: none; }}
      .kv span:first-child {{ color: {SUBTLE}; }}
      .kv span:last-child {{ font-weight: 500; font-variant-numeric: tabular-nums; }}
      .badge {{
        display: inline-block; background: {ACCENT}; color: #fff;
        font-size: 0.68rem; font-weight: 600; letter-spacing: 0.07em;
        text-transform: uppercase; padding: 0.2rem 0.55rem;
        border-radius: 99px; margin-left: 0.4rem;
      }}

      /* ---------- Weight budget ---------- */
      .budget-track {{
        height: 8px; border-radius: 99px; background: #e8e8ed;
        overflow: hidden; margin: 0.4rem 0 0.35rem 0;
      }}
      .budget-fill {{ height: 8px; border-radius: 99px; background: {ACCENT}; }}
      .budget-fill.full {{ background: #30b158; }}
      .budget-text {{ font-size: 0.82rem; color: {SUBTLE}; }}

      /* ---------- Equation blocks ---------- */
      .eq-card {{
        background: {SURFACE}; border-radius: 18px; padding: 1.35rem 1.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 6px 22px rgba(0,0,0,0.045);
        margin-bottom: 1rem;
      }}
      .eq-num {{
        font-size: 0.74rem; font-weight: 600; letter-spacing: 0.1em;
        color: {ACCENT}; text-transform: uppercase;
      }}
      .eq-title {{
        font-size: 1.12rem; font-weight: 600; letter-spacing: -0.015em;
        margin: 0.2rem 0 0.15rem 0;
      }}
      .eq-body {{ font-size: 0.9rem; color: {SUBTLE}; line-height: 1.6; }}
      .eq-body b {{ color: {INK}; font-weight: 500; }}

      /* ---------- Sidebar ---------- */
      [data-testid="stSidebar"] {{
        background: {SURFACE};
        border-right: 1px solid {HAIRLINE};
      }}
      [data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}
      .side-group {{
        font-size: 0.74rem; font-weight: 600; letter-spacing: 0.1em;
        text-transform: uppercase; color: {SUBTLE};
        margin: 1.35rem 0 0.35rem 0;
      }}

      /* ---------- Tabs ---------- */
      .stTabs [data-baseweb="tab-list"] {{
        gap: 0.35rem; border-bottom: 1px solid {HAIRLINE};
      }}
      .stTabs [data-baseweb="tab"] {{
        font-size: 0.95rem; font-weight: 500; letter-spacing: -0.01em;
        padding: 0.55rem 0.9rem; color: {SUBTLE};
      }}
      .stTabs [aria-selected="true"] {{ color: {INK}; font-weight: 600; }}

      /* ---------- Controls ---------- */
      .stSlider [data-baseweb="slider"] div[role="slider"] {{
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
      }}
      div[data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; }}
      hr.rule {{ border: none; border-top: 1px solid {HAIRLINE}; margin: 2.4rem 0 1.8rem 0; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# PHYSICAL CONSTANTS & WORKBOOK ASSUMPTIONS
# ==========================================================
LB_TO_KG = 0.45359237
MPH_TO_MS = 0.44704
MI_TO_M = 1609.344
G = 9.81                # m/s^2
RHO_AIR = 1.225         # kg/m^3
MJ_PER_KWH = 3.6

# Diesel
DIESEL_LHV = 44.0       # MJ/kg
DIESEL_DENSITY = 0.85   # kg/L
L_PER_GAL = 3.79        # L/gal
ETA_DIESEL = 0.25
EF_DIESEL = 10.18       # kg CO2 / gal

# Hydrogen fuel cell
H2_LHV = 120.0          # MJ/kg
ETA_H2 = 0.50
EF_H2 = 10.50           # kg CO2 / kg H2 (SMR pathway)

# Battery electric
BATT_DENSITY_KWH = 0.16     # kWh/kg  (= 0.576 MJ/kg)
BATT_DENSITY_MJ = BATT_DENSITY_KWH * MJ_PER_KWH
ETA_BEV = 0.90
EF_GRID = 0.394             # kg CO2 / kWh

# Infrastructure readiness (fixed expert scores, Decision Logic sheet)
INFRA = {"Diesel": 100.0, "Hydrogen Fuel Cell": 30.0, "Battery Electric": 60.0}

TECHS = ["Diesel", "Hydrogen Fuel Cell", "Battery Electric"]


def _full_width() -> dict:
    """Streamlit renamed `use_container_width` to `width` in 1.49 — support both."""
    try:
        major, minor = (int(p) for p in st.__version__.split(".")[:2])
    except Exception:
        return {"use_container_width": True}
    return {"width": "stretch"} if (major, minor) >= (1, 49) else {"use_container_width": True}


FULL = _full_width()


# ==========================================================
# WEIGHT BUDGET — hard cap at 100 %
# ==========================================================
WEIGHT_CAP = 100

WEIGHTS = {
    "w_cost": ("Annual fuel cost", 50),
    "w_mass": ("Onboard energy mass", 10),
    "w_eff": ("Energy efficiency", 5),
    "w_infra": ("Infrastructure readiness", 20),
    "w_emis": ("CO₂ emissions", 15),
}

for _key, (_label, _default) in WEIGHTS.items():
    st.session_state.setdefault(_key, _default)


st.session_state.setdefault("_capped", None)


def clamp_weights(changed_key: str) -> None:
    """Keep the five weight sliders from ever summing above 100%.

    Runs before the rerun that redraws the sidebar, so an overshoot is written
    back down to the remaining headroom and the user sees the corrected value.
    """
    others = sum(st.session_state[k] for k in WEIGHTS if k != changed_key)
    headroom = max(WEIGHT_CAP - others, 0)
    if st.session_state[changed_key] > headroom:
        st.session_state[changed_key] = headroom
        st.session_state["_capped"] = WEIGHTS[changed_key][0]
    else:
        st.session_state["_capped"] = None


# ==========================================================
# SIDEBAR — INPUTS
# ==========================================================
with st.sidebar:
    st.markdown(
        f"<div style='font-size:1.15rem;font-weight:600;letter-spacing:-0.02em;'>"
        f"Model inputs</div>"
        f"<div style='font-size:0.86rem;color:{SUBTLE};margin-top:0.15rem;'>"
        f"Duty cycle, prices and decision weights.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='side-group'>Duty cycle</div>", unsafe_allow_html=True)
    route_dist = st.slider("Daily route distance (miles)", 5, 500, 15, step=5)
    operating_days = st.number_input("Operating days per year", 100, 365, 355, step=5)
    avg_speed = st.slider("Average operating speed (mph)", 5, 65, 15, step=1)
    n_stops = st.slider("Stops per day", 0, 400, 100, step=10)
    t_accel = st.slider("Time to reach speed (s)", 2.0, 20.0, 5.0, step=0.5)

    st.markdown("<div class='side-group'>Vehicle</div>", unsafe_allow_html=True)
    curb_weight = st.number_input("Chassis curb weight (lbs)", 10000, 60000, 30000, step=1000)
    payload = st.number_input("Payload requirement (lbs)", 0, 60000, 20000, step=1000)
    cd = st.slider("Drag coefficient  Cd", 0.40, 1.20, 0.90, step=0.01)
    frontal_area = st.slider("Frontal area (m²)", 4.0, 14.0, 10.0, step=0.5)
    crr = st.slider("Rolling resistance  C_rr", 0.004, 0.020, 0.010, step=0.001, format="%.3f")

    st.markdown("<div class='side-group'>Energy prices</div>", unsafe_allow_html=True)
    diesel_price = st.number_input("Diesel ($/gal)", 1.0, 15.0, 5.30, step=0.10)
    h2_price = st.number_input("Hydrogen ($/kg)", 1.0, 60.0, 32.00, step=1.00)
    elec_price = st.number_input("Electricity ($/kWh)", 0.02, 1.00, 0.31, step=0.01)

    st.markdown("<div class='side-group'>Secondary loads</div>", unsafe_allow_html=True)
    aux_pct = st.slider("Auxiliary + cabin HVAC uplift (%)", 0, 40, 0, step=1)
    regen_pct = st.slider("Regenerative braking recovery (%)", 0, 70, 0, step=5)
    st.caption(
        "Regeneration is applied to the electric and fuel-cell hybrid "
        "drivelines only; the diesel baseline has no recovery path."
    )

    st.markdown("<div class='side-group'>Decision weights</div>", unsafe_allow_html=True)
    used = sum(st.session_state[k] for k in WEIGHTS)
    remaining = WEIGHT_CAP - used
    st.markdown(
        f"<div class='budget-track'><div class='budget-fill "
        f"{'full' if remaining == 0 else ''}' style='width:{used}%;'></div></div>"
        f"<div class='budget-text'><b>{used}%</b> allocated · "
        f"<b>{remaining}%</b> left of the 100% budget</div>",
        unsafe_allow_html=True,
    )

    for key, (label, _default) in WEIGHTS.items():
        headroom = WEIGHT_CAP - sum(st.session_state[k] for k in WEIGHTS if k != key)
        st.slider(
            label,
            min_value=0,
            max_value=WEIGHT_CAP,
            step=5,
            key=key,
            on_change=clamp_weights,
            args=(key,),
            help=f"Ceiling is {headroom}% while the other four hold their values. "
                 f"Anything higher snaps back to the remaining budget.",
        )

    if st.session_state["_capped"]:
        st.warning(
            f"Budget full — “{st.session_state['_capped']}” was capped so the five "
            f"weights stay at {WEIGHT_CAP}%. Lower another weight to free up room.",
            icon="⚖️",
        )
    elif remaining > 0:
        st.caption(
            f"{remaining}% of the budget is unallocated. Scores are normalized "
            "to the weight you have assigned, so the scale stays 0–100."
        )

w_cost = st.session_state["w_cost"]
w_mass = st.session_state["w_mass"]
w_eff = st.session_state["w_eff"]
w_infra = st.session_state["w_infra"]
w_emis = st.session_state["w_emis"]


# ==========================================================
# PHYSICS ENGINE
# ==========================================================
gvw_lb = curb_weight + payload
m = gvw_lb * LB_TO_KG                      # kg
v = avg_speed * MPH_TO_MS                  # m/s
d_total = route_dist * MI_TO_M             # m
a = v / t_accel                            # m/s^2

# Stop-start kinetic energy
d_accel_each = 0.5 * v * t_accel           # m per acceleration event
d_accel_total = min(n_stops * d_accel_each, d_total)
d_cruise = max(d_total - d_accel_total, 0.0)

F_accel = m * a                            # N
E_accel = n_stops * 0.5 * m * v**2 / 1e6   # MJ/day

# Aerodynamic drag (acts over the cruise segment)
F_drag = 0.5 * RHO_AIR * frontal_area * cd * v**2   # N
P_drag = F_drag * v                                # W
E_drag = F_drag * d_cruise / 1e6                     # MJ/day

# Rolling resistance (acts over the whole route)
F_rr = crr * m * G                          # N
E_rr = F_rr * d_total / 1e6                 # MJ/day

E_tractive = E_accel + E_drag + E_rr                         # MJ/day, gross
E_recovered = (regen_pct / 100.0) * E_accel                 # MJ/day, hybrids only
aux_factor = 1 + aux_pct / 100.0

E_daily_conv = E_tractive * aux_factor                      # diesel: no regen
E_daily_hybrid = (E_tractive - E_recovered) * aux_factor    # H2 FC + BEV

# --- Tank-to-wheel energy demand -------------------------------------------
E_src_diesel = E_daily_conv / ETA_DIESEL
E_src_h2 = E_daily_hybrid / ETA_H2
E_src_bev = E_daily_hybrid / ETA_BEV

# --- Consumption, cost, emissions, onboard mass -----------------------------
diesel_kg = E_src_diesel / DIESEL_LHV
diesel_L = diesel_kg / DIESEL_DENSITY
diesel_gal = diesel_L / L_PER_GAL
diesel_cost_d = diesel_gal * diesel_price
diesel_co2_d = diesel_gal * EF_DIESEL
diesel_mass_d = diesel_kg

h2_kg = E_src_h2 / H2_LHV
h2_cost_d = h2_kg * h2_price
h2_co2_d = h2_kg * EF_H2
h2_mass_d = h2_kg

bev_kwh = E_src_bev / MJ_PER_KWH
bev_cost_d = bev_kwh * elec_price
bev_co2_d = bev_kwh * EF_GRID
bev_mass_d = bev_kwh / BATT_DENSITY_KWH     # pack sized for one full route

daily_cost = np.array([diesel_cost_d, h2_cost_d, bev_cost_d])
daily_mass = np.array([diesel_mass_d, h2_mass_d, bev_mass_d])
daily_energy = np.array([E_src_diesel, E_src_h2, E_src_bev])
daily_co2 = np.array([diesel_co2_d, h2_co2_d, bev_co2_d])
efficiency = np.array([ETA_DIESEL, ETA_H2, ETA_BEV])

annual_cost = daily_cost * operating_days
annual_energy = daily_energy * operating_days
annual_co2 = daily_co2 * operating_days


# ==========================================================
# SCORING  (ratio normalization, per Decision Logic sheet)
# ==========================================================
def lower_is_better(x: np.ndarray) -> np.ndarray:
    x = np.where(x <= 0, 1e-9, x)
    return x.min() / x * 100.0


def higher_is_better(x: np.ndarray) -> np.ndarray:
    x = np.where(x <= 0, 1e-9, x)
    return x / x.max() * 100.0


s_cost = lower_is_better(annual_cost)
s_mass = lower_is_better(daily_mass)
s_eff = higher_is_better(efficiency)
s_infra = np.array([INFRA[t] for t in TECHS])
s_emis = lower_is_better(annual_co2)

total_w = w_cost + w_mass + w_eff + w_infra + w_emis
denom = total_w if total_w > 0 else 1

composite = (
    s_cost * w_cost
    + s_mass * w_mass
    + s_eff * w_eff
    + s_infra * w_infra
    + s_emis * w_emis
) / denom

best_idx = int(np.argmax(composite))
best_tech = TECHS[best_idx]

RATIONALE = {
    "Diesel": (
        "Diesel wins on infrastructure and onboard energy density: it refuels "
        "anywhere, carries a full shift of energy in a few hundred pounds of fuel, "
        "and needs no depot investment. It pays for that with the worst "
        "tank-to-wheel efficiency and the highest tailpipe CO₂."
    ),
    "Hydrogen Fuel Cell": (
        "Hydrogen delivers the lightest onboard energy storage of the three and "
        "twice the efficiency of diesel, which protects payload on heavy routes. "
        "Its weakness is price per kilogram and a station network that barely exists."
    ),
    "Battery Electric": (
        "Battery electric converts about 90% of stored energy into tractive work, "
        "so the same route costs the least to run and emits the least CO₂ even on "
        "an average grid. The trade-off is pack mass, which eats into payload as "
        "route length grows."
    ),
}

results = pd.DataFrame(
    {
        "Technology": TECHS,
        "Composite score": composite,
        "Annual fuel cost ($)": annual_cost,
        "Daily cost ($)": daily_cost,
        "Annual energy (MJ)": annual_energy,
        "Onboard energy mass (kg)": daily_mass,
        "Annual CO₂ (kg)": annual_co2,
        "Powertrain efficiency": efficiency,
    }
)


# ==========================================================
# HELPERS
# ==========================================================
def score_card(tech: str, score: float, rows: list, winner: bool) -> str:
    color = TECH_COLORS[tech]
    badge = "<span class='badge'>Recommended</span>" if winner else ""
    kvs = "".join(
        f"<div class='kv'><span>{k}</span><span>{val}</span></div>" for k, val in rows
    )
    return f"""
    <div class='score-card {"win" if winner else ""}'>
      <div class='score-tech'>
        <span class='dot' style='background:{color};'></span>{tech}{badge}
      </div>
      <div class='score-value' style='color:{color};'>{score:,.1f}</div>
      <div class='score-sub'>Composite score out of 100</div>
      <div class='bar-track'>
        <div class='bar-fill' style='width:{max(min(score,100),0)}%;background:{color};'></div>
      </div>
      {kvs}
    </div>
    """


# ==========================================================
# HEADER
# ==========================================================
st.markdown(
    "<div class='eyebrow'>Heavy-duty fleet study</div>"
    "<div class='headline'>Three powertrains.<br>One duty cycle.</div>"
    "<div class='subhead'>A physics-first comparison of diesel, hydrogen fuel cell "
    "and battery electric drivelines for an urban municipal truck — built from "
    "tractive-energy demand, not sticker specifications.</div>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["Evaluation", "Equations & methodology", "Technical report"])


# ==========================================================
# TAB 1 — EVALUATION
# ==========================================================
with tab1:
    # ---------- Hero ----------
    hero_l, hero_r = st.columns([2.15, 1])
    with hero_l:
        st.markdown(
            f"<div class='hero' style='margin-right:-1.4rem;'>"
            f"<div class='hero-label'>Recommended powertrain</div>"
            f"<div class='hero-tech' style='color:{TECH_COLORS[best_tech]};'>{best_tech}</div>"
            f"<div class='hero-reason'>{RATIONALE[best_tech]}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with hero_r:
        runner_up = float(np.sort(composite)[-2])
        margin = composite[best_idx] - runner_up
        st.markdown(
            f"<div class='hero' style='margin-left:-1.4rem;'>"
            f"<div class='hero-score' style='color:{TECH_COLORS[best_tech]};'>"
            f"{composite[best_idx]:,.1f}"
            f"<span class='hero-score-unit'>/100</span></div>"
            f"<div class='hero-score-cap'>Composite score · "
            f"+{margin:,.1f} over next best</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ---------- Score cards ----------
    st.markdown(
        "<div class='section-title'>Scorecard</div>"
        "<div class='section-note'>Each criterion is normalized against the best "
        "performer in the set, then weighted by your allocation.</div>",
        unsafe_allow_html=True,
    )

    cards = st.columns(3, gap="medium")
    for i, tech in enumerate(TECHS):
        rows = [
            ("Annual fuel cost", f"${annual_cost[i]:,.0f}"),
            ("Daily cost", f"${daily_cost[i]:,.2f}"),
            ("Onboard energy mass", f"{daily_mass[i]:,.1f} kg"),
            ("Annual CO₂", f"{annual_co2[i]:,.0f} kg"),
            ("Powertrain efficiency", f"{efficiency[i]*100:,.0f}%"),
        ]
        with cards[i]:
            st.markdown(
                score_card(tech, composite[i], rows, i == best_idx),
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    # ---------- Criterion breakdown ----------
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown(
            "<div class='section-title'>Where the score comes from</div>"
            "<div class='section-note'>Weighted contribution of each criterion, "
            "in points of the final 100.</div>",
            unsafe_allow_html=True,
        )
        contrib = pd.DataFrame(
            {
                "Annual fuel cost": s_cost * w_cost / denom,
                "Onboard mass": s_mass * w_mass / denom,
                "Efficiency": s_eff * w_eff / denom,
                "Infrastructure": s_infra * w_infra / denom,
                "CO₂ emissions": s_emis * w_emis / denom,
            },
            index=TECHS,
        )
        palette = ["#0071e3", "#5e5ce6", "#30b158", "#ff9f0a", "#ff453a"]
        fig_c = go.Figure()
        for j, col in enumerate(contrib.columns):
            fig_c.add_bar(
                x=contrib.index,
                y=contrib[col],
                name=col,
                marker_color=palette[j],
                hovertemplate="%{x}<br>" + col + ": %{y:.1f} pts<extra></extra>",
            )
        fig_c.update_layout(
            barmode="stack",
            template="simple_white",
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family="-apple-system, BlinkMacSystemFont, Inter, sans-serif",
                      color=INK, size=12),
            legend=dict(orientation="h", y=-0.18, x=0, title=None),
            yaxis_title="Points",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_c, **FULL)

    with right:
        st.markdown(
            "<div class='section-title'>Daily tractive energy</div>"
            "<div class='section-note'>Work the wheels must deliver, before any "
            "powertrain losses — identical for all three vehicles.</div>",
            unsafe_allow_html=True,
        )
        breakdown = pd.DataFrame(
            {
                "Component": ["Stop–start acceleration", "Aerodynamic drag", "Rolling resistance"],
                "MJ": [E_accel, E_drag, E_rr],
            }
        )
        fig_b = go.Figure(
            go.Bar(
                x=breakdown["MJ"],
                y=breakdown["Component"],
                orientation="h",
                marker_color=["#0071e3", "#5e5ce6", "#30b158"],
                text=[f"{x:,.1f} MJ" for x in breakdown["MJ"]],
                textposition="outside",
                hovertemplate="%{y}: %{x:.2f} MJ<extra></extra>",
            )
        )
        fig_b.update_layout(
            template="simple_white",
            height=380,
            margin=dict(l=10, r=40, t=10, b=10),
            font=dict(family="-apple-system, BlinkMacSystemFont, Inter, sans-serif",
                      color=INK, size=12),
            xaxis_title="MJ per day",
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_b, **FULL)

        st.markdown(
            f"<div class='card' style='padding:1.1rem 1.4rem;'>"
            f"<div class='kv'><span>Gross vehicle weight</span>"
            f"<span>{gvw_lb:,.0f} lb · {m:,.0f} kg</span></div>"
            f"<div class='kv'><span>Drag force at speed</span>"
            f"<span>{F_drag:,.1f} N</span></div>"
            f"<div class='kv'><span>Rolling resistance force</span>"
            f"<span>{F_rr:,.1f} N</span></div>"
            f"<div class='kv'><span>Acceleration force per event</span>"
            f"<span>{F_accel:,.0f} N</span></div>"
            f"<div class='kv'><span>Daily tractive work</span>"
            f"<span>{E_tractive:,.1f} MJ</span></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    # ---------- Ten-year cost ----------
    st.markdown(
        "<div class='section-title'>Ten-year cumulative energy spend</div>"
        "<div class='section-note'>Fuel and electricity only. Vehicle purchase "
        "price, depot charging capital and maintenance are outside this model.</div>",
        unsafe_allow_html=True,
    )
    years = np.arange(0, 11)
    fig_t = go.Figure()
    for i, tech in enumerate(TECHS):
        fig_t.add_trace(
            go.Scatter(
                x=years,
                y=years * annual_cost[i],
                name=tech,
                mode="lines",
                line=dict(color=TECH_COLORS[tech], width=3, shape="spline"),
                hovertemplate="Year %{x}<br>" + tech + ": $%{y:,.0f}<extra></extra>",
            )
        )
    fig_t.update_layout(
        template="simple_white",
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="-apple-system, BlinkMacSystemFont, Inter, sans-serif",
                  color=INK, size=12),
        legend=dict(orientation="h", y=1.08, x=0, title=None),
        xaxis_title="Year",
        yaxis_title="Cumulative cost ($)",
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_t, **FULL)

    with st.expander("Full results table"):
        st.dataframe(
            results.style.format(
                {
                    "Composite score": "{:,.1f}",
                    "Annual fuel cost ($)": "${:,.0f}",
                    "Daily cost ($)": "${:,.2f}",
                    "Annual energy (MJ)": "{:,.0f}",
                    "Onboard energy mass (kg)": "{:,.1f}",
                    "Annual CO₂ (kg)": "{:,.0f}",
                    "Powertrain efficiency": "{:.0%}",
                }
            ),
            **FULL,
            hide_index=True,
        )
        st.download_button(
            "Download results as CSV",
            results.to_csv(index=False).encode("utf-8"),
            file_name="powertrain_evaluation.csv",
            mime="text/csv",
        )


# ==========================================================
# TAB 2 — EQUATIONS & METHODOLOGY
# ==========================================================
with tab2:
    st.markdown(
        "<div class='section-title'>How the model works</div>"
        "<div class='section-note'>The model runs in four stages: resolve the "
        "tractive energy the route demands, divide by each powertrain's efficiency "
        "to get energy at the source, convert that into fuel, cost and CO₂, then "
        "score the three options against one another.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class='card'>
          <div style='display:flex;flex-wrap:wrap;gap:1.6rem;font-size:0.92rem;'>
            <div><b>Stage 1</b><br><span style='color:{SUBTLE};'>Road load → wheel energy</span></div>
            <div style='color:{HAIRLINE};'>→</div>
            <div><b>Stage 2</b><br><span style='color:{SUBTLE};'>Wheel energy ÷ efficiency</span></div>
            <div style='color:{HAIRLINE};'>→</div>
            <div><b>Stage 3</b><br><span style='color:{SUBTLE};'>Energy → fuel, cost, CO₂</span></div>
            <div style='color:{HAIRLINE};'>→</div>
            <div><b>Stage 4</b><br><span style='color:{SUBTLE};'>Normalize and weight</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- Stage 1 ----------
    st.markdown(
        "<div class='section-title' style='margin-top:1.6rem;'>Stage 1 — Road load</div>"
        "<div class='section-note'>Three resistances consume energy on an urban "
        "refuse route. Grade is neglected: the modeled route returns to its "
        "starting elevation, so net potential energy is zero.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 01</div>"
            "<div class='eq-title'>Gross vehicle mass</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"m = \left(m_{\text{curb}} + m_{\text{payload}}\right)\times 0.45359237")
        st.markdown(
            f"<div class='eq-body'>Curb weight plus payload, converted from pounds "
            f"to kilograms. Mass drives both rolling resistance and stop–start "
            f"energy, which is why it is resolved first.<br>"
            f"<b>Current run: {gvw_lb:,.0f} lb → {m:,.0f} kg</b></div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 02</div>"
            "<div class='eq-title'>Rolling resistance</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"F_{rr} = C_{rr} \cdot m \cdot g")
        st.latex(r"E_{rr} = \frac{F_{rr} \cdot d_{\text{total}}}{10^6}")
        st.markdown(
            f"<div class='eq-body'>Acts over the full daily distance "
            f"<b>d_total = {d_total/1000:,.1f} km</b>.<br>"
            f"<b>Current run: {F_rr:,.1f} N → {E_rr:,.1f} MJ/day</b></div></div>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 03</div>"
            "<div class='eq-title'>Aerodynamic drag</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"F_{\text{drag}} = \frac{1}{2} \cdot \rho \cdot A \cdot C_d \cdot v^2")
        st.latex(r"E_{\text{drag}} = \frac{F_{\text{drag}} \cdot d_{\text{cruise}}}{10^6}")
        st.markdown(
            f"<div class='eq-body'>Acts over cruise distance "
            f"<b>d_cruise = {d_cruise/1000:,.1f} km</b>.<br>"
            f"<b>Current run: {F_drag:,.1f} N → {E_drag:,.1f} MJ/day</b></div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 04</div>"
            "<div class='eq-title'>Stop–start kinetic energy</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"E_{\text{accel}} = \frac{N_{\text{stops}} \cdot \frac{1}{2} \cdot m \cdot v^2}{10^6}")
        st.markdown(
            f"<div class='eq-body'>Kinetic energy transferred to the vehicle over "
            f"<b>N_stops = {n_stops}</b> acceleration cycles to <b>v = {avg_speed} mph ({v:,.2f} m/s)</b>.<br>"
            f"<b>Current run: {E_accel:,.1f} MJ/day</b></div></div>",
            unsafe_allow_html=True,
        )


# ==========================================================
# TAB 3 — TECHNICAL REPORT
# ==========================================================
with tab3:
    st.markdown(
        "<div class='section-title'>Technical Assessment & Methodology Summary</div>"
        "<div class='section-note'>Detailed analysis of findings, assumptions, and technology pathways.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        ### Executive Summary
        This evaluation model evaluates heavy-duty vehicle decarbonization pathways using first-principles physics.
        By isolating tractive energy requirements from fuel delivery mechanics, the model provides an objective baseline 
        for assessing **Diesel**, **Hydrogen Fuel Cell**, and **Battery Electric** powertrains.

        ### Key Findings for Current Parameters
        * **Tractive Demand:** The route requires **{E_tractive:,.1f} MJ/day** of net tractive energy at the wheels.
        * **Energy Leader:** **{best_tech}** scored highest overall with a composite score of **{composite[best_idx]:,.1f}/100**.
        * **Cost Comparison:** Annual energy expenditure spans from **${annual_cost.min():,.0f}** to **${annual_cost.max():,.0f}**.
        * **Emissions Reduction:** Transitioning from Diesel to Electric pathways reduces annual operational CO₂ by up to **{((annual_co2[0] - annual_co2.min()) / annual_co2[0] * 100) if annual_co2[0] > 0 else 0:,.1f}%**.
        """
    )
