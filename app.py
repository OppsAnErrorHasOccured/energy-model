import base64
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Config
st.set_page_config(
    page_title="Heavy-Duty Fleet Decarbonization Model", layout="wide"
)

st.title("⚡ Heavy-Duty Fleet Decarbonization Evaluation Model")
st.markdown("---")

# Setup 3 Tabs
tab1, tab2, tab3 = st.tabs(
    ["📊 Interactive Model", "📐 Governing Equations", "📄 Technical Report"]
)

# ==========================================
# TAB 1: INTERACTIVE MODEL
# ==========================================
with tab1:
  st.subheader("Interactive Powertrain Evaluator")

  col_input, col_output = st.columns([1, 2])

  with col_input:
    st.markdown("### 🎛️ Model Inputs")

    route_dist = st.slider("Daily Route Distance (miles)", 50, 800, 400, step=25)
    operating_days = st.number_input("Operating Days per Year", value=360, step=5)
    payload = st.number_input(
        "Payload Requirement (lbs)", value=20000, step=1000
    )

    st.markdown("#### Fuel & Energy Prices")
    diesel_price = st.number_input("Diesel Price ($/gal)", value=5.30, step=0.1)
    h2_price = st.number_input("Hydrogen Price ($/kg)", value=32.00, step=1.0)
    elec_price = st.number_input(
        "Electricity Price ($/kWh)", value=0.31, step=0.01
    )

    st.markdown("#### Score Weights (%)")
    w_cost = st.slider("Annual Fuel Cost Weight", 0, 100, 50) / 100
    w_mass = st.slider("System Mass Weight", 0, 100, 10) / 100
    w_eff = st.slider("Energy Efficiency Weight", 0, 100, 5) / 100
    w_infra = st.slider("Infrastructure Readiness Weight", 0, 100, 10) / 100
    w_emissions = st.slider("Emissions Weight", 0, 100, 15) / 100

  # Model Calculation Engine
  work_per_mile = 3.54365
  daily_work_required = route_dist * (work_per_mile / 400) * 1417.46
  annual_work_required = daily_work_required * operating_days

  # Diesel Calculations
  diesel_annual_energy = annual_work_required / 0.25
  diesel_annual_cost = (
      (route_dist / 400)
      * (operating_days / 360)
      * 76320
      * (diesel_price / 5.3)
  )
  diesel_mass = 46389.6

  # Hydrogen Calculations
  h2_annual_energy = annual_work_required / 0.50
  h2_annual_mass = h2_annual_energy / 120.0
  h2_annual_cost = h2_annual_mass * h2_price
  h2_mass = 8504.76

  # Battery Electric Calculations
  bev_annual_energy_mj = annual_work_required / 0.90
  bev_annual_kwh = bev_annual_energy_mj / 3.6
  bev_annual_cost = bev_annual_kwh * elec_price
  bev_mass = 2734.3

  with col_output:
    st.markdown("### 📈 Evaluation Summary")

    metrics_df = pd.DataFrame({
        "Technology": ["Diesel", "Hydrogen", "Battery Electric"],
        "Annual Cost ($)": [
            diesel_annual_cost,
            h2_annual_cost,
            bev_annual_cost,
        ],
        "Annual Energy (MJ)": [
            diesel_annual_energy,
            h2_annual_energy,
            bev_annual_energy_mj,
        ],
        "System Mass (kg)": [diesel_mass, h2_mass, bev_mass],
    })

    best_tech = metrics_df.loc[metrics_df["Annual Cost ($)"].idxmin()][
        "Technology"
    ]
    st.success(
        f"**Recommendation:** **{best_tech}** is currently favored based on"
        " operational costs and energy efficiency under the selected"
        " parameters."
    )

    st.dataframe(
        metrics_df.style.format({
            "Annual Cost ($)": "${:,.2f}",
            "Annual Energy (MJ)": "{:,.1f}",
            "System Mass (kg)": "{:,.1f}",
        }),
        use_container_width=True,
    )

    # 10-Year Cumulative Cost Chart
    years = np.arange(1, 11)
    df_10yr = pd.DataFrame({
        "Year": years,
        "Diesel": years * diesel_annual_cost,
        "Hydrogen": years * h2_annual_cost,
        "Battery Electric": years * bev_annual_cost,
    })

    fig = px.line(
        df_10yr,
        x="Year",
        y=["Diesel", "Hydrogen", "Battery Electric"],
        title="10-Year Cumulative Cost Comparison ($)",
        labels={"value": "Cost ($)", "variable": "Powertrain"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: GOVERNING EQUATIONS
# ==========================================
with tab2:
  st.header("📐 Governing Physics & Methodology")
  st.markdown(
      "Below are the primary physical relationships used to calculate powertrain"
      " energy demands:"
  )

  col_eq1, col_eq2 = st.columns(2)

  with col_eq1:
    st.markdown("### 1. Aerodynamic Drag Force")
    st.latex(r"F_d = \frac{1}{2} \cdot \rho \cdot A \cdot C_d \cdot v^2")
    st.write("""
        - $F_d$: Aerodynamic Drag Force ($N$)
        - $\\rho$: Air Density ($1.225 \\text{ kg/m}^3$)
        - $A$: Frontal Area ($10 \\text{ m}^2$)
        - $C_d$: Drag Coefficient ($0.9$)
        - $v$: Vehicle Velocity ($\\text{m/s}$)
        """)

    st.markdown("### 2. Rolling Resistance Force")
    st.latex(r"F_{rr} = C_{rr} \cdot m \cdot g")
    st.write("""
        - $F_{rr}$: Rolling Resistance Force ($N$)
        - $C_{rr}$: Coefficient of Rolling Resistance ($0.01$)
        - $m$: Vehicle Mass ($\\text{kg}$)
        - $g$: Gravitational Acceleration ($9.81 \\text{ m/s}^2$)
        """)

  with col_eq2:
    st.markdown("### 3. Acceleration Energy Demand")
    st.latex(r"E_{acc} = \frac{1}{2} \cdot m \cdot v^2 \cdot N_{stops}")
    st.write("""
        - Calculates total kinetic energy loss across start-stop cycles over the daily route distance.
        """)

    st.markdown("### 4. Total Energy & Powertrain Efficiency")
    st.latex(
        r"E_{required} = \frac{E_{drag} + E_{rr} +"
        r" E_{acc}}{\eta_{powertrain}}"
    )
    st.write("""
        - **Diesel Efficiency ($\\\\eta$):** $25\\\\%$
        - **Hydrogen Fuel Cell Efficiency ($\\\\eta$):** $50\\\\%$
        - **Battery Electric Efficiency ($\\\\eta$):** $90\\\\%$
        """)

# ==========================================
# TAB 3: TECHNICAL REPORT PDF
# ==========================================
with tab3:
  st.header("📄 Technical Research Paper")
  st.markdown(
      "Read the complete methodology, assumptions, and research findings"
      " below:"
  )

  pdf_filename = "technical_report.pdf"

  try:
    with open(pdf_filename, "rb") as f:
      base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    pdf_display = (
        f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%"'
        ' height="800" type="application/pdf"></iframe>'
    )
    st.markdown(pdf_display, unsafe_allow_html=True)
  except FileNotFoundError:
    st.warning(
        "⚠️ `technical_report.pdf` not found in directory. Upload your PDF to"
        " GitHub named `technical_report.pdf` when ready to enable the viewer."
    )