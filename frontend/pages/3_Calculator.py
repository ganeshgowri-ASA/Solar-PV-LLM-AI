"""
Calculator Page - Standalone Streamlit page
For use with Streamlit's multi-page app feature.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client, CalculationType

st.set_page_config(page_title="Calculator - Solar PV AI", page_icon="", layout="wide")

st.title("Solar PV Calculator")
st.markdown("Calculate system size, energy output, ROI, and more.")

client = get_client()

# Calculator selection
calc_options = {
    "System Size": CalculationType.SYSTEM_SIZE,
    "Energy Output": CalculationType.ENERGY_OUTPUT,
    "ROI Analysis": CalculationType.ROI,
    "Payback Period": CalculationType.PAYBACK_PERIOD,
    "Panel Count": CalculationType.PANEL_COUNT,
    "Inverter Size": CalculationType.INVERTER_SIZE,
    "Battery Size": CalculationType.BATTERY_SIZE,
}

selected = st.selectbox("Calculation Type", list(calc_options.keys()))
calc_type = calc_options[selected]

st.markdown("---")

# Dynamic inputs
params = {}

if calc_type == CalculationType.SYSTEM_SIZE:
    c1, c2 = st.columns(2)
    with c1:
        params["annual_kwh"] = st.number_input("Annual Usage (kWh)", value=10000, step=500)
        params["peak_sun_hours"] = st.slider("Peak Sun Hours", 3.0, 7.0, 5.0)
    with c2:
        params["performance_ratio"] = st.slider("Performance Ratio", 0.7, 0.9, 0.8)
        params["panel_wattage"] = st.number_input("Panel Wattage", value=400)

elif calc_type == CalculationType.ENERGY_OUTPUT:
    c1, c2 = st.columns(2)
    with c1:
        params["system_size_kw"] = st.number_input("System Size (kW)", value=6.0)
        params["peak_sun_hours"] = st.slider("Peak Sun Hours", 3.0, 7.0, 5.0)
    with c2:
        params["performance_ratio"] = st.slider("Performance Ratio", 0.7, 0.9, 0.8)

elif calc_type == CalculationType.ROI:
    c1, c2 = st.columns(2)
    with c1:
        params["system_cost"] = st.number_input("System Cost ($)", value=15000)
        params["annual_kwh"] = st.number_input("Annual Production (kWh)", value=8000)
        params["electricity_rate"] = st.number_input("Rate ($/kWh)", value=0.12, format="%.2f")
    with c2:
        params["annual_rate_increase"] = st.slider("Annual Rate Increase", 0.0, 0.1, 0.03)
        params["incentive_percent"] = st.slider("Tax Credit %", 0, 50, 30)

elif calc_type == CalculationType.PAYBACK_PERIOD:
    c1, c2 = st.columns(2)
    with c1:
        params["system_cost"] = st.number_input("System Cost ($)", value=15000)
        params["annual_kwh"] = st.number_input("Annual Production (kWh)", value=8000)
    with c2:
        params["electricity_rate"] = st.number_input("Rate ($/kWh)", value=0.12, format="%.2f")
        params["incentive_percent"] = st.slider("Tax Credit %", 0, 50, 30)

elif calc_type == CalculationType.PANEL_COUNT:
    c1, c2 = st.columns(2)
    with c1:
        params["target_kwh_annual"] = st.number_input("Target Annual (kWh)", value=10000)
        params["panel_wattage"] = st.number_input("Panel Wattage", value=400)
    with c2:
        params["peak_sun_hours"] = st.slider("Peak Sun Hours", 3.0, 7.0, 5.0)
        params["efficiency_factor"] = st.slider("Efficiency Factor", 0.7, 0.9, 0.8)

elif calc_type == CalculationType.INVERTER_SIZE:
    c1, c2 = st.columns(2)
    with c1:
        params["array_size_kw"] = st.number_input("Array Size (kW DC)", value=6.0)
    with c2:
        params["dc_ac_ratio"] = st.slider("DC/AC Ratio", 1.0, 1.5, 1.2)

elif calc_type == CalculationType.BATTERY_SIZE:
    c1, c2 = st.columns(2)
    with c1:
        params["daily_kwh"] = st.number_input("Daily Usage (kWh)", value=30)
        params["backup_days"] = st.slider("Backup Days", 0.5, 3.0, 1.0)
    with c2:
        params["depth_of_discharge"] = st.slider("DoD %", 50, 95, 80) / 100
        params["backup_percentage"] = st.slider("Backup %", 25, 100, 100)

# Calculate
st.markdown("---")
c1, c2 = st.columns([1, 3])
with c1:
    calculate = st.button("Calculate", type="primary", use_container_width=True)
with c2:
    show_explanation = st.checkbox("Show Explanation", value=True)

if calculate:
    with st.spinner("Calculating..."):
        response = client.calculate(calc_type, params, include_explanation=show_explanation)

    if response.success:
        data = response.data
        st.subheader("Results")

        result = data.get("result", {})
        cols = st.columns(min(len(result), 4))
        for i, (k, v) in enumerate(result.items()):
            with cols[i % len(cols)]:
                label = k.replace("_", " ").title()
                st.metric(label, f"{v:,.2f}" if isinstance(v, float) else f"{v:,}")

        if show_explanation and data.get("explanation"):
            with st.expander("Explanation", expanded=True):
                st.markdown(data["explanation"])

        if data.get("recommendations"):
            with st.expander("Recommendations"):
                for rec in data["recommendations"]:
                    st.info(rec)
    else:
        st.error(response.error)
