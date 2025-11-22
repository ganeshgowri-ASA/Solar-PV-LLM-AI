"""Calculator router for Solar PV calculations."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models.schemas import CalculatorRequest, CalculatorResponse, CalculationType

router = APIRouter(prefix="/calculate", tags=["Calculator"])


def calculate_system_size(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate required system size."""
    annual_kwh = params.get("annual_kwh", 10000)
    peak_sun_hours = params.get("peak_sun_hours", 5)
    performance_ratio = params.get("performance_ratio", 0.80)

    system_size_kw = annual_kwh / (peak_sun_hours * 365 * performance_ratio)
    panel_wattage = params.get("panel_wattage", 400)
    num_panels = int(system_size_kw * 1000 / panel_wattage) + 1

    return {
        "system_size_kw": round(system_size_kw, 2),
        "number_of_panels": num_panels,
        "total_wattage_dc": num_panels * panel_wattage
    }


def calculate_energy_output(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate expected energy output."""
    system_size_kw = params.get("system_size_kw", 6)
    peak_sun_hours = params.get("peak_sun_hours", 5)
    performance_ratio = params.get("performance_ratio", 0.80)

    daily_kwh = system_size_kw * peak_sun_hours * performance_ratio
    monthly_kwh = daily_kwh * 30
    annual_kwh = daily_kwh * 365

    return {
        "daily_kwh": round(daily_kwh, 2),
        "monthly_kwh": round(monthly_kwh, 2),
        "annual_kwh": round(annual_kwh, 2)
    }


def calculate_roi(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate return on investment."""
    system_cost = params.get("system_cost", 15000)
    annual_kwh = params.get("annual_kwh", 8000)
    electricity_rate = params.get("electricity_rate", 0.12)
    annual_rate_increase = params.get("annual_rate_increase", 0.03)
    incentive_percent = params.get("incentive_percent", 30)

    # Calculate net cost after incentives
    incentive_amount = system_cost * (incentive_percent / 100)
    net_cost = system_cost - incentive_amount

    # Calculate savings over 25 years
    total_savings = 0
    current_rate = electricity_rate
    for year in range(1, 26):
        annual_savings = annual_kwh * current_rate
        total_savings += annual_savings
        current_rate *= (1 + annual_rate_increase)

    roi_percent = ((total_savings - net_cost) / net_cost) * 100

    return {
        "net_system_cost": round(net_cost, 2),
        "incentive_amount": round(incentive_amount, 2),
        "total_25_year_savings": round(total_savings, 2),
        "roi_percent": round(roi_percent, 1),
        "lifetime_net_benefit": round(total_savings - net_cost, 2)
    }


def calculate_payback_period(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate payback period."""
    system_cost = params.get("system_cost", 15000)
    annual_kwh = params.get("annual_kwh", 8000)
    electricity_rate = params.get("electricity_rate", 0.12)
    incentive_percent = params.get("incentive_percent", 30)

    net_cost = system_cost * (1 - incentive_percent / 100)
    annual_savings = annual_kwh * electricity_rate
    payback_years = net_cost / annual_savings

    return {
        "payback_years": round(payback_years, 1),
        "annual_savings": round(annual_savings, 2),
        "net_cost": round(net_cost, 2)
    }


def calculate_panel_count(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate number of panels needed."""
    target_kwh_annual = params.get("target_kwh_annual", 10000)
    panel_wattage = params.get("panel_wattage", 400)
    peak_sun_hours = params.get("peak_sun_hours", 5)
    efficiency_factor = params.get("efficiency_factor", 0.80)

    daily_kwh_needed = target_kwh_annual / 365
    kw_needed = daily_kwh_needed / (peak_sun_hours * efficiency_factor)
    panels_needed = int((kw_needed * 1000) / panel_wattage) + 1

    # Estimate roof space (assuming 17.5 sq ft per panel)
    roof_space_sqft = panels_needed * 17.5

    return {
        "panels_needed": panels_needed,
        "total_wattage": panels_needed * panel_wattage,
        "estimated_roof_space_sqft": round(roof_space_sqft, 1),
        "system_size_kw": round(panels_needed * panel_wattage / 1000, 2)
    }


def calculate_inverter_size(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate recommended inverter size."""
    array_size_kw = params.get("array_size_kw", 6)
    dc_ac_ratio = params.get("dc_ac_ratio", 1.2)

    inverter_size = array_size_kw / dc_ac_ratio
    min_size = array_size_kw * 0.75
    max_size = array_size_kw * 1.0

    return {
        "recommended_inverter_kw": round(inverter_size, 2),
        "min_inverter_kw": round(min_size, 2),
        "max_inverter_kw": round(max_size, 2),
        "dc_ac_ratio": dc_ac_ratio
    }


def calculate_battery_size(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate battery storage size."""
    daily_kwh = params.get("daily_kwh", 30)
    backup_days = params.get("backup_days", 1)
    depth_of_discharge = params.get("depth_of_discharge", 0.80)
    backup_percentage = params.get("backup_percentage", 100)

    backup_kwh = daily_kwh * (backup_percentage / 100)
    usable_capacity = backup_kwh * backup_days
    total_capacity = usable_capacity / depth_of_discharge

    # Assuming 48V battery system
    battery_voltage = params.get("battery_voltage", 48)
    amp_hours = (total_capacity * 1000) / battery_voltage

    return {
        "total_capacity_kwh": round(total_capacity, 2),
        "usable_capacity_kwh": round(usable_capacity, 2),
        "amp_hours_at_48v": round(amp_hours, 1),
        "backup_hours": round(backup_days * 24, 1)
    }


CALCULATION_FUNCTIONS = {
    CalculationType.SYSTEM_SIZE: calculate_system_size,
    CalculationType.ENERGY_OUTPUT: calculate_energy_output,
    CalculationType.ROI: calculate_roi,
    CalculationType.PAYBACK_PERIOD: calculate_payback_period,
    CalculationType.PANEL_COUNT: calculate_panel_count,
    CalculationType.INVERTER_SIZE: calculate_inverter_size,
    CalculationType.BATTERY_SIZE: calculate_battery_size,
}

CALCULATION_UNITS = {
    CalculationType.SYSTEM_SIZE: "kW",
    CalculationType.ENERGY_OUTPUT: "kWh",
    CalculationType.ROI: "%",
    CalculationType.PAYBACK_PERIOD: "years",
    CalculationType.PANEL_COUNT: "panels",
    CalculationType.INVERTER_SIZE: "kW",
    CalculationType.BATTERY_SIZE: "kWh",
}

EXPLANATIONS = {
    CalculationType.SYSTEM_SIZE: """
**System Size Calculation**

The system size is calculated using:
```
System Size (kW) = Annual kWh / (Peak Sun Hours × 365 × Performance Ratio)
```

Where:
- **Annual kWh**: Your total yearly electricity consumption
- **Peak Sun Hours**: Average daily hours of peak sunlight (varies by location)
- **Performance Ratio**: System efficiency factor (typically 0.75-0.85)
""",
    CalculationType.ENERGY_OUTPUT: """
**Energy Output Calculation**

Expected energy output is calculated using:
```
Daily kWh = System Size (kW) × Peak Sun Hours × Performance Ratio
```

This accounts for:
- System capacity
- Local solar resource
- Real-world efficiency losses
""",
    CalculationType.ROI: """
**Return on Investment Calculation**

ROI is calculated considering:
1. Net system cost after incentives (e.g., 30% federal tax credit)
2. Annual electricity savings
3. Projected rate increases over 25 years
4. Total lifetime savings vs. initial investment
""",
    CalculationType.PAYBACK_PERIOD: """
**Payback Period Calculation**

Simple payback period:
```
Payback Years = Net System Cost / Annual Savings
```

Where:
- Net System Cost = Total Cost - Incentives
- Annual Savings = Annual kWh × Electricity Rate
""",
    CalculationType.PANEL_COUNT: """
**Panel Count Calculation**

Number of panels is determined by:
1. Calculate required system size based on energy needs
2. Divide by individual panel wattage
3. Round up to ensure adequate production

Roof space is estimated at ~17.5 sq ft per standard panel.
""",
    CalculationType.INVERTER_SIZE: """
**Inverter Sizing**

Inverter size is based on DC/AC ratio:
```
Inverter Size = Array Size (kW) / DC-AC Ratio
```

A DC/AC ratio of 1.1-1.3 is typical, allowing for:
- Clipping during peak production
- Better performance in non-ideal conditions
- Cost optimization
""",
    CalculationType.BATTERY_SIZE: """
**Battery Storage Sizing**

Battery capacity is calculated considering:
1. Daily energy needs to backup
2. Number of backup days required
3. Depth of discharge (typically 80% for lithium)

```
Total Capacity = (Daily kWh × Backup Days) / Depth of Discharge
```
""",
}


@router.post("", response_model=CalculatorResponse)
async def perform_calculation(request: CalculatorRequest):
    """
    Perform a solar PV calculation.

    Args:
        request: Calculation request with type and parameters

    Returns:
        Calculation results with explanations
    """
    try:
        calc_func = CALCULATION_FUNCTIONS.get(request.calculation_type)
        if not calc_func:
            raise HTTPException(status_code=400, detail=f"Unknown calculation type: {request.calculation_type}")

        result = calc_func(request.parameters)

        # Get explanation if requested
        explanation = EXPLANATIONS.get(request.calculation_type, "") if request.include_explanation else None

        # Generate recommendations based on results
        recommendations = _generate_recommendations(request.calculation_type, result, request.parameters)

        # Generate assumptions
        assumptions = _generate_assumptions(request.calculation_type, request.parameters)

        return CalculatorResponse(
            result=result,
            calculation_type=request.calculation_type,
            explanation=explanation,
            assumptions=assumptions,
            recommendations=recommendations,
            unit=CALCULATION_UNITS.get(request.calculation_type, "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


def _generate_recommendations(
    calc_type: CalculationType,
    result: Dict[str, Any],
    params: Dict[str, Any]
) -> list:
    """Generate recommendations based on calculation results."""
    recommendations = []

    if calc_type == CalculationType.SYSTEM_SIZE:
        if result.get("system_size_kw", 0) > 10:
            recommendations.append("Consider a commercial-grade inverter for systems over 10kW")
        recommendations.append("Get multiple quotes from certified installers")
        recommendations.append("Check local utility interconnection requirements")

    elif calc_type == CalculationType.PAYBACK_PERIOD:
        years = result.get("payback_years", 0)
        if years < 6:
            recommendations.append("Excellent payback period! Solar is a great investment for you")
        elif years < 10:
            recommendations.append("Good payback period. Consider financing options to start saving sooner")
        else:
            recommendations.append("Consider higher efficiency panels to improve payback")
            recommendations.append("Look into additional incentives or net metering programs")

    elif calc_type == CalculationType.BATTERY_SIZE:
        recommendations.append("Consider lithium iron phosphate (LFP) batteries for longevity")
        recommendations.append("Ensure your inverter supports battery integration")
        if result.get("total_capacity_kwh", 0) > 20:
            recommendations.append("For large battery systems, consider modular solutions")

    return recommendations


def _generate_assumptions(calc_type: CalculationType, params: Dict[str, Any]) -> list:
    """Generate list of assumptions used in calculation."""
    assumptions = []

    peak_sun = params.get("peak_sun_hours", 5)
    assumptions.append(f"Peak sun hours: {peak_sun} hours/day")

    if "performance_ratio" in params:
        assumptions.append(f"Performance ratio: {params['performance_ratio']}")
    else:
        assumptions.append("Performance ratio: 0.80 (default)")

    if calc_type in [CalculationType.ROI, CalculationType.PAYBACK_PERIOD]:
        assumptions.append(f"Electricity rate: ${params.get('electricity_rate', 0.12)}/kWh")
        if calc_type == CalculationType.ROI:
            assumptions.append("System lifetime: 25 years")
            assumptions.append(f"Annual rate increase: {params.get('annual_rate_increase', 0.03) * 100}%")

    return assumptions


@router.get("/types")
async def get_calculation_types():
    """Get available calculation types with descriptions."""
    return {
        "system_size": "Calculate required system size based on energy needs",
        "energy_output": "Calculate expected energy output from a system",
        "roi": "Calculate return on investment over system lifetime",
        "payback_period": "Calculate simple payback period",
        "panel_count": "Calculate number of panels needed",
        "inverter_size": "Calculate recommended inverter size",
        "battery_size": "Calculate battery storage requirements"
    }


@router.get("/health")
async def calculator_health():
    """Health check for calculator service."""
    return {"status": "healthy", "service": "calculator"}
