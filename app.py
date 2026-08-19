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

/* Hide standard header elements */
#MainMenu, footer {{ visibility: hidden; }}
header {{ visibility: hidden; }}

/* Force BOTH the open and close sidebar buttons to stay visible */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarHeader"] {{
  visibility: visible !important;
}}

/* Move the open button down slightly so it isn't cut off at the very top */
[data-testid="stSidebarCollapsedControl"] {{
  top: 0.5rem;
  left: 0.5rem;
  z-index: 999999;
}}

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
      .score-card.out {{ opacity: 0.62; }}
      .badge.fail {{ background: #ff453a; }}
      .kv span.warn {{ color: #d70015; font-weight: 600; }}
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
      .derived {{
        display: flex; justify-content: space-between; align-items: baseline;
        background: {CANVAS}; border-radius: 10px;
        padding: 0.45rem 0.7rem; margin-top: 0.4rem;
        font-size: 0.83rem; color: {SUBTLE};
      }}
      .derived b {{ color: {INK}; font-variant-numeric: tabular-nums; font-weight: 600; }}
      .derived i {{ color: {ACCENT}; font-style: normal; font-weight: 500; }}

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
    "w_mass": ("Usable payload", 10),
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
        f"Set the route, the prices and what matters to you. Everything else "
        f"lives under Advanced settings.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='side-group'>Route</div>", unsafe_allow_html=True)
    route_dist = st.slider("Daily route distance (miles)", 5, 500, 15, step=5)
    operating_days = st.number_input("Operating days per year", 100, 365, 355, step=5)
    n_stops = st.slider("Stops per day", 0, 400, 100, step=10)

    st.markdown("<div class='side-group'>Energy prices</div>", unsafe_allow_html=True)
    diesel_price = st.number_input("Diesel ($/gal)", 1.0, 15.0, 5.30, step=0.10)
    h2_price = st.number_input("Hydrogen ($/kg)", 1.0, 60.0, 32.00, step=1.00)
    elec_price = st.number_input("Electricity ($/kWh)", 0.02, 1.00, 0.31, step=0.01)

    # ---------- Advanced settings ----------
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
        payload = st.number_input("Payload requirement (lbs)", 0, 60000, 20000, step=1000)
        gvwr = st.number_input("GVWR — max legal gross weight (lbs)", 20000, 90000, 66000, step=1000)

        st.markdown("<div class='side-group'>Energy storage</div>", unsafe_allow_html=True)
        h2_grav = st.slider(
            "H₂ tank system capacity (% H₂ by mass)", 2.0, 10.0, 5.7, step=0.1,
            help="Fraction of the filled 700-bar tank system that is hydrogen. "
                 "5.7% means the tank weighs about 17× the fuel it holds.",
        )
        pack_factor = st.slider(
            "Battery pack integration factor", 0.50, 1.00, 0.70, step=0.01,
            help="Cell-to-pack ratio. Enclosure, cooling, BMS and structure mean a "
                 "pack is heavier than its cells alone.",
        )
        dod = st.slider(
            "Usable depth of discharge (%)", 50, 100, 90, step=5,
            help="Packs are oversized so the route only draws this share of "
                 "nameplate capacity.",
        )
        diesel_tank_pct = st.slider(
            "Diesel tank + hardware (% of fuel mass)", 0, 60, 20, step=5
        )

        st.markdown("<div class='side-group'>Road load</div>", unsafe_allow_html=True)
        cd = st.slider("Drag coefficient  Cd", 0.40, 1.20, 0.90, step=0.01)
        frontal_area = st.slider("Frontal area (m²)", 4.0, 14.0, 10.0, step=0.5)
        crr = st.slider(
            "Rolling resistance  C_rr", 0.004, 0.020, 0.010, step=0.001, format="%.3f"
        )

        st.markdown("<div class='side-group'>Launch behavior</div>", unsafe_allow_html=True)
        accel_rate = st.slider(
            "Acceleration rate (m/s²)", 0.30, 3.00, 1.36, step=0.02,
            help="Time to reach operating speed is derived from this, not entered.",
        )
        _v_ms = avg_speed * MPH_TO_MS
        t_accel = _v_ms / accel_rate
        st.markdown(
            f"<div class='derived'><span>Time to reach speed &nbsp;"
            f"<i>t = v / a</i></span><b>{t_accel:,.2f} s</b></div>"
            f"<div class='derived'><span>Operating speed in SI</span>"
            f"<b>{_v_ms:,.2f} m/s</b></div>",
            unsafe_allow_html=True,
        )

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
a = accel_rate                             # m/s^2 (input); t_accel = v / a

# Stop-start kinetic energy
d_accel_each = 0.5 * v * t_accel           # m per acceleration event
d_accel_total = min(n_stops * d_accel_each, d_total)
d_cruise = max(d_total - d_accel_total, 0.0)

F_accel = m * a                            # N
E_accel = n_stops * 0.5 * m * v**2 / 1e6   # MJ/day

# Aerodynamic drag (acts over the cruise segment)
F_drag = 0.5 * RHO_AIR * frontal_area * cd * v**2   # N
P_drag = F_drag * v                                 # W
E_drag = F_drag * d_cruise / 1e6                     # MJ/day

# Rolling resistance (acts over the whole route)
F_rr = crr * m * G                          # N
E_rr = F_rr * d_total / 1e6                 # MJ/day

E_tractive = E_accel + E_drag + E_rr                        # MJ/day, gross
E_recovered = (regen_pct / 100.0) * E_accel                 # MJ/day, hybrids only
aux_factor = 1 + aux_pct / 100.0

E_daily_conv = E_tractive * aux_factor                      # diesel: no regen
E_daily_hybrid = (E_tractive - E_recovered) * aux_factor    # H2 FC + BEV

# --- Tank-to-wheel energy demand -------------------------------------------
E_src_diesel = E_daily_conv / ETA_DIESEL
E_src_h2 = E_daily_hybrid / ETA_H2
E_src_bev = E_daily_hybrid / ETA_BEV

# --- Consumption, cost, emissions, storage system mass ----------------------
diesel_kg = E_src_diesel / DIESEL_LHV
diesel_L = diesel_kg / DIESEL_DENSITY
diesel_gal = diesel_L / L_PER_GAL
diesel_cost_d = diesel_gal * diesel_price
diesel_co2_d = diesel_gal * EF_DIESEL
diesel_sys = diesel_kg * (1 + diesel_tank_pct / 100.0)          # fuel + tank

h2_kg = E_src_h2 / H2_LHV
h2_cost_d = h2_kg * h2_price
h2_co2_d = h2_kg * EF_H2
h2_sys = h2_kg / (h2_grav / 100.0)                              # 700-bar tank system

bev_kwh = E_src_bev / MJ_PER_KWH                                # energy drawn on route
bev_cost_d = bev_kwh * elec_price
bev_co2_d = bev_kwh * EF_GRID
bev_nameplate_kwh = bev_kwh / (dod / 100.0)                     # oversized for DoD
bev_sys = bev_nameplate_kwh / (BATT_DENSITY_KWH * pack_factor)  # cells → full pack

daily_cost = np.array([diesel_cost_d, h2_cost_d, bev_cost_d])
fuel_mass = np.array([diesel_kg, h2_kg, bev_kwh / BATT_DENSITY_KWH])
system_mass = np.array([diesel_sys, h2_sys, bev_sys])           # kg on the truck
daily_energy = np.array([E_src_diesel, E_src_h2, E_src_bev])
daily_co2 = np.array([diesel_co2_d, h2_co2_d, bev_co2_d])
efficiency = np.array([ETA_DIESEL, ETA_H2, ETA_BEV])

annual_cost = daily_cost * operating_days
annual_energy = daily_energy * operating_days
annual_co2 = daily_co2 * operating_days

# --- Payload accounting ------------------------------------------------------
# The energy system competes with cargo for the same weight allowance, so a
# longer route displaces payload. This is where duty cycle changes the ranking.
rated_capacity_kg = max((gvwr - curb_weight) * LB_TO_KG, 0.0)   # payload if energy were weightless
usable_payload = rated_capacity_kg - system_mass                 # kg of cargo left
required_payload = payload * LB_TO_KG
feasible = usable_payload >= required_payload
payload_used_pct = np.where(
    rated_capacity_kg > 0, system_mass / rated_capacity_kg * 100.0, 100.0
)
any_feasible = bool(feasible.any())


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
# Payload score: cargo capacity left after the energy system takes its share,
# normalized against whichever technology leaves the most. A vehicle that
# cannot carry the required load scores zero here and is barred from winning.
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

# A technology that cannot carry the required payload is not a candidate,
# however well it scores elsewhere.
eligible = composite if not any_feasible else np.where(feasible, composite, -np.inf)
best_idx = int(np.argmax(eligible))
best_tech = TECHS[best_idx]

RATIONALE = {
    "Diesel": (
        "Diesel wins on infrastructure and onboard energy density: it refuels "
        "anywhere, carries a full shift of energy in a few hundred pounds of fuel "
        "and tank, and needs no depot investment. It pays for that with the worst "
        "tank-to-wheel efficiency and the highest tailpipe CO₂."
    ),
    "Hydrogen Fuel Cell": (
        "Hydrogen holds its payload better than a battery on long routes — the "
        "700-bar tank is heavy, but it grows far more slowly with distance than a "
        "pack does. Its weakness is price per kilogram and a station network that "
        "barely exists."
    ),
    "Battery Electric": (
        "Battery electric converts about 90% of stored energy into tractive work, "
        "so this route costs the least to run and emits the least CO₂ even on an "
        "average grid. The trade-off is pack mass, which displaces cargo as route "
        "length grows."
    ),
}

results = pd.DataFrame(
    {
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
    }
)


# ==========================================================
# HELPERS
# ==========================================================
def score_card(tech: str, score: float, rows: list, winner: bool,
               ok: bool = True) -> str:
    color = TECH_COLORS[tech] if ok else "#c7c7cc"
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
    "<div class='subhead'>A physics-first comparison of diesel, hydrogen fuel cell "
    "and battery electric drivelines — built from tractive-energy demand, not "
    "sticker specifications. Set a route and prices to get an answer; open "
    "Advanced settings to change the vehicle itself.</div>",
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
                score_card(tech, composite[i], rows, i == best_idx, bool(feasible[i])),
                unsafe_allow_html=True,
            )

    if not feasible.all():
        blocked = ", ".join(t for t, ok in zip(TECHS, feasible) if not ok)
        st.warning(
            f"{blocked} cannot complete this route with the required "
            f"{required_payload:,.0f} kg payload — the energy system alone exceeds "
            f"the {rated_capacity_kg:,.0f} kg the chassis has left under its GVWR. "
            f"It scores zero on payload and is barred from the recommendation.",
            icon="⚠️",
        )
    if not any_feasible:
        st.error(
            "No powertrain can carry the required payload over this route. "
            "Shorten the route, lower the payload, or raise the GVWR in "
            "Advanced settings.",
            icon="🚫",
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
                x=sweep_mi, y=ys, name=tech, mode="lines",
                line=dict(color=TECH_COLORS[tech], width=3),
                hovertemplate="%{x:.0f} mi<br>" + tech + ": %{y:,.0f} kg left<extra></extra>",
            )
        )
    fig_p.add_hline(
        y=required_payload, line_dash="dash", line_color="#ff453a",
        annotation_text=f"Required payload — {required_payload:,.0f} kg",
        annotation_position="bottom right",
    )
    fig_p.add_vline(x=route_dist, line_dash="dot", line_color=SUBTLE,
                    annotation_text="Your route", annotation_position="top left")
    fig_p.update_layout(
        template="simple_white", height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="-apple-system, BlinkMacSystemFont, Inter, sans-serif",
                  color=INK, size=12),
        legend=dict(orientation="h", y=1.12, x=0, title=None),
        xaxis_title="Daily route distance (miles)",
        yaxis_title="Payload capacity remaining (kg)",
        hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig_p, **FULL)

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
                "Usable payload": s_mass * w_mass / denom,
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
                    "Energy system mass (kg)": "{:,.0f}",
                    "Usable payload (kg)": "{:,.0f}",
                    "Payload capacity used (%)": "{:,.1f}%",
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
        st.latex(r"m = \left(m_{\text{curb}} + m_{\text{payload}}\right)\times 0.45359")
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
        st.latex(r"F_{rr} = C_{rr}\, m\, g \qquad E_{rr} = F_{rr}\, d")
        st.markdown(
            f"<div class='eq-body'>The normal force on level ground is <b>mg</b>, so "
            f"rolling resistance is constant with speed and scales linearly with "
            f"distance. On a heavy, slow, stop-heavy route this is usually the "
            f"single largest term.<br>"
            f"<b>C_rr = {crr:.3f} · F_rr = {F_rr:,.0f} N · E_rr = {E_rr:,.2f} MJ/day</b>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 03</div>"
            "<div class='eq-title'>Aerodynamic drag</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"F_d = \tfrac{1}{2}\,\rho\, A\, C_d\, v^{2} \qquad P_d = F_d\, v")
        st.markdown(
            f"<div class='eq-body'>Drag rises with the square of velocity and the "
            f"energy cost with the cube, so it is nearly irrelevant at 15 mph and "
            f"dominant on highway duty. Drag is integrated over the cruise segment "
            f"only.<br>"
            f"<b>F_d = {F_drag:,.1f} N · P_d = {P_drag/1000:,.2f} kW · "
            f"E_drag = {E_drag:,.2f} MJ/day</b></div></div>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 04</div>"
            "<div class='eq-title'>Launch time, force and distance</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"t_{acc} = \frac{v}{a} \qquad F_{acc} = m\,a "
                 r"\qquad d_{acc} = \tfrac{1}{2}\,v\,t_{acc}")
        st.markdown(
            f"<div class='eq-body'>Acceleration is treated as constant from rest to "
            f"operating speed. The workbook entered a launch time and solved for "
            f"<b>a = v / t</b>; the model inverts that relationship so the physical "
            f"capability of the truck is the input and the time follows from "
            f"whatever speed the route runs at. The distance covered while "
            f"accelerating is subtracted from the cruise distance used in the drag "
            f"term, so no metre is counted twice.<br>"
            f"<b>a = {a:.2f} m/s² → t_acc = {t_accel:.2f} s · "
            f"F_acc = {F_accel:,.0f} N · d_acc = {d_accel_each:,.1f} m per stop</b>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 05</div>"
            "<div class='eq-title'>Stop–start kinetic energy</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"E_{acc} = N_{stops}\cdot \tfrac{1}{2}\, m\, v^{2}")
        st.markdown(
            f"<div class='eq-body'>Work done against inertia equals the kinetic "
            f"energy of the vehicle, since <b>F·d = m·a·½·a·t² = ½mv²</b>. Without "
            f"regeneration every joule here is thrown away as brake heat at the next "
            f"stop — the defining penalty of refuse duty.<br>"
            f"<b>{n_stops} stops × {0.5*m*v**2/1e6:,.3f} MJ = {E_accel:,.2f} MJ/day</b>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 06</div>"
            "<div class='eq-title'>Total tractive demand with auxiliaries</div>",
            unsafe_allow_html=True,
        )
        st.latex(
            r"E_{tract} = \left(E_{acc}+E_{d}+E_{rr}-\eta_{regen}E_{acc}\right)"
            r"\left(1+\alpha_{aux}\right)"
        )
        st.markdown(
            f"<div class='eq-body'>Cabin heating, hydraulics and the compaction body "
            f"are carried as a percentage uplift <b>α_aux</b> on the sum of the "
            f"mechanical terms. Recovery <b>η_regen</b> applies only to braking "
            f"kinetic energy, and only on the electric and fuel-cell hybrid "
            f"drivelines.<br><b>E_tract = {E_daily_hybrid:,.2f} MJ/day "
            f"(electric) · {E_daily_conv:,.2f} MJ/day (diesel)</b></div></div>",
            unsafe_allow_html=True,
        )

    # ---------- Stage 2 ----------
    st.markdown(
        "<div class='section-title' style='margin-top:1.4rem;'>Stage 2 — Powertrain efficiency</div>"
        "<div class='section-note'>The same wheel energy costs three very different "
        "amounts of stored energy.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='eq-card'><div class='eq-num'>Equation 07</div>"
        "<div class='eq-title'>Energy at the source</div>",
        unsafe_allow_html=True,
    )
    st.latex(r"E_{source} = \frac{E_{tract}}{\eta_{powertrain}}")
    st.markdown(
        f"<div class='eq-body'>η is a tank-to-wheel figure covering conversion, "
        f"transmission and driveline losses. Diesel loses roughly three quarters of "
        f"its fuel energy to heat; a battery driveline loses about a tenth.<br>"
        f"<b>Diesel η = 25% → {E_src_diesel:,.1f} MJ · "
        f"Fuel cell η = 50% → {E_src_h2:,.1f} MJ · "
        f"Battery η = 90% → {E_src_bev:,.1f} MJ</b> (per day)</div></div>",
        unsafe_allow_html=True,
    )

    # ---------- Stage 3 ----------
    st.markdown(
        "<div class='section-title' style='margin-top:1.4rem;'>Stage 3 — Fuel, cost, mass, emissions</div>"
        "<div class='section-note'>Energy is converted into the unit each fuel is "
        "actually sold and stored in.</div>",
        unsafe_allow_html=True,
    )

    d1, d2, d3 = st.columns(3, gap="large")

    with d1:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 08 · Diesel</div>"
            "<div class='eq-title'>Mass, volume, gallons</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"m_f = \frac{E_{source}}{LHV_d}")
        st.latex(r"V_{gal} = \frac{m_f}{\rho_d \cdot 3.79}")
        st.markdown(
            f"<div class='eq-body'>LHV_d = 44 MJ/kg, ρ_d = 0.85 kg/L. A gallon of "
            f"diesel therefore carries about 141.7 MJ.<br>"
            f"<b>{diesel_kg:,.2f} kg → {diesel_L:,.1f} L → "
            f"{diesel_gal:,.2f} gal/day</b></div></div>",
            unsafe_allow_html=True,
        )

    with d2:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 09 · Hydrogen</div>"
            "<div class='eq-title'>Mass of hydrogen</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"m_{H_2} = \frac{E_{source}}{LHV_{H_2}}")
        st.markdown(
            f"<div class='eq-body'>LHV_H₂ = 120 MJ/kg — nearly three times diesel by "
            f"mass, which is why the fuel itself is so light. Tank mass is excluded "
            f"here and is the model's main omission for hydrogen.<br>"
            f"<b>{h2_kg:,.2f} kg/day</b></div></div>",
            unsafe_allow_html=True,
        )

    with d3:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 10 · Battery</div>"
            "<div class='eq-title'>Pack energy and pack mass</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"E_{kWh} = \frac{E_{source}}{3.6} \qquad "
                 r"E_{nameplate} = \frac{E_{kWh}}{DoD}")
        st.markdown(
            f"<div class='eq-body'>The pack is sized to complete one route on a "
            f"single charge while drawing only its usable depth of discharge, so "
            f"nameplate capacity exceeds the energy actually consumed.<br>"
            f"<b>{bev_kwh:,.1f} kWh drawn → {bev_nameplate_kwh:,.1f} kWh installed"
            f"</b></div></div>",
            unsafe_allow_html=True,
        )

    # ---------- Storage system mass + payload ----------
    p1, p2 = st.columns(2, gap="large")
    with p1:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 11</div>"
            "<div class='eq-title'>Energy system mass, not fuel mass</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"m_{sys}^{diesel} = m_f\,(1+\phi_{tank})")
        st.latex(r"m_{sys}^{H_2} = \frac{m_{H_2}}{\gamma_{tank}}")
        st.latex(r"m_{sys}^{BEV} = \frac{E_{nameplate}}{e_{grav}\cdot \kappa_{pack}}")
        st.markdown(
            f"<div class='eq-body'>What sits on the chassis is the fuel <i>and</i> "
            f"everything holding it. A 700-bar composite tank system is only "
            f"<b>γ = {h2_grav:.1f}%</b> hydrogen by mass, so the tank outweighs its "
            f"contents roughly {100/h2_grav:.0f}-fold — the single biggest correction "
            f"to the original workbook. Cells become a pack through the integration "
            f"factor <b>κ = {pack_factor:.2f}</b>.<br>"
            f"<b>Diesel {diesel_sys:,.0f} kg · Hydrogen {h2_sys:,.0f} kg · "
            f"Battery {bev_sys:,.0f} kg</b></div></div>",
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 12</div>"
            "<div class='eq-title'>Usable payload and the feasibility gate</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"m_{cargo} = \left(GVWR - m_{curb}\right) - m_{sys}")
        st.latex(r"\text{feasible} \iff m_{cargo} \ge m_{payload}^{req}")
        st.markdown(
            f"<div class='eq-body'>Cargo and energy storage compete for the same "
            f"weight allowance under the GVWR. Because <b>m_sys</b> grows with route "
            f"length while the allowance is fixed, this is the term that makes the "
            f"duty cycle change the answer rather than just the numbers. A "
            f"powertrain that cannot carry the required load scores zero here and "
            f"is barred from the recommendation, however cheap it is.<br>"
            f"<b>Allowance {rated_capacity_kg:,.0f} kg · required "
            f"{required_payload:,.0f} kg · "
            f"{'all three feasible' if feasible.all() else 'not all feasible'}</b>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    e1, e2 = st.columns(2, gap="large")
    with e1:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 13</div>"
            "<div class='eq-title'>Operating cost</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"C_{daily} = Q_{fuel}\cdot p_{fuel} \qquad "
                 r"C_{annual} = C_{daily}\cdot N_{days}")
        st.markdown(
            f"<div class='eq-body'>Q is gallons, kilograms or kilowatt-hours "
            f"depending on the technology. This is an energy cost only — no capital, "
            f"maintenance or demand charges.<br>"
            f"<b>{operating_days} operating days per year</b></div></div>",
            unsafe_allow_html=True,
        )
    with e2:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 14</div>"
            "<div class='eq-title'>CO₂ emissions</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"M_{CO_2} = Q_{fuel}\cdot \varepsilon_{fuel}")
        st.markdown(
            f"<div class='eq-body'>ε = 10.18 kg/gal for diesel (tailpipe), "
            f"10.5 kg/kg for steam-methane-reformed hydrogen, and 0.394 kg/kWh for "
            f"average grid electricity. Hydrogen and electricity therefore carry "
            f"upstream emissions, not tailpipe emissions — a like-for-like "
            f"well-to-wheel comparison would also load diesel with refining.</div></div>",
            unsafe_allow_html=True,
        )

    # ---------- Stage 4 ----------
    st.markdown(
        "<div class='section-title' style='margin-top:1.4rem;'>Stage 4 — Decision logic</div>"
        "<div class='section-note'>Five criteria in different units are reduced to a "
        "common 0–100 scale, then weighted.</div>",
        unsafe_allow_html=True,
    )

    f1, f2 = st.columns(2, gap="large")
    with f1:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 15</div>"
            "<div class='eq-title'>Ratio normalization</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"S_i = \frac{x_{\min}}{x_i}\times 100 \quad\text{(lower is better)}")
        st.latex(r"S_i = \frac{x_i}{x_{\max}}\times 100 \quad\text{(higher is better)}")
        st.markdown(
            "<div class='eq-body'>Ratio scaling is used instead of min–max scaling so "
            "the worst option never scores a hard zero. A technology twice as "
            "expensive as the cheapest scores 50, which preserves the size of the "
            "gap rather than only its rank. Cost and CO₂ use the first form; "
            "efficiency and usable payload use the second; infrastructure readiness "
            "is a fixed expert score of 100 / 30 / 60. Note that cost and CO₂ ratios "
            "are scale-invariant — every powertrain's consumption is proportional to "
            "the same tractive energy, so route length cancels out of those two "
            "criteria. Payload and regeneration are the terms that carry duty-cycle "
            "sensitivity.</div></div>",
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            "<div class='eq-card'><div class='eq-num'>Equation 16</div>"
            "<div class='eq-title'>Weighted composite score</div>",
            unsafe_allow_html=True,
        )
        st.latex(r"\text{Score} = \frac{\sum_{i=1}^{5} w_i S_i}{\sum_{i=1}^{5} w_i}"
                 r"\qquad \sum_{i=1}^{5} w_i \le 100")
        st.markdown(
            f"<div class='eq-body'>The five weights are hard-capped so they can never "
            f"exceed a 100% budget; each slider's ceiling shrinks as the others are "
            f"raised. Dividing by the allocated total keeps the result on a 0–100 "
            f"scale even when part of the budget is left unspent.<br>"
            f"<b>Allocated: {total_w}% · Winner: {best_tech} at "
            f"{composite[best_idx]:,.1f}</b></div></div>",
            unsafe_allow_html=True,
        )

    # ---------- Assumptions ----------
    st.markdown("<hr class='rule'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-title'>Assumption register</div>"
        "<div class='section-note'>Every fixed constant in the model, with its "
        "source unit.</div>",
        unsafe_allow_html=True,
    )

    a1, a2 = st.columns(2, gap="large")
    with a1:
        st.markdown("**Environment and vehicle**")
        st.dataframe(
            pd.DataFrame(
                {
                    "Parameter": [
                        "Air density ρ", "Gravity g", "Drag coefficient Cd",
                        "Frontal area A", "Rolling resistance C_rr",
                        "Average operating speed", "Stops per day",
                        "Acceleration rate", "Launch time (derived)",
                    ],
                    "Value": [
                        f"{RHO_AIR}", f"{G}", f"{cd:.2f}", f"{frontal_area:.1f}",
                        f"{crr:.3f}", f"{avg_speed}", f"{n_stops}",
                        f"{a:.2f}", f"{t_accel:.2f}",
                    ],
                    "Unit": [
                        "kg/m³", "m/s²", "—", "m²", "—", "mph", "per day",
                        "m/s²", "s",
                    ],
                }
            ),
            hide_index=True,
            **FULL,
        )
    with a2:
        st.markdown("**Energy carriers**")
        st.dataframe(
            pd.DataFrame(
                {
                    "Parameter": [
                        "Diesel LHV", "Diesel density", "Diesel efficiency",
                        "Diesel emissions factor", "Hydrogen LHV",
                        "Fuel cell efficiency", "Hydrogen emissions factor",
                        "Cell energy density", "Battery efficiency",
                        "Grid emissions factor",
                    ],
                    "Value": [
                        "44.0", "0.85", "25%", "10.18", "120.0", "50%", "10.5",
                        "0.16", "90%", "0.394",
                    ],
                    "Unit": [
                        "MJ/kg", "kg/L", "—", "kg CO₂/gal", "MJ/kg", "—",
                        "kg CO₂/kg", "kWh/kg", "—", "kg CO₂/kWh",
                    ],
                }
            ),
            hide_index=True,
            **FULL,
        )

    # ---------- Limitations ----------
    st.markdown(
        f"""
        <div class='card' style='margin-top:1.2rem;'>
          <div class='eq-title'>What this model does not capture</div>
          <div class='eq-body' style='margin-top:0.5rem;'>
            <b>Capital cost.</b> Vehicle purchase price, depot charging hardware and
            hydrogen dispensing equipment are excluded. Battery electric wins on
            energy cost long before it wins on total cost of ownership.<br><br>
            <b>Storage system mass.</b> Tanks, enclosures, cooling and structure are
            now counted, but the powertrain hardware itself is not — a fuel cell
            stack, an engine and block, or a traction motor all differ in mass and
            none of them appear here.<br><br>
            <b>Grade and elevation.</b> The route is assumed to return to its starting
            elevation, so gravitational work nets to zero. A hilly route without
            regeneration would penalize diesel further.<br><br>
            <b>Charging and refueling time.</b> Route feasibility is treated as a
            binary — the model sizes energy for one shift but does not test whether
            that energy can be replaced overnight.<br><br>
            <b>Empirical cross-check.</b> The workbook's MPG-derived baseline of
            3.54 MJ/mi at the wheels is an <i>aggregate</i> figure that already
            contains drag, rolling resistance and stop–start losses. It is used here
            only as a sanity check against the summed physical terms, never added to
            them, to avoid double-counting the same energy.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# TAB 3 — TECHNICAL REPORT
# ==========================================================
with tab3:
    st.markdown(
        "<div class='section-title'>Technical paper</div>"
        "<div class='section-note'>Full methodology, source data and discussion of "
        "results.</div>",
        unsafe_allow_html=True,
    )

    pdf_filename = "technical_report.pdf"
    try:
        with open(pdf_filename, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(
            f"<iframe src='data:application/pdf;base64,{base64_pdf}' width='100%' "
            f"height='820' style='border:none;border-radius:18px;"
            f"box-shadow:0 8px 28px rgba(0,0,0,0.08);'></iframe>",
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        st.markdown(
            f"""
            <div class='card' style='text-align:center;padding:3.2rem 2rem;'>
              <div style='font-size:1.25rem;font-weight:600;letter-spacing:-0.02em;'>
                No report loaded yet
              </div>
              <div style='color:{SUBTLE};font-size:0.95rem;margin-top:0.5rem;
                          max-width:46ch;margin-left:auto;margin-right:auto;'>
                Add a file named <b>technical_report.pdf</b> to the same folder as
                this app, then reload the page to read it here.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    f"<div style='text-align:center;color:{SUBTLE};font-size:0.8rem;"
    f"margin-top:2.5rem;'>Energy figures are modeled estimates for comparison "
    f"between powertrains, not manufacturer specifications.</div>",
    unsafe_allow_html=True,
)
