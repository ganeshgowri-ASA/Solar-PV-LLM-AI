"""
Calculators Page
Multiple solar PV calculators with real-time results and visualizations
"""
import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from backend.api.mock_service import mock_api
from frontend.utils.ui_components import show_success, show_info


def render():
    """Render the calculators page"""
    st.title("🧮 Solar PV Calculators")
    st.markdown(
        "Professional calculators for system design, performance analysis, and financial planning."
    )

    # Create tabs for different calculators
    tabs = st.tabs([
        "⚡ Energy Yield",
        "📐 System Sizing",
        "💰 ROI Calculator",
        "📊 Efficiency",
        "🌤️ Shading Analysis",
    ])

    # Energy Yield Calculator
    with tabs[0]:
        render_energy_yield_calculator()

    # System Sizing Calculator
    with tabs[1]:
        render_system_sizing_calculator()

    # ROI Calculator
    with tabs[2]:
        render_roi_calculator()

    # Efficiency Calculator
    with tabs[3]:
        render_efficiency_calculator()

    # Shading Analysis
    with tabs[4]:
        render_shading_analysis()


def render_energy_yield_calculator():
    """Energy Yield Calculator"""
    st.markdown("### ⚡ Energy Yield Calculator")
    st.markdown("Calculate expected energy production based on system size and location.")

    col1, col2 = st.columns(2)

    with col1:
        system_size = st.number_input(
            "System Size (kW)",
            min_value=1.0,
            max_value=10000.0,
            value=5.0,
            step=0.5,
        )

        location_irradiance = st.number_input(
            "Average Daily Irradiance (kWh/m²/day)",
            min_value=1.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Typical values: 3-4 for northern regions, 5-6 for moderate climates, 6-7 for sunny regions",
        )

    with col2:
        performance_ratio = st.slider(
            "Performance Ratio",
            min_value=0.5,
            max_value=1.0,
            value=0.8,
            step=0.05,
            help="Typical range: 0.75-0.85 for well-designed systems",
        )

        show_chart = st.checkbox("Show Monthly Breakdown", value=True)

    if st.button("Calculate Energy Yield", type="primary", use_container_width=True):
        results = mock_api.calculate_energy_yield(
            system_size, location_irradiance, performance_ratio
        )

        st.divider()
        st.markdown("### 📊 Results")

        # Display metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            st.metric(
                "Daily Energy",
                f"{results['daily_energy_kwh']:.1f} kWh",
                help="Average daily energy production",
            )

        with metric_col2:
            st.metric(
                "Monthly Energy",
                f"{results['monthly_energy_kwh']:.0f} kWh",
                help="Average monthly energy production",
            )

        with metric_col3:
            st.metric(
                "Annual Energy",
                f"{results['annual_energy_mwh']:.2f} MWh",
                help="Total annual energy production",
            )

        with metric_col4:
            st.metric(
                "CO₂ Offset",
                f"{results['co2_offset_kg']:.0f} kg",
                help="Annual CO₂ emissions offset",
            )

        if show_chart:
            # Generate monthly data
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            monthly_variation = [0.7, 0.8, 0.9, 1.0, 1.1, 1.15, 1.2, 1.15, 1.0, 0.9, 0.75, 0.7]
            monthly_energy = [
                results["monthly_energy_kwh"] * var for var in monthly_variation
            ]

            # Create chart
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=months,
                    y=monthly_energy,
                    marker_color="#667eea",
                    text=[f"{val:.0f}" for val in monthly_energy],
                    textposition="outside",
                )
            )
            fig.update_layout(
                title="Monthly Energy Production (kWh)",
                xaxis_title="Month",
                yaxis_title="Energy (kWh)",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)


def render_system_sizing_calculator():
    """System Sizing Calculator"""
    st.markdown("### 📐 System Sizing Calculator")
    st.markdown("Determine the optimal system size based on your energy needs.")

    col1, col2 = st.columns(2)

    with col1:
        daily_consumption = st.number_input(
            "Daily Energy Consumption (kWh)",
            min_value=1.0,
            max_value=1000.0,
            value=30.0,
            step=1.0,
        )

        peak_sun_hours = st.number_input(
            "Peak Sun Hours",
            min_value=1.0,
            max_value=10.0,
            value=5.0,
            step=0.5,
            help="Average daily peak sun hours for your location",
        )

    with col2:
        system_efficiency = st.slider(
            "System Efficiency",
            min_value=0.5,
            max_value=1.0,
            value=0.8,
            step=0.05,
        )

        autonomy_days = st.number_input(
            "Autonomy Days (with battery)",
            min_value=0,
            max_value=7,
            value=0,
            help="Days of backup power with battery storage",
        )

    if st.button("Calculate System Size", type="primary", use_container_width=True):
        results = mock_api.calculate_system_sizing(
            daily_consumption, peak_sun_hours, system_efficiency
        )

        st.divider()
        st.markdown("### 📊 Sizing Results")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Required System",
                f"{results['required_system_size_kw']:.2f} kW",
            )

        with col2:
            st.metric("Number of Panels", results["recommended_panels"])

        with col3:
            st.metric(
                "Total Capacity",
                f"{results['total_system_size_kw']:.2f} kW",
            )

        with col4:
            st.metric(
                "Roof Area",
                f"{results['estimated_roof_area_m2']:.1f} m²",
            )

        # System composition chart
        st.markdown("### 📦 System Composition")

        composition_data = {
            "Component": [
                "Solar Panels",
                "Inverter",
                "Mounting",
                "Wiring & Protection",
                "Monitoring",
            ],
            "Cost Share (%)": [60, 15, 10, 10, 5],
        }

        fig = px.pie(
            composition_data,
            values="Cost Share (%)",
            names="Component",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


def render_roi_calculator():
    """ROI Calculator"""
    st.markdown("### 💰 Return on Investment Calculator")
    st.markdown("Calculate financial returns and payback period for your solar investment.")

    col1, col2 = st.columns(2)

    with col1:
        system_cost = st.number_input(
            "Total System Cost ($)",
            min_value=1000.0,
            max_value=1000000.0,
            value=15000.0,
            step=500.0,
        )

        annual_savings = st.number_input(
            "Annual Energy Savings ($)",
            min_value=100.0,
            max_value=100000.0,
            value=2000.0,
            step=100.0,
        )

    with col2:
        electricity_rate_increase = st.slider(
            "Annual Electricity Rate Increase (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.5,
        ) / 100

        incentives = st.number_input(
            "Government Incentives/Tax Credits ($)",
            min_value=0.0,
            max_value=100000.0,
            value=3000.0,
            step=500.0,
        )

    if st.button("Calculate ROI", type="primary", use_container_width=True):
        net_cost = system_cost - incentives
        adjusted_annual_savings = annual_savings

        results = mock_api.calculate_roi(
            net_cost, adjusted_annual_savings, electricity_rate_increase
        )

        st.divider()
        st.markdown("### 💵 Financial Analysis")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Payback Period",
                f"{results['payback_period_years']:.1f} years",
            )

        with col2:
            st.metric(
                "25-Year ROI",
                f"{results['roi_percentage']:.1f}%",
            )

        with col3:
            st.metric(
                "Total Savings",
                f"${results['total_savings_25_years']:,.0f}",
            )

        with col4:
            st.metric(
                "Net Profit",
                f"${results['net_profit_25_years']:,.0f}",
                delta="25 years",
            )

        # Cumulative savings chart
        years = list(range(26))
        cumulative_savings = []
        total = -net_cost

        for year in years:
            total += adjusted_annual_savings * ((1 + electricity_rate_increase) ** year)
            cumulative_savings.append(total)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=years,
                y=cumulative_savings,
                mode="lines+markers",
                fill="tozeroy",
                line=dict(color="#667eea", width=3),
                marker=dict(size=6),
            )
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_layout(
            title="Cumulative Cash Flow Over 25 Years",
            xaxis_title="Year",
            yaxis_title="Cumulative Savings ($)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


def render_efficiency_calculator():
    """Efficiency Calculator"""
    st.markdown("### 📊 Solar Panel Efficiency Calculator")
    st.markdown("Calculate module and system efficiency based on performance data.")

    col1, col2 = st.columns(2)

    with col1:
        max_power = st.number_input(
            "Maximum Power Output (W)",
            min_value=1.0,
            max_value=1000.0,
            value=400.0,
            step=10.0,
        )

        module_area = st.number_input(
            "Module Area (m²)",
            min_value=0.1,
            max_value=10.0,
            value=2.0,
            step=0.1,
        )

    with col2:
        irradiance = st.number_input(
            "Irradiance (W/m²)",
            min_value=100.0,
            max_value=1500.0,
            value=1000.0,
            step=50.0,
            help="Standard Test Conditions use 1000 W/m²",
        )

        temperature = st.number_input(
            "Module Temperature (°C)",
            min_value=-40.0,
            max_value=85.0,
            value=25.0,
            step=1.0,
        )

    if st.button("Calculate Efficiency", type="primary", use_container_width=True):
        module_efficiency = (max_power / (module_area * irradiance)) * 100

        # Temperature derating
        temp_coefficient = -0.4  # %/°C (typical for Si)
        temp_loss = (temperature - 25) * temp_coefficient
        actual_efficiency = module_efficiency * (1 + temp_loss / 100)

        st.divider()
        st.markdown("### ⚡ Efficiency Results")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Module Efficiency",
                f"{module_efficiency:.2f}%",
                help="At STC (25°C)",
            )

        with col2:
            st.metric(
                "Actual Efficiency",
                f"{actual_efficiency:.2f}%",
                delta=f"{temp_loss:.2f}%",
                help="At operating temperature",
            )

        with col3:
            st.metric(
                "Power Density",
                f"{max_power / module_area:.1f} W/m²",
            )

        with col4:
            quality_rating = "Excellent" if module_efficiency > 20 else "Good" if module_efficiency > 18 else "Standard"
            st.metric("Quality Rating", quality_rating)

        # Temperature performance curve
        temps = list(range(-10, 86, 5))
        efficiencies = [
            module_efficiency * (1 + (t - 25) * temp_coefficient / 100)
            for t in temps
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=temps,
                y=efficiencies,
                mode="lines",
                line=dict(color="#667eea", width=3),
                fill="tozeroy",
            )
        )
        fig.add_vline(x=25, line_dash="dash", line_color="green", annotation_text="STC")
        fig.add_vline(
            x=temperature, line_dash="dash", line_color="red", annotation_text="Operating"
        )
        fig.update_layout(
            title="Efficiency vs Temperature",
            xaxis_title="Temperature (°C)",
            yaxis_title="Efficiency (%)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


def render_shading_analysis():
    """Shading Analysis Calculator"""
    st.markdown("### 🌤️ Shading Analysis Calculator")
    st.markdown("Estimate energy losses due to shading and optimize panel placement.")

    st.info(
        "⚠️ This is a simplified shading calculator. For detailed analysis, "
        "use professional software or consult with a solar installer."
    )

    col1, col2 = st.columns(2)

    with col1:
        annual_production = st.number_input(
            "Unshaded Annual Production (kWh)",
            min_value=100.0,
            max_value=100000.0,
            value=7500.0,
            step=100.0,
        )

        shading_morning = st.slider(
            "Morning Shading (%)",
            min_value=0,
            max_value=100,
            value=10,
        )

    with col2:
        shading_midday = st.slider(
            "Midday Shading (%)",
            min_value=0,
            max_value=100,
            value=5,
        )

        shading_evening = st.slider(
            "Evening Shading (%)",
            min_value=0,
            max_value=100,
            value=15,
        )

    # Time of day weights (midday has more production)
    morning_weight = 0.25
    midday_weight = 0.50
    evening_weight = 0.25

    total_loss = (
        shading_morning * morning_weight
        + shading_midday * midday_weight
        + shading_evening * evening_weight
    )

    actual_production = annual_production * (1 - total_loss / 100)
    energy_loss = annual_production - actual_production

    st.divider()
    st.markdown("### 🌥️ Shading Impact")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Loss",
            f"{total_loss:.1f}%",
            delta=f"-{energy_loss:.0f} kWh",
            delta_color="inverse",
        )

    with col2:
        st.metric("Actual Production", f"{actual_production:.0f} kWh")

    with col3:
        value_loss = energy_loss * 0.12  # Assume $0.12/kWh
        st.metric("Annual Value Loss", f"${value_loss:.0f}")

    with col4:
        severity = "Critical" if total_loss > 20 else "Moderate" if total_loss > 10 else "Minor"
        st.metric("Impact Severity", severity)

    # Shading distribution chart
    shading_data = pd.DataFrame({
        "Time Period": ["Morning\n(6-10am)", "Midday\n(10am-3pm)", "Evening\n(3-7pm)"],
        "Shading (%)": [shading_morning, shading_midday, shading_evening],
        "Production Weight": [morning_weight * 100, midday_weight * 100, evening_weight * 100],
    })

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Shading %",
            x=shading_data["Time Period"],
            y=shading_data["Shading (%)"],
            marker_color="#ff6b6b",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Production Weight %",
            x=shading_data["Time Period"],
            y=shading_data["Production Weight"],
            marker_color="#667eea",
        )
    )
    fig.update_layout(
        title="Shading vs Production Distribution",
        xaxis_title="Time Period",
        yaxis_title="Percentage (%)",
        barmode="group",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Recommendations
    st.markdown("### 💡 Recommendations")
    if total_loss > 20:
        st.error(
            "⚠️ High shading losses detected. Consider:\n"
            "- Trimming nearby trees\n"
            "- Relocating panels to unshaded areas\n"
            "- Using micro-inverters or power optimizers"
        )
    elif total_loss > 10:
        st.warning(
            "⚡ Moderate shading losses. Consider:\n"
            "- Seasonal tree trimming\n"
            "- Panel-level electronics for better performance\n"
            "- Regular monitoring"
        )
    else:
        st.success(
            "✅ Low shading impact. System should perform well.\n"
            "Continue monitoring and maintain clear surroundings."
        )
