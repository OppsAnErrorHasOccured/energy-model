import base64
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Powertrain Energy Model",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# DESIGN TOKENS & SAMURAI BLUE / MUTED PASTEL PALETTE
# ==========================================================
C_DIESEL = "#6C757D"  # Muted Slate
C_HYDROGEN = "#1D3557"  # Samurai Blue
C_BATTERY = "#386641"  # Deep Muted Sage

# Muted Pastel / Darker Palette (Samurai Blue base)
PALETTE = [
    "#1D3557",  # Samurai Blue
    "#386641",  # Muted Sage Green
    "#6A4C93",  # Deep Muted Plum/Purple
    "#D97706",  # Muted Amber / Ochre
    "#C1121F",  # Muted Dark Coral / Red
]

FONT_FAMILY = (
    "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text',"
    " 'Helvetica Neue', sans-serif"
)

TECH_COLORS = {
    "Diesel": C_DIESEL,
    "Hydrogen Fuel Cell": C_HYDROGEN,
    "Battery Electric": C_BATTERY,
}

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

      :root {{
        --ink: #1d1d1f;
        --subtle: #6e6e73;
        --hairline: #e2e8f0;
        --canvas: #f8fafc;
        --surface: #ffffff;
        --accent: #1D3557;
        --hero-bg: linear-gradient(160deg, #ffffff 0%, #f0f4fb 100%);
        --shadow: rgba(0, 0, 0, 0.05);
        --plot-bg: #ffffff;
      }}

      @media (prefers-color-scheme: dark) {{
        :root {{
          --ink: #f0f4f8;
          --subtle: #94a3b8;
          --hairline: #1e293b;
          --canvas: #0b1320;
          --surface: #131c2e;
          --accent: #457b9d;
          --hero-bg: linear-gradient(160deg, #182338 0%, #0f172a 100%);
          --shadow: rgba(0, 0, 0, 0.3);
          --plot-bg: #131c2e;
        }}
      }}

      html, body, [class*="css"], .stApp {{
        font-family: {FONT_FAMILY};
        color: var(--ink);
      }}

      .stApp {{ background: var(--canvas); }}

      .block-container {{
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        max-width: 1320px;
      }}

      header[data-testid="stHeader"] {{
        background: transparent !important;
        z-index: 99999 !important;
      }}
      
      #MainMenu, footer, [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{
        visibility: hidden !important;
        display: none !important;
      }}

      [data-testid="stSidebarCollapsedControl"], 
      [data-testid="stSidebarExpandButton"] {{
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        color: var(--ink) !important;
      }}

      .eyebrow {{
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.09em;
        text-transform: uppercase; color: var(--subtle); margin-bottom: 0.55rem;
      }}
      .headline {{
        font-size: 3.15rem; font-weight: 600; letter-spacing: -0.028em;
        line-height: 1.05; color: var(--ink); margin: 0 0 0.55rem 0;
      }}
      .subhead {{
        font-size: 1.16rem; font-weight: 400; color: var(--subtle);
        letter-spacing: -0.01em; line-height: 1.5; max-width: 62ch; margin-bottom: 2.1rem;
      }}
      .section-title {{
        font-size: 1.55rem; font-weight: 600; letter-spacing: -0.02em;
        color: var(--ink); margin: 0 0 0.25rem 0;
      }}
      .section-note {{
        font-size: 0.95rem; color: var(--subtle); margin-bottom: 1.1rem;
      }}

      .card {{
        background: var(--surface); border-radius: 20px; padding: 1.6rem 1.75rem;
        border: 1px solid var(--hairline); box-shadow: 0 4px 20px var(--shadow); margin-bottom: 1.1rem;
      }}

      .hero {{
        background: var(--hero-bg); border-radius: 26px; padding: 2.1rem 2.3rem 1.9rem 2.3rem;
        border: 1px solid var(--hairline); box-shadow: 0 10px 30px var(--shadow); margin-bottom: 1.35rem;
      }}
      .hero-label {{
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.1em;
        text-transform: uppercase; color: var(--subtle);
      }}
      .hero-tech {{
        font-size: 2.55rem; font-weight: 600; letter-spacing: -0.03em;
        line-height: 1.1; margin: 0.35rem 0 0.15rem 0;
      }}
      .hero-reason {{
        font-size: 1.0rem; color: var(--subtle); line-height: 1.55;
        max-width: 52ch; margin-top: 0.5rem;
      }}
      .hero-score {{
        font-size: 5.6rem; font-weight: 600; letter-spacing: -0.045em;
        line-height: 0.92; text-align: right;
      }}
      .hero-score-unit {{
        font-size: 1.6rem; font-weight: 500; color: var(--subtle); letter-spacing: -0.02em;
      }}
      .hero-score-cap {{
        text-align: right; font-size: 0.78rem; font-weight: 600;
        letter-spacing: 0.1em; text-transform: uppercase; color: var(--subtle); margin-top: 0.45rem;
      }}

      .score-card {{
        background: var(--surface); border-radius: 20px; padding: 1.35rem 1.5rem 1.5rem 1.5rem;
        border: 1px solid var(--hairline); box-shadow: 0 4px 20px var(--shadow); height: 100%;
      }}
      .score-card.win {{ box-shadow: 0 0 0 2px var(--accent), 0 10px 30px var(--shadow); }}
      .score-tech {{
        font-size: 1.02rem; font-weight: 600; letter-spacing: -0.01em;
        color: var(--ink); display: flex; align-items: center; gap: 0.5rem;
      }}
      .dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; }}
      .score-value {{
        font-size: 3.3rem; font-weight: 600; letter-spacing: -0.04em;
        line-height: 1.05; margin-top: 0.5rem;
      }}
      .score-sub {{ font-size: 0.83rem; color: var(--subtle); letter-spacing: 0.01em; }}
      .bar-track {{
        height: 6px; border-radius: 99px; background: var(--hairline);
        margin: 0.95rem 0 0.85rem 0; overflow: hidden;
      }}
      .bar-fill {{ height: 6px; border-radius: 99px; }}
      .kv {{
        display: flex; justify-content: space-between;
        font-size: 0.88rem; padding: 0.28rem 0; border-bottom: 1px solid var(--hairline);
      }}
      .kv:last-child {{ border-bottom: none; }}
      .kv span:first-child {{ color: var(--subtle); }}
      .kv span:last-child {{ font-weight: 500; color: var(--ink); font-variant-numeric: tabular-nums; }}
      .score-card.out {{ opacity: 0.5; }}
      .badge.fail {{ background: #C1121F; }}
      .kv span.warn {{ color: #C1121F; font-weight: 600; }}
      .badge {{
        display: inline-block; background: var(--accent); color: #ffffff;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.07em;
        text-transform: uppercase; padding: 0.2rem 0.55rem; border-radius: 99px; margin-left: 0.4rem;
      }}

      .budget-track {{
        height: 8px; border-radius: 99px; background: var(--hairline);
        overflow: hidden; margin: 0.4rem 0 0.35rem 0;
      }}
      .budget-fill {{ height: 8px; border-radius: 99px; background: var(--accent); }}
      .budget-fill.full {{ background: #386641; }}
      .budget-text {{ font-size: 0.82rem; color: var(--subtle); }}

      .eq-card {{
        background: var(--surface); border-radius: 18px; padding: 1.35rem 1.5rem;
        border: 1px solid var(--hairline); box-shadow: 0 4px 15px var(--shadow); margin-bottom: 1rem;
      }}
      .eq-num {{
        font-size: 0.74rem; font-weight: 600; letter-spacing: 0.1em;
        color: var(--accent); text-transform: uppercase;
      }}
      .eq-title {{
        font-size: 1.12rem; font-weight: 600; letter-spacing: -0.015em;
        color: var(--ink); margin: 0.2rem 0 0.15rem 0;
      }}
      .eq-body {{ font-size: 0.9rem; color: var(--subtle); line-height: 1.6; }}
      .eq-body b {{ color: var(--ink); font-weight: 500; }}

      [data-testid="stSidebar"] {{
        background: var(--surface); border-right: 1px solid var(--hairline);
      }}
      [data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}
      .derived {{
        display: flex; justify-content: space-between; align-items: baseline;
        background: var(--canvas); border-radius: 10px; padding: 0.45rem 0.7rem; margin-top: 0.4rem;
        font-size: 0.83rem; color: var(--subtle);
      }}
      .derived b {{ color: var(--ink); font-variant-numeric: tabular-nums; font-weight: 600; }}
      .derived i {{ color: var(--accent); font-style: normal; font-weight: 500; }}

      .side-group {{
        font-size: 0.74rem; font-weight: 600; letter-spacing: 0.1em;
        text-transform: uppercase; color: var(--subtle); margin: 1.35rem 0 0.35rem 0;
      }}

      .stTabs [data-baseweb="tab-list"] {{
        gap: 0.35rem; border-bottom: 1px solid var(--hairline);
      }}
      .stTabs [data-baseweb="tab"] {{
        font-size: 0.95rem; font-weight: 500; letter-spacing: -0.01em;
        padding: 0.55rem 0.9rem; color: var(--subtle);
      }}
      .stTabs [aria-selected="true"] {{ color: var(--ink); font-weight: 600; border-bottom-color: var(--accent) !important; }}

      .stSlider [data-baseweb="slider"] div[role="slider"] {{
        box-shadow: 0 1px 4px var(--shadow);
      }}
      div[data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; border: 1px solid var(--hairline); }}
      hr.rule {{ border: none; border-top: 1px solid var(--hairline); margin: 2.4rem 0 1.8rem 0; }}
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
G = 9.81
RHO_AIR = 1.225
MJ_PER_KWH = 3.6

DIESEL_LHV = 44.0
DIESEL_DENSITY = 0.85
L_PER_GAL = 3.79
ETA_DIESEL = 0.25
EF_DIESEL = 10.18

H2_LHV = 120.0
ETA_H2 = 0.50
EF_H2 = 10.50

BATT_DENSITY_KWH = 0.16
BATT_DENSITY_MJ = BATT_DENSITY_KWH * MJ_PER_KWH
ETA_BEV = 0.90
EF_GRID = 0.394

INFRA = {"Diesel": 100.0, "Hydrogen Fuel Cell": 30.0, "Battery Electric": 60.0}
TECHS = ["Diesel", "Hydrogen Fuel Cell", "Battery Electric"]


def _full_width() -> dict:
  try:
    major, minor = (int(p) for p in st.__version__.split(".")[:2])
  except Exception:
    return {"use_container_width": True}
  return (
      {"width": "stretch"}
      if (major, minor) >= (1, 49)
      else {"use_container_width": True}
  )


FULL = _full_width()

WEIGHT_CAP = 100
WEIGHTS = {
    "w_cost": ("Annual fuel cost", 50),
    "w_mass": ("Usable payload", 10),
    "w_eff": ("Energy efficiency", 5),
    "w_infra": ("Infrastructure readiness", 20),
    "w_emis": ("CO₂ emissions", 15),
}

for _key, (_label, _default) in WEIGHTS.items():
  st.session_state.setdefault(_key, _default)

st.session_state.setdefault("_capped", None)


def clamp_weights(changed_key: str) -> None:
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
      "<div style='font-size:1.15rem;font-weight:600;letter-spacing:-0.02em;color:var(--ink);'>"
      "Model inputs</div>"
      "<div style='font-size:0.86rem;color:var(--subtle);margin-top:0.15rem;'>"
      "Set the route, the prices and what matters to you. Everything else "
      "lives under Advanced settings.</div>",
      unsafe_allow_html=True,
  )

  st.markdown("<div class='side-group'>Route</div>", unsafe_allow_html=True)
  route_dist = st.slider("Daily route distance (miles)", 5, 500, 15, step=5)
  operating_days = st.number_input(
      "Operating days per year", 100, 365, 355, step=5
  )
  n_stops = st.slider("Stops per day", 0, 400, 100, step=10)

  st.markdown(
      "<div class='side-group'>Energy prices</div>", unsafe_allow_html=True
  )
  diesel_price = st.number_input("Diesel ($/gal)", 1.0, 15.0, 5.30, step=0.10)
  h2_price = st.number_input("Hydrogen ($/kg)", 1.0, 60.0, 33.00, step=1.00)
  elec_price = st.number_input("Electricity ($/kWh)", 0.02, 1.00, 0.31, step=0.01)

  with st.expander("Advanced settings"):
    st.caption(
        "Vehicle geometry, road-load coefficients and secondary loads. "
        "Defaults describe a typical urban municipal truck — leave them as "
        "they are for a standard run."
    )

    st.markdown("<div class='side-group'>Vehicle</div>", unsafe_allow_html=True)
    avg_speed = st.slider("Average operating speed (mph)", 5, 65, 15, step=1)
    curb_weight = st.number_input(
        "Chassis curb weight (lbs)", 10000, 60000, 30000, step=1000
    )
    payload = st.number_input(
        "Payload requirement (lbs)", 0, 60000, 20000, step=1000
    )
    gvwr = st.number_input(
        "GVWR — max legal gross weight (lbs)", 20000, 90000, 66000, step=1000
    )

    st.markdown(
        "<div class='side-group'>Energy storage</div>", unsafe_allow_html=True
    )
    h2_grav = st.slider(
        "H₂ tank system capacity (% H₂ by mass)", 2.0, 10.0, 5.7, step=0.1
    )
    pack_factor = st.slider(
        "Battery pack integration factor", 0.50, 1.00, 0.70, step=0.01
    )
    dod = st.slider("Usable depth of discharge (%)", 50, 100, 90, step=5)
    diesel_tank_pct = st.slider(
        "Diesel tank + hardware (% of fuel mass)", 0, 60, 20, step=5
    )

    st.markdown(
        "<div class='side-group'>Road load</div>", unsafe_allow_html=True
    )
    cd = st.slider("Drag coefficient Cd", 0.40, 1.20, 0.90, step=0.01)
    frontal_area = st.slider("Frontal area (m²)", 4.0, 14.0, 10.0, step=0.5)
    crr = st.slider(
        "Rolling resistance C_rr",
        0.004,
        0.020,
        0.010,
        step=0.001,
        format="%.3f",
    )

    st.markdown(
        "<div class='side-group'>Launch behavior</div>", unsafe_allow_html=True
    )
    accel_rate = st.slider(
        "Acceleration rate (m/s²)", 0.30, 3.00, 1.36, step=0.02
    )
    _v_ms = avg_speed * MPH_TO_MS
    t_accel = _v_ms / accel_rate

    st.markdown(
        "<div class='side-group'>Secondary loads</div>", unsafe_allow_html=True
    )
    aux_pct = st.slider("Auxiliary + cabin HVAC uplift (%)", 0, 40, 0, step=1)
    regen_pct = st.slider(
        "Regenerative braking recovery (%)", 0, 70, 0, step=5
    )

  st.markdown(
      "<div class='side-group'>Decision weights</div>", unsafe_allow_html=True
  )
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
    headroom = WEIGHT_CAP - sum(
        st.session_state[k] for k in WEIGHTS if k != key
    )
    st.slider(
        label,
        min_value=0,
        max_value=WEIGHT_CAP,
        step=5,
        key=key,
        on_change=clamp_weights,
        args=(key,),
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
m = gvw_lb * LB_TO_KG
v = avg_speed * MPH_TO_MS
d_total = route_dist * MI_TO_M
a = accel_rate

d_accel_each = 0.5 * v * t_accel
d_accel_total = min(n_stops * d_accel_each, d_total)
d_cruise = max(d_total - d_accel_total, 0.0)

F_accel = m * a
E_accel = n_stops * 0.5 * m * v**2 / 1e6
F_drag = 0.5 * RHO_AIR * frontal_area * cd * v**2
P_drag = F_drag * v
E_drag = F_drag * d_cruise / 1e6
F_rr = crr * m * G
E_rr = F_rr * d_total / 1e6

E_tractive = E_accel + E_drag + E_rr
E_recovered = (regen_pct / 100.0) * E_accel
aux_factor = 1 + aux_pct / 100.0

E_daily_conv = E_tractive * aux_factor
E_daily_hybrid = (E_tractive - E_recovered) * aux_factor

E_src_diesel = E_daily_conv / ETA_DIESEL
E_src_h2 = E_daily_hybrid / ETA_H2
E_src_bev = E_daily_hybrid / ETA_BEV

diesel_kg = E_src_diesel / DIESEL_LHV
diesel_L = diesel_kg / DIESEL_DENSITY
diesel_gal = diesel_L / L_PER_GAL
diesel_cost_d = diesel_gal * diesel_price
diesel_co2_d = diesel_gal * EF_DIESEL
diesel_sys = diesel_kg * (1 + diesel_tank_pct / 100.0)

h2_kg = E_src_h2 / H2_LHV
h2_cost_d = h2_kg * h2_price
h2_co2_d = h2_kg * EF_H2
h2_sys = h2_kg / (h2_grav / 100.0)

bev_kwh = E_src_bev / MJ_PER_KWH
bev_cost_d = bev_kwh * elec_price
bev_co2_d = bev_kwh * EF_GRID
bev_nameplate_kwh = bev_kwh / (dod / 100.0)
bev_sys = bev_nameplate_kwh / (BATT_DENSITY_KWH * pack_factor)

daily_cost = np.array([diesel_cost_d, h2_cost_d, bev_cost_d])
fuel_mass = np.array([diesel_kg, h2_kg, bev_kwh / BATT_DENSITY_KWH])
system_mass = np.array([diesel_sys, h2_sys, bev_sys])
daily_energy = np.array([E_src_diesel, E_src_h2, E_src_bev])
daily_co2 = np.array([diesel_co2_d, h2_co2_d, bev_co2_d])
efficiency = np.array([ETA_DIESEL, ETA_H2, ETA_BEV])

annual_cost = daily_cost * operating_days
annual_energy = daily_energy * operating_days
annual_co2 = daily_co2 * operating_days

rated_capacity_kg = max((gvwr - curb_weight) * LB_TO_KG, 0.0)
usable_payload = rated_capacity_kg - system_mass
required_payload = payload * LB_TO_KG
feasible = usable_payload >= required_payload
payload_used_pct = np.where(
    rated_capacity_kg > 0, system_mass / rated_capacity_kg * 100.0, 100.0
)
any_feasible = bool(feasible.any())


# ==========================================================
# SCORING
# ==========================================================
def lower_is_better(x: np.ndarray) -> np.ndarray:
  x = np.where(x <= 0, 1e-9, x)
  return x.min() / x * 100.0


def higher_is_better(x: np.ndarray) -> np.ndarray:
  x = np.where(x <= 0, 1e-9, x)
  return x / x.max() * 100.0


s_cost = lower_is_better(annual_cost)
s_mass = np.where(feasible, higher_is_better(np.maximum(usable_payload, 0.0)), 0.0)
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

eligible = (
    composite if not any_feasible else np.where(feasible, composite, -np.inf)
)
best_idx = int(np.argmax(eligible))
best_tech = TECHS[best_idx]

RATIONALE = {
    "Diesel": (
        "Diesel wins on infrastructure and onboard energy density: it refuels"
        " anywhere, carries a full shift of energy in a few hundred pounds of"
        " fuel and tank, and needs no depot investment. It pays for that with"
        " the worst tank-to-wheel efficiency and the highest tailpipe CO₂."
    ),
    "Hydrogen Fuel Cell": (
        "Hydrogen holds its payload better than a battery on long routes — the"
        " 700-bar tank is heavy, but it grows far more slowly with distance than"
        " a pack does. Its weakness is price per kilogram and a station network"
        " that barely exists."
    ),
    "Battery Electric": (
        "Battery electric converts about 90% of stored energy into tractive"
        " work, so this route costs the least to run and emits the least CO₂"
        " even on an average grid. The trade-off is pack mass, which displaces"
        " cargo as route length grows."
    ),
}

results = pd.DataFrame({
    "Technology": TECHS,
    "Composite score": composite,
    "Annual fuel cost ($)": annual_cost,
    "Daily cost ($)": daily_cost,
    "Annual energy (MJ)": annual_energy,
    "Energy system mass (kg)": system_mass,
    "Usable payload (kg)": usable_payload,
    "Payload capacity used (%)": payload_used_pct,
    "Route feasible": np.where(feasible, "Yes", "No"),
    "Annual CO₂ (kg)": annual_co2,
    "Powertrain efficiency": efficiency,
})


def score_card(
    tech: str, score: float, rows: list, winner: bool, ok: bool = True
) -> str:
  color = TECH_COLORS[tech] if ok else "var(--subtle)"
  badge = "<span class='badge'>Recommended</span>" if winner else ""
  if not ok:
    badge = "<span class='badge fail'>Payload short</span>"
  kvs = "".join(
      f"<div class='kv'><span>{k}</span><span>{val}</span></div>" for k, val in rows
  )
  return f"""
    <div class='score-card {"win" if winner else ""} {"" if ok else "out"}'>
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
    "<div class='eyebrow'>Urban municipal truck · duty-cycle study</div>"
    "<div class='headline'>Powertrain<br>Energy Model</div>"
    "<div class='subhead'>A physics-driven analysis of diesel, hydrogen"
    " fuel-cell, and battery-electric drivetrains – based on tractive energy"
    " requirements, not spec sheets. Pick a route and costs to get your answer;"
    " click the Advanced button to alter the car’s specifications.</div>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(
    ["Evaluation", "Equations & methodology", "Technical report"]
)

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
        f"<div class='hero-tech'"
        f" style='color:{TECH_COLORS[best_tech]};'>{best_tech}</div>"
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

  # ---------- SCORECARD SECTION (MOVED ABOVE CHARTS) ----------
  st.markdown(
      "<div class='section-title'>Scorecard</div>"
      "<div class='section-note'>Each criterion is normalized against the best "
      "performer in the set, then weighted by your allocation.</div>",
      unsafe_allow_html=True,
  )

  cards = st.columns(3, gap="medium")
  for i, tech in enumerate(TECHS):
    pay_txt = f"{usable_payload[i]:,.0f} kg"
    if not feasible[i]:
      pay_txt = f"<span class='warn'>{usable_payload[i]:,.0f} kg</span>"
    rows = [
        ("Annual fuel cost", f"${annual_cost[i]:,.0f}"),
        ("Daily cost", f"${daily_cost[i]:,.2f}"),
        ("Energy system mass", f"{system_mass[i]:,.0f} kg"),
        ("Payload left", pay_txt),
        ("Capacity used by energy", f"{payload_used_pct[i]:,.1f}%"),
        ("Annual CO₂", f"{annual_co2[i]:,.0f} kg"),
        ("Powertrain efficiency", f"{efficiency[i]*100:,.0f}%"),
    ]
    with cards[i]:
      st.markdown(
          score_card(
              tech, composite[i], rows, i == best_idx, bool(feasible[i])
          ),
          unsafe_allow_html=True,
      )

  if not feasible.all():
    blocked = ", ".join(t for t, ok in zip(TECHS, feasible) if not ok)
    st.warning(
        f"{blocked} cannot complete this route with the required "
        f"{required_payload:,.0f} kg payload — the energy system alone exceeds "
        f"the {rated_capacity_kg:,.0f} kg the chassis has left under its GVWR. "
        "It scores zero on payload and is barred from the recommendation.",
        icon="⚠️",
    )

  st.markdown("<hr class='rule'>", unsafe_allow_html=True)

  # ---------- CHARTS SECTION ----------
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
            "Usable payload": s_mass * w_mass / denom,
            "Efficiency": s_eff * w_eff / denom,
            "Infrastructure": s_infra * w_infra / denom,
            "CO₂ emissions": s_emis * w_emis / denom,
        },
        index=TECHS,
    )

    fig_c = go.Figure()
    for j, col in enumerate(contrib.columns):
      fig_c.add_bar(
          x=contrib.index,
          y=contrib[col],
          name=col,
          marker_color=PALETTE[j % len(PALETTE)],
          hovertemplate="%{x}<br>" + col + ": %{y:.1f} pts<extra></extra>",
      )
    fig_c.update_layout(
        barmode="stack",
        template="none",
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family=FONT_FAMILY, size=12),
        hoverlabel=dict(font=dict(family=FONT_FAMILY, size=13)),
        legend=dict(orientation="h", y=-0.18, x=0, title=None),
        xaxis=dict(gridcolor="rgba(150,150,150,0.15)"),
        yaxis=dict(title="Points", gridcolor="rgba(150,150,150,0.15)"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_c, **FULL)

  with right:
    st.markdown(
        "<div class='section-title'>Daily tractive energy</div>"
        "<div class='section-note'>Work the wheels must deliver, before any "
        "powertrain losses — identical for all three vehicles.</div>",
        unsafe_allow_html=True,
    )
    breakdown = pd.DataFrame({
        "Component": [
            "Stop–start acceleration",
            "Aerodynamic drag",
            "Rolling resistance",
        ],
        "MJ": [E_accel, E_drag, E_rr],
    })
    fig_b = go.Figure(
        go.Bar(
            x=breakdown["MJ"],
            y=breakdown["Component"],
            orientation="h",
            marker_color=[PALETTE[0], PALETTE[2], PALETTE[1]],
            text=[f"{x:,.1f} MJ" for x in breakdown["MJ"]],
            textposition="outside",
            hovertemplate="%{y}: %{x:.2f} MJ<extra></extra>",
        )
    )
    fig_b.update_layout(
        template="none",
        height=380,
        margin=dict(l=10, r=40, t=10, b=10),
        font=dict(family=FONT_FAMILY, size=12),
        hoverlabel=dict(font=dict(family=FONT_FAMILY, size=13)),
        xaxis=dict(title="MJ per day", gridcolor="rgba(150,150,150,0.15)"),
        yaxis=dict(gridcolor="rgba(150,150,150,0.15)"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
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

  # ---------- Payload vs route length ----------
  st.markdown(
      "<div class='section-title'>How far the route can stretch</div>"
      "<div class='section-note'>Cargo capacity left after the energy system "
      "takes its share, as the route grows. Where a line crosses the required "
      "payload, that powertrain can no longer do the job.</div>",
      unsafe_allow_html=True,
  )

  sweep_mi = np.linspace(5, max(route_dist * 3, 120), 60)
  fig_p = go.Figure()
  for i, tech in enumerate(TECHS):
    ys = []
    for mi in sweep_mi:
      scale = mi / route_dist if route_dist > 0 else 1.0
      d_m = mi * MI_TO_M
      d_cr_s = max(d_m - min(n_stops * d_accel_each, d_m), 0.0)
      e_acc = n_stops * 0.5 * m * v**2 / 1e6
      e_dr = F_drag * d_cr_s / 1e6
      e_rr = F_rr * d_m / 1e6
      e_t = e_acc + e_dr + e_rr
      conv = e_t * aux_factor
      hyb = (e_t - (regen_pct / 100.0) * e_acc) * aux_factor
      if tech == "Diesel":
        sys_m = (conv / ETA_DIESEL / DIESEL_LHV) * (1 + diesel_tank_pct / 100.0)
      elif tech == "Hydrogen Fuel Cell":
        sys_m = (hyb / ETA_H2 / H2_LHV) / (h2_grav / 100.0)
      else:
        kwh = hyb / ETA_BEV / MJ_PER_KWH / (dod / 100.0)
        sys_m = kwh / (BATT_DENSITY_KWH * pack_factor)
      ys.append(rated_capacity_kg - sys_m)
    fig_p.add_trace(
        go.Scatter(
            x=sweep_mi,
            y=ys,
            name=tech,
            mode="lines",
            line=dict(color=TECH_COLORS[tech], width=3),
            hovertemplate=(
                "%{x:.0f} mi<br>" + tech + ": %{y:,.0f} kg left<extra></extra>"
            ),
        )
    )
  fig_p.add_hline(
      y=required_payload,
      line_dash="dash",
      line_color="#C1121F",
      annotation_text=f"Required payload — {required_payload:,.0f} kg",
      annotation_position="bottom right",
  )
  fig_p.add_vline(
      x=route_dist,
      line_dash="dot",
      line_color="#6C757D",
      annotation_text="Your route",
      annotation_position="top left",
  )
  fig_p.update_layout(
      template="none",
      height=420,
      margin=dict(l=10, r=10, t=30, b=10),
      font=dict(family=FONT_FAMILY, size=12),
      hoverlabel=dict(font=dict(family=FONT_FAMILY, size=13)),
      legend=dict(orientation="h", y=1.12, x=0, title=None),
      xaxis=dict(
          title="Daily route distance (miles)",
          gridcolor="rgba(150,150,150,0.15)",
      ),
      yaxis=dict(
          title="Payload capacity remaining (kg)",
          gridcolor="rgba(150,150,150,0.15)",
      ),
      hovermode="x unified",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
  )
  st.plotly_chart(fig_p, **FULL)

  st.markdown("<hr class='rule'>", unsafe_allow_html=True)

  # ---------- Ten-year cost ----------
  st.markdown(
      "<div class='section-title'>Ten-year cumulative energy spend</div>"
      "<div class='section-note'>Fuel and electricity only. Vehicle purchase "
      "price, depot charging capital and maintenance are outside this"
      " model.</div>",
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
            hovertemplate=(
                "Year %{x}<br>" + tech + ": $%{y:,.0f}<extra></extra>"
            ),
        )
    )
  fig_t.update_layout(
      template="none",
      height=420,
      margin=dict(l=10, r=10, t=10, b=10),
      font=dict(family=FONT_FAMILY, size=12),
      hoverlabel=dict(font=dict(family=FONT_FAMILY, size=13)),
      legend=dict(orientation="h", y=1.08, x=0, title=None),
      xaxis=dict(title="Year", gridcolor="rgba(150,150,150,0.15)"),
      yaxis=dict(
          title="Cumulative cost ($)", gridcolor="rgba(150,150,150,0.15)"
      ),
      hovermode="x unified",
      plot_bgcolor="rgba(0,0,0,0)",
      paper_bgcolor="rgba(0,0,0,0)",
  )
  st.plotly_chart(fig_t, **FULL)

  with st.expander("Full results table"):
    st.dataframe(
        results.style.format({
            "Composite score": "{:,.1f}",
            "Annual fuel cost ($)": "${:,.0f}",
            "Daily cost ($)": "${:,.2f}",
            "Annual energy (MJ)": "{:,.0f}",
            "Energy system mass (kg)": "{:,.0f}",
            "Usable payload (kg)": "{:,.0f}",
            "Payload capacity used (%)": "{:,.1f}%",
            "Annual CO₂ (kg)": "{:,.0f}",
            "Powertrain efficiency": "{:.0%}",
        }),
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
      "tractive energy the route demands, divide by each powertrain's"
      " efficiency to get energy at the source, convert that into fuel, cost"
      " and CO₂, then score the three options against one another.</div>",
      unsafe_allow_html=True,
  )

  st.markdown(
      """
        <div class='card'>
          <div style='display:flex;flex-wrap:wrap;gap:1.6rem;font-size:0.92rem;color:var(--ink);'>
            <div><b>Stage 1</b><br><span style='color:var(--subtle);'>Road load → wheel energy</span></div>
            <div style='color:var(--subtle);'>→</div>
            <div><b>Stage 2</b><br><span style='color:var(--subtle);'>Wheel energy ÷ efficiency</span></div>
            <div style='color:var(--subtle);'>→</div>
            <div><b>Stage 3</b><br><span style='color:var(--subtle);'>Energy → fuel, cost, CO₂</span></div>
            <div style='color:var(--subtle);'>→</div>
            <div><b>Stage 4</b><br><span style='color:var(--subtle);'>Normalize and weight</span></div>
          </div>
        </div>
        """,
      unsafe_allow_html=True,
  )

  c1, c2 = st.columns(2, gap="large")

  with c1:
    st.markdown(
        "<div class='eq-card'><div class='eq-num'>Equation 01</div>"
        "<div class='eq-title'>Gross vehicle mass</div>",
        unsafe_allow_html=True,
    )
    st.latex(
        r"m = \left(m_{\text{curb}} + m_{\text{payload}}\right)\times 0.45359"
    )

    st.markdown(
        "<div class='eq-card'><div class='eq-num'>Equation 02</div>"
        "<div class='eq-title'>Rolling resistance</div>",
        unsafe_allow_html=True,
    )
    st.latex(r"F_{rr} = C_{rr}\, m\, g \qquad E_{rr} = F_{rr}\, d")

    st.markdown(
        "<div class='eq-card'><div class='eq-num'>Equation 03</div>"
        "<div class='eq-title'>Aerodynamic drag</div>",
        unsafe_allow_html=True,
    )
    st.latex(
        r"F_d = \tfrac{1}{2}\,\rho\, A\, C_d\, v^{2} \qquad P_d = F_d\, v"
    )

  with c2:
    st.markdown(
        "<div class='eq-card'><div class='eq-num'>Equation 04</div>"
        "<div class='eq-title'>Launch time, force and distance</div>",
        unsafe_allow_html=True,
    )
    st.latex(
        r"t_{acc} = \frac{v}{a} \qquad F_{acc} = m\,a \qquad d_{acc} ="
        r" \tfrac{1}{2}\,v\,t_{acc}"
    )

    st.markdown(
        "<div class='eq-card'><div class='eq-num'>Equation 05</div>"
        "<div class='eq-title'>Stop–start kinetic energy</div>",
        unsafe_allow_html=True,
    )
    st.latex(r"E_{acc} = N_{stops}\cdot \tfrac{1}{2}\, m\, v^{2}")

    st.markdown(
        "<div class='eq-card'><div class='eq-num'>Equation 06</div>"
        "<div class='eq-title'>Total tractive demand with auxiliaries</div>",
        unsafe_allow_html=True,
    )
    st.latex(
        r"E_{tract} = \left(E_{acc}+E_{d}+E_{rr}-\eta_{regen}E_{acc}\right)"
        r"\left(1+\alpha_{aux}\right)"
    )


# ==========================================================
# TAB 3 — TECHNICAL REPORT
# ==========================================================
with tab3:
  st.markdown(
      "<div class='section-title'>Technical paper</div>"
      "<div class='section-note'>Full methodology, source data and discussion"
      " of results.</div>",
      unsafe_allow_html=True,
  )

  pdf_filename = "technical_report.pdf"
  try:
    with open(pdf_filename, "rb") as f:
      base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(
        f"<iframe src='data:application/pdf;base64,{base64_pdf}' width='100%' "
        "height='820' style='border:none;border-radius:18px;"
        "box-shadow:0 8px 28px var(--shadow);'></iframe>",
        unsafe_allow_html=True,
    )
  except FileNotFoundError:
    st.markdown(
        """
            <div class='card' style='text-align:center;padding:3.2rem 2rem;'>
              <div style='font-size:1.25rem;font-weight:600;letter-spacing:-0.02em;color:var(--ink);'>
                No report loaded yet
              </div>
              <div style='color:var(--subtle);font-size:0.95rem;margin-top:0.5rem;
                          max-width:46ch;margin-left:auto;margin-right:auto;'>
                Add a file named <b>technical_report.pdf</b> to the same folder as
                this app, then reload the page to read it here.
              </div>
            </div>
            """,
        unsafe_allow_html=True,
    )

st.markdown(
    "<div style='text-align:center;color:var(--subtle);font-size:0.8rem;"
    "margin-top:2.5rem;'>Energy figures are modeled estimates for comparison "
    "between powertrains, not manufacturer specifications.</div>",
    unsafe_allow_html=True,
)
