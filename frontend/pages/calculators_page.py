"""
Calculators Page - Standalone Streamlit page
Multiple solar PV calculators with real-time results and visualizations.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_client, CalculationType

st.set_page_config(page_title="Calculators - Solar PV AI", page_icon="", layout="wide")

st.title("Solar PV Calculators")
st.markdown("Professional calculators for system design, performance analysis, and financial planning.")

client = get_client()

# Create tabs for different calculators
tabs = st.tabs([
    "Energy Yield",
    "System Sizing",
    "ROI Calculator",
    "Payback Period",
    "Panel Count",
    "Inverter Size",
    "Battery Size",
])

# Energy Yield Calculator
with tabs[0]:
    st.markdown("### Energy Yield Calculator")
    st.markdown("Calculate expected energy production based on system size and location.")

    col1, col2 = st.columns(2)

    with col1:
        system_size = st.number_input(
            "System Size (kW)",
            min_value=1.0,
            max_value=10000.0,
            value=6.0,
            step=0.5,
            key="yield_system_size"
        )
        peak_sun_hours = st.slider(
            "Peak Sun Hours",
            min_value=3.0,
            max_value=7.0,
            value=5.0,
            step=0.1,
            key="yield_sun_hours",
            help="Typical values: 3-4 for northern regions, 5-6 for moderate climates, 6-7 for sunny regions"
        )

    with col2:
        performance_ratio = st.slider(
            "Performance Ratio",
            min_value=0.70,
            max_value=0.90,
            value=0.80,
            step=0.05,
            key="yield_performance",
            help="Typical range: 0.75-0.85 for well-designed systems"
        )

    if st.button("Calculate Energy Yield", type="primary", key="calc_yield"):
        params = {
            "system_size_kw": system_size,
            "peak_sun_hours": peak_sun_hours,
            "performance_ratio": performance_ratio
        }
        with st.spinner("Calculating..."):
            response = client.calculate(CalculationType.ENERGY_OUTPUT, params)

        if response.success:
            data = response.data
            result = data.get("result", {})

            st.markdown("---")
            st.subheader("Results")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Daily Energy", f"{result.get('daily_kwh', 0):.1f} kWh")
            with col2:
                st.metric("Monthly Energy", f"{result.get('monthly_kwh', 0):,.0f} kWh")
            with col3:
                st.metric("Annual Energy", f"{result.get('annual_kwh', 0):,.0f} kWh")

            if data.get("explanation"):
                with st.expander("Explanation", expanded=True):
                    st.markdown(data["explanation"])
        else:
            st.error(f"Calculation error: {response.error}")

# System Sizing Calculator
with tabs[1]:
    st.markdown("### System Sizing Calculator")
    st.markdown("Determine the optimal system size based on your energy needs.")

    col1, col2 = st.columns(2)

    with col1:
        annual_kwh = st.number_input(
            "Annual Energy Consumption (kWh)",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=500,
            key="size_annual_kwh"
        )
        peak_sun = st.slider(
            "Peak Sun Hours",
            min_value=3.0,
            max_value=7.0,
            value=5.0,
            step=0.5,
            key="size_sun_hours"
        )

    with col2:
        perf_ratio = st.slider(
            "Performance Ratio",
            min_value=0.70,
            max_value=0.90,
            value=0.80,
            step=0.05,
            key="size_performance"
        )
        panel_wattage = st.number_input(
            "Panel Wattage (W)",
            min_value=200,
            max_value=600,
            value=400,
            step=25,
            key="size_panel_wattage"
        )

    if st.button("Calculate System Size", type="primary", key="calc_size"):
        params = {
            "annual_kwh": annual_kwh,
            "peak_sun_hours": peak_sun,
            "performance_ratio": perf_ratio,
            "panel_wattage": panel_wattage
        }
        with st.spinner("Calculating..."):
            response = client.calculate(CalculationType.SYSTEM_SIZE, params)

        if response.success:
            data = response.data
            result = data.get("result", {})

            st.markdown("---")
            st.subheader("Sizing Results")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Required System", f"{result.get('system_size_kw', 0):.2f} kW")
            with col2:
                st.metric("Actual System", f"{result.get('actual_size_kw', 0):.2f} kW")
            with col3:
                st.metric("Number of Panels", result.get('number_of_panels', 0))

            if data.get("explanation"):
                with st.expander("Explanation", expanded=True):
                    st.markdown(data["explanation"])
        else:
            st.error(f"Calculation error: {response.error}")

# ROI Calculator
with tabs[2]:
    st.markdown("### Return on Investment Calculator")
    st.markdown("Calculate financial returns and long-term savings for your solar investment.")

    col1, col2 = st.columns(2)

    with col1:
        system_cost = st.number_input(
            "Total System Cost ($)",
            min_value=1000,
            max_value=100000,
            value=15000,
            step=500,
            key="roi_cost"
        )
        annual_production = st.number_input(
            "Annual Production (kWh)",
            min_value=1000,
            max_value=50000,
            value=8000,
            step=500,
            key="roi_production"
        )
        electricity_rate = st.number_input(
            "Electricity Rate ($/kWh)",
            min_value=0.05,
            max_value=0.50,
            value=0.12,
            step=0.01,
            format="%.2f",
            key="roi_rate"
        )

    with col2:
        rate_increase = st.slider(
            "Annual Rate Increase (%)",
            min_value=0,
            max_value=10,
            value=3,
            key="roi_increase"
        )
        incentive = st.slider(
            "Tax Credit / Incentive (%)",
            min_value=0,
            max_value=50,
            value=30,
            key="roi_incentive"
        )

    if st.button("Calculate ROI", type="primary", key="calc_roi"):
        params = {
            "system_cost": system_cost,
            "annual_kwh": annual_production,
            "electricity_rate": electricity_rate,
            "annual_rate_increase": rate_increase / 100,
            "incentive_percent": incentive
        }
        with st.spinner("Calculating..."):
            response = client.calculate(CalculationType.ROI, params)

        if response.success:
            data = response.data
            result = data.get("result", {})

            st.markdown("---")
            st.subheader("Financial Analysis")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Net Cost", f"${result.get('net_system_cost', 0):,.0f}")
            with col2:
                st.metric("Annual Savings", f"${result.get('annual_savings', 0):,.0f}")
            with col3:
                st.metric("25-Year Savings", f"${result.get('total_savings_25yr', 0):,.0f}")
            with col4:
                st.metric("ROI", f"{result.get('roi_percent', 0):.0f}%")

            if data.get("explanation"):
                with st.expander("Explanation", expanded=True):
                    st.markdown(data["explanation"])
        else:
            st.error(f"Calculation error: {response.error}")

# Payback Period Calculator
with tabs[3]:
    st.markdown("### Payback Period Calculator")
    st.markdown("Calculate how long it will take to recoup your solar investment.")

    col1, col2 = st.columns(2)

    with col1:
        pb_cost = st.number_input(
            "System Cost ($)",
            min_value=1000,
            max_value=100000,
            value=15000,
            step=500,
            key="pb_cost"
        )
        pb_production = st.number_input(
            "Annual Production (kWh)",
            min_value=1000,
            max_value=50000,
            value=8000,
            step=500,
            key="pb_production"
        )

    with col2:
        pb_rate = st.number_input(
            "Electricity Rate ($/kWh)",
            min_value=0.05,
            max_value=0.50,
            value=0.12,
            step=0.01,
            format="%.2f",
            key="pb_rate"
        )
        pb_incentive = st.slider(
            "Tax Credit (%)",
            min_value=0,
            max_value=50,
            value=30,
            key="pb_incentive"
        )

    if st.button("Calculate Payback", type="primary", key="calc_pb"):
        params = {
            "system_cost": pb_cost,
            "annual_kwh": pb_production,
            "electricity_rate": pb_rate,
            "incentive_percent": pb_incentive
        }
        with st.spinner("Calculating..."):
            response = client.calculate(CalculationType.PAYBACK_PERIOD, params)

        if response.success:
            data = response.data
            result = data.get("result", {})

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Net Cost", f"${result.get('net_cost', 0):,.0f}")
            with col2:
                st.metric("Annual Savings", f"${result.get('annual_savings', 0):,.0f}")
            with col3:
                st.metric("Payback Period", f"{result.get('payback_years', 0):.1f} years")

            if data.get("explanation"):
                with st.expander("Explanation", expanded=True):
                    st.markdown(data["explanation"])
        else:
            st.error(f"Calculation error: {response.error}")

# Panel Count Calculator
with tabs[4]:
    st.markdown("### Panel Count Calculator")
    st.markdown("Calculate how many panels you need for your energy goals.")

    col1, col2 = st.columns(2)

    with col1:
        target_kwh = st.number_input(
            "Target Annual Production (kWh)",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=500,
            key="panel_target"
        )
        panel_watts = st.number_input(
            "Panel Wattage (W)",
            min_value=200,
            max_value=600,
            value=400,
            step=25,
            key="panel_watts"
        )

    with col2:
        sun_hours = st.slider(
            "Peak Sun Hours",
            min_value=3.0,
            max_value=7.0,
            value=5.0,
            step=0.5,
            key="panel_sun"
        )
        efficiency = st.slider(
            "Efficiency Factor",
            min_value=0.70,
            max_value=0.90,
            value=0.80,
            step=0.05,
            key="panel_efficiency"
        )

    if st.button("Calculate Panels", type="primary", key="calc_panels"):
        params = {
            "target_kwh_annual": target_kwh,
            "panel_wattage": panel_watts,
            "peak_sun_hours": sun_hours,
            "efficiency_factor": efficiency
        }
        with st.spinner("Calculating..."):
            response = client.calculate(CalculationType.PANEL_COUNT, params)

        if response.success:
            data = response.data
            result = data.get("result", {})

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Panels Needed", result.get('panel_count', 0))
            with col2:
                st.metric("Total System Size", f"{result.get('system_size_kw', 0):.2f} kW")

            if data.get("explanation"):
                with st.expander("Explanation", expanded=True):
                    st.markdown(data["explanation"])
        else:
            st.error(f"Calculation error: {response.error}")

# Inverter Size Calculator
with tabs[5]:
    st.markdown("### Inverter Size Calculator")
    st.markdown("Determine the appropriate inverter size for your solar array.")

    col1, col2 = st.columns(2)

    with col1:
        array_size = st.number_input(
            "Array Size (kW DC)",
            min_value=1.0,
            max_value=100.0,
            value=6.0,
            step=0.5,
            key="inv_array"
        )

    with col2:
        dc_ac_ratio = st.slider(
            "DC/AC Ratio",
            min_value=1.0,
            max_value=1.5,
            value=1.2,
            step=0.05,
            key="inv_ratio",
            help="Typical range: 1.1-1.3 for residential systems"
        )

    if st.button("Calculate Inverter Size", type="primary", key="calc_inv"):
        params = {
            "array_size_kw": array_size,
            "dc_ac_ratio": dc_ac_ratio
        }
        with st.spinner("Calculating..."):
            response = client.calculate(CalculationType.INVERTER_SIZE, params)

        if response.success:
            data = response.data
            result = data.get("result", {})

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Inverter Size", f"{result.get('inverter_size_kw', 0):.2f} kW")
            with col2:
                st.metric("DC/AC Ratio", f"{result.get('dc_ac_ratio', 0):.2f}")

            if data.get("explanation"):
                with st.expander("Explanation", expanded=True):
                    st.markdown(data["explanation"])
        else:
            st.error(f"Calculation error: {response.error}")

# Battery Size Calculator
with tabs[6]:
    st.markdown("### Battery Size Calculator")
    st.markdown("Calculate the battery capacity needed for your backup power requirements.")

    col1, col2 = st.columns(2)

    with col1:
        daily_usage = st.number_input(
            "Daily Energy Usage (kWh)",
            min_value=5.0,
            max_value=200.0,
            value=30.0,
            step=1.0,
            key="bat_usage"
        )
        backup_days = st.slider(
            "Backup Days",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.5,
            key="bat_days"
        )

    with col2:
        dod = st.slider(
            "Depth of Discharge (%)",
            min_value=50,
            max_value=95,
            value=80,
            key="bat_dod",
            help="Typical DoD for lithium-ion: 80-90%"
        )
        backup_pct = st.slider(
            "Backup Percentage (%)",
            min_value=25,
            max_value=100,
            value=100,
            key="bat_pct",
            help="Percentage of daily usage to back up"
        )

    if st.button("Calculate Battery Size", type="primary", key="calc_bat"):
        params = {
            "daily_kwh": daily_usage,
            "backup_days": backup_days,
            "depth_of_discharge": dod / 100,
            "backup_percentage": backup_pct
        }
        with st.spinner("Calculating..."):
            response = client.calculate(CalculationType.BATTERY_SIZE, params)

        if response.success:
            data = response.data
            result = data.get("result", {})

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Battery Capacity", f"{result.get('battery_size_kwh', 0):.1f} kWh")
            with col2:
                st.metric("Usable Capacity", f"{result.get('usable_capacity_kwh', 0):.1f} kWh")

            if data.get("explanation"):
                with st.expander("Explanation", expanded=True):
                    st.markdown(data["explanation"])
        else:
            st.error(f"Calculation error: {response.error}")

# Footer with tips
st.markdown("---")
st.markdown("### Tips for Accurate Calculations")
tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.markdown("""
    **Location Factors:**
    - Peak sun hours vary by region
    - Northern regions: 3-4 hours
    - Moderate climates: 4-5 hours
    - Sunny regions: 5-7 hours
    """)

with tips_col2:
    st.markdown("""
    **System Considerations:**
    - Include 10-20% buffer for future needs
    - Performance degrades ~0.5% per year
    - Consider shading and orientation
    - Account for seasonal variations
    """)
