"""
IEC TS 60904-13 Defect Categorizer Module

Categorizes PV panel defects according to IEC TS 60904-13 standard
for electroluminescence imaging and provides standardized recommendations.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class DefectSeverity(Enum):
    """Defect severity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DefectCategory(Enum):
    """IEC TS 60904-13 based defect categories"""
    # Cell defects
    CELL_CRACK = "Cell Crack"
    MICRO_CRACK = "Micro-crack"
    CORNER_CRACK = "Corner Crack"
    DIAGONAL_CRACK = "Diagonal Crack"
    MULTI_CRACK = "Multiple Cracks"

    # Cell degradation
    INACTIVE_AREA = "Inactive Cell Area"
    DARK_AREA = "Dark Area"
    DEAD_CELL = "Dead Cell"
    PID = "Potential Induced Degradation"

    # Electrical defects
    FINGER_INTERRUPTION = "Finger Interruption"
    BUSBAR_INTERRUPTION = "Busbar Interruption"
    SOLDERING_FAULT = "Soldering Fault"
    SHUNT = "Shunt"

    # Thermal defects
    HOTSPOT = "Hotspot"
    BYPASS_DIODE_FAILURE = "Bypass Diode Failure"

    # Physical/material defects
    DELAMINATION = "Delamination"
    DISCOLORATION = "Discoloration"
    SNAIL_TRAIL = "Snail Trail"
    BURN_MARK = "Burn Mark"
    CORROSION = "Corrosion"

    # No defect
    NO_DEFECT = "No Defect"


@dataclass
class IECDefectClassification:
    """Structured defect classification based on IEC standards"""
    category: DefectCategory
    severity: DefectSeverity
    description: str
    performance_impact: str  # Percentage or qualitative
    detection_method: str  # EL, IR, Visual, IV
    recommended_action: str
    failure_mode: str
    standard_reference: str


class IECDefectCategorizer:
    """
    Categorizes and provides recommendations for PV defects
    based on IEC TS 60904-13 and related standards.
    """

    # IEC-based defect database
    DEFECT_DATABASE = {
        DefectCategory.CELL_CRACK: IECDefectClassification(
            category=DefectCategory.CELL_CRACK,
            severity=DefectSeverity.HIGH,
            description="Visible crack in solar cell, potentially affecting current collection",
            performance_impact="5-30% power loss per affected cell",
            detection_method="EL imaging, Visual inspection",
            recommended_action="Monitor for propagation; consider replacement if multiple cells affected",
            failure_mode="Progressive crack growth leading to cell isolation",
            standard_reference="IEC TS 60904-13 Section 5.2.1"
        ),

        DefectCategory.MICRO_CRACK: IECDefectClassification(
            category=DefectCategory.MICRO_CRACK,
            severity=DefectSeverity.MEDIUM,
            description="Hairline crack visible only in EL imaging, not visible to naked eye",
            performance_impact="1-10% power loss per cell",
            detection_method="EL imaging",
            recommended_action="Monitor during regular inspections; may propagate under thermal cycling",
            failure_mode="Can develop into major cracks under mechanical/thermal stress",
            standard_reference="IEC TS 60904-13 Section 5.2.2"
        ),

        DefectCategory.CORNER_CRACK: IECDefectClassification(
            category=DefectCategory.CORNER_CRACK,
            severity=DefectSeverity.LOW,
            description="Crack originating from cell corner, often from handling during manufacturing",
            performance_impact="0-5% power loss",
            detection_method="EL imaging, Visual inspection",
            recommended_action="Monitor only; minimal immediate impact",
            failure_mode="Low risk of propagation if confined to corner",
            standard_reference="IEC TS 60904-13 Section 5.2.3"
        ),

        DefectCategory.DIAGONAL_CRACK: IECDefectClassification(
            category=DefectCategory.DIAGONAL_CRACK,
            severity=DefectSeverity.HIGH,
            description="Diagonal crack across cell, often from mechanical stress",
            performance_impact="10-40% power loss per cell",
            detection_method="EL imaging, Visual inspection",
            recommended_action="Priority repair or replacement; high risk of complete cell failure",
            failure_mode="Rapid progression leading to cell separation",
            standard_reference="IEC TS 60904-13 Section 5.2.4"
        ),

        DefectCategory.MULTI_CRACK: IECDefectClassification(
            category=DefectCategory.MULTI_CRACK,
            severity=DefectSeverity.CRITICAL,
            description="Multiple intersecting cracks in single cell",
            performance_impact="30-80% power loss per cell",
            detection_method="EL imaging, Visual inspection",
            recommended_action="Immediate replacement recommended",
            failure_mode="High probability of complete cell failure",
            standard_reference="IEC TS 60904-13 Section 5.2.5"
        ),

        DefectCategory.INACTIVE_AREA: IECDefectClassification(
            category=DefectCategory.INACTIVE_AREA,
            severity=DefectSeverity.MEDIUM,
            description="Region of cell showing no or reduced electroluminescence",
            performance_impact="Proportional to inactive area size",
            detection_method="EL imaging",
            recommended_action="Investigate cause; monitor for growth",
            failure_mode="May indicate manufacturing defect or degradation",
            standard_reference="IEC TS 60904-13 Section 5.3.1"
        ),

        DefectCategory.DARK_AREA: IECDefectClassification(
            category=DefectCategory.DARK_AREA,
            severity=DefectSeverity.MEDIUM,
            description="Area with significantly reduced EL signal",
            performance_impact="5-25% power loss depending on area",
            detection_method="EL imaging",
            recommended_action="Check for shadowing or electrical issues",
            failure_mode="Potential current collection problem",
            standard_reference="IEC TS 60904-13 Section 5.3.2"
        ),

        DefectCategory.DEAD_CELL: IECDefectClassification(
            category=DefectCategory.DEAD_CELL,
            severity=DefectSeverity.CRITICAL,
            description="Cell showing no electroluminescence signal",
            performance_impact="100% power loss for affected cell; module performance reduced",
            detection_method="EL imaging, IR imaging",
            recommended_action="Module replacement or repair required",
            failure_mode="Complete cell failure, bypass diode activation",
            standard_reference="IEC TS 60904-13 Section 5.3.3"
        ),

        DefectCategory.PID: IECDefectClassification(
            category=DefectCategory.PID,
            severity=DefectSeverity.HIGH,
            description="Potential Induced Degradation - voltage stress degradation",
            performance_impact="10-90% module power loss over time",
            detection_method="EL imaging, IV curve analysis",
            recommended_action="Implement PID mitigation strategies; consider grounding changes",
            failure_mode="Progressive performance degradation",
            standard_reference="IEC TS 62804 (PID testing)"
        ),

        DefectCategory.FINGER_INTERRUPTION: IECDefectClassification(
            category=DefectCategory.FINGER_INTERRUPTION,
            severity=DefectSeverity.MEDIUM,
            description="Broken or disconnected finger contact on cell",
            performance_impact="2-15% power loss per affected cell",
            detection_method="EL imaging",
            recommended_action="Monitor; consider repair if multiple fingers affected",
            failure_mode="Reduced current collection efficiency",
            standard_reference="IEC TS 60904-13 Section 5.4.1"
        ),

        DefectCategory.BUSBAR_INTERRUPTION: IECDefectClassification(
            category=DefectCategory.BUSBAR_INTERRUPTION,
            severity=DefectSeverity.CRITICAL,
            description="Break or disconnection in main busbar",
            performance_impact="50-100% power loss for affected substring",
            detection_method="EL imaging, IR imaging",
            recommended_action="Immediate repair or module replacement",
            failure_mode="Complete substring failure",
            standard_reference="IEC TS 60904-13 Section 5.4.2"
        ),

        DefectCategory.SOLDERING_FAULT: IECDefectClassification(
            category=DefectCategory.SOLDERING_FAULT,
            severity=DefectSeverity.MEDIUM,
            description="Poor solder connection at cell interconnect",
            performance_impact="5-20% power loss",
            detection_method="EL imaging, IR imaging (hotspot)",
            recommended_action="Monitor for hotspot development; repair if worsening",
            failure_mode="Increased resistance, potential hotspot formation",
            standard_reference="IEC TS 60904-13 Section 5.4.3"
        ),

        DefectCategory.SHUNT: IECDefectClassification(
            category=DefectCategory.SHUNT,
            severity=DefectSeverity.HIGH,
            description="Localized shunt resistance creating current leakage path",
            performance_impact="10-40% power loss",
            detection_method="EL imaging (bright spots), IR imaging",
            recommended_action="Monitor for thermal runaway; consider module isolation",
            failure_mode="Potential fire hazard, progressive degradation",
            standard_reference="IEC TS 60904-13 Section 5.5.1"
        ),

        DefectCategory.HOTSPOT: IECDefectClassification(
            category=DefectCategory.HOTSPOT,
            severity=DefectSeverity.CRITICAL,
            description="Localized area of elevated temperature",
            performance_impact="20-60% local power loss, potential damage",
            detection_method="IR thermal imaging",
            recommended_action="Immediate investigation and remediation required",
            failure_mode="Fire hazard, accelerated degradation, potential safety issue",
            standard_reference="IEC TS 60904-13 Section 6.2.1"
        ),

        DefectCategory.BYPASS_DIODE_FAILURE: IECDefectClassification(
            category=DefectCategory.BYPASS_DIODE_FAILURE,
            severity=DefectSeverity.CRITICAL,
            description="Bypass diode short-circuit or open-circuit failure",
            performance_impact="Substring power loss or hotspot risk",
            detection_method="IR imaging, IV curve analysis",
            recommended_action="Immediate replacement of junction box or module",
            failure_mode="Hotspot formation, potential fire hazard",
            standard_reference="IEC 61215 Section 10.17"
        ),

        DefectCategory.DELAMINATION: IECDefectClassification(
            category=DefectCategory.DELAMINATION,
            severity=DefectSeverity.HIGH,
            description="Separation of encapsulant layers",
            performance_impact="Progressive degradation, moisture ingress risk",
            detection_method="Visual inspection, IR imaging",
            recommended_action="Monitor for growth; replace if extensive",
            failure_mode="Moisture ingress leading to corrosion and electrical failure",
            standard_reference="IEC 61215 Section 10.13"
        ),

        DefectCategory.DISCOLORATION: IECDefectClassification(
            category=DefectCategory.DISCOLORATION,
            severity=DefectSeverity.MEDIUM,
            description="Browning or yellowing of encapsulant material",
            performance_impact="5-15% power loss due to reduced light transmission",
            detection_method="Visual inspection",
            recommended_action="Monitor for progression; acceptable if stable",
            failure_mode="Progressive light absorption, potential delamination",
            standard_reference="IEC 61215 Section 10.10"
        ),

        DefectCategory.SNAIL_TRAIL: IECDefectClassification(
            category=DefectCategory.SNAIL_TRAIL,
            severity=DefectSeverity.LOW,
            description="Brown discoloration pattern along cracks",
            performance_impact="Minimal immediate impact (0-5%)",
            detection_method="Visual inspection",
            recommended_action="Monitor only; cosmetic in most cases",
            failure_mode="Indicates micro-crack presence; monitor for crack propagation",
            standard_reference="IEC TS 60904-13 Section 7.1"
        ),

        DefectCategory.BURN_MARK: IECDefectClassification(
            category=DefectCategory.BURN_MARK,
            severity=DefectSeverity.CRITICAL,
            description="Evidence of overheating or electrical arcing",
            performance_impact="Variable, potential safety hazard",
            detection_method="Visual inspection, IR imaging",
            recommended_action="Immediate shutdown and investigation; safety priority",
            failure_mode="Fire hazard, complete module failure",
            standard_reference="IEC 62790 (Junction box safety)"
        ),

        DefectCategory.CORROSION: IECDefectClassification(
            category=DefectCategory.CORROSION,
            severity=DefectSeverity.HIGH,
            description="Corrosion of metallic components (contacts, frame)",
            performance_impact="Variable depending on location",
            detection_method="Visual inspection, EL imaging",
            recommended_action="Assess extent; repair or replace affected components",
            failure_mode="Increased resistance, potential open circuit",
            standard_reference="IEC 61215 Section 10.14"
        ),

        DefectCategory.NO_DEFECT: IECDefectClassification(
            category=DefectCategory.NO_DEFECT,
            severity=DefectSeverity.LOW,
            description="No visible defects detected",
            performance_impact="None",
            detection_method="All methods",
            recommended_action="Continue routine monitoring schedule",
            failure_mode="N/A",
            standard_reference="IEC TS 60904-13"
        ),
    }

    def __init__(self):
        """Initialize the IEC defect categorizer."""
        self.defect_db = self.DEFECT_DATABASE

    def categorize_defect(self, defect_name: str) -> Optional[IECDefectClassification]:
        """
        Get IEC classification for a defect name.

        Args:
            defect_name: Name of the defect

        Returns:
            IEC defect classification or None if not found
        """
        # Normalize defect name
        defect_name_lower = defect_name.lower().replace("_", " ").replace("-", " ")

        # Try direct match
        for category in DefectCategory:
            if category.value.lower() == defect_name_lower:
                return self.defect_db.get(category)

            # Also try enum name match
            if category.name.lower().replace("_", " ") == defect_name_lower:
                return self.defect_db.get(category)

        # Try partial match
        for category in DefectCategory:
            if defect_name_lower in category.value.lower():
                return self.defect_db.get(category)

        return None

    def get_recommendation(self, defect_name: str) -> str:
        """
        Get IEC-based recommendation for a defect.

        Args:
            defect_name: Name of the defect

        Returns:
            Recommendation string
        """
        classification = self.categorize_defect(defect_name)
        if classification:
            return classification.recommended_action
        return "Consult qualified PV technician for assessment"

    def assess_severity(self, defect_name: str) -> DefectSeverity:
        """
        Assess severity of a defect based on IEC standards.

        Args:
            defect_name: Name of the defect

        Returns:
            Severity level
        """
        classification = self.categorize_defect(defect_name)
        if classification:
            return classification.severity
        return DefectSeverity.MEDIUM  # Default to medium if unknown

    def get_performance_impact(self, defect_name: str) -> str:
        """
        Get expected performance impact of a defect.

        Args:
            defect_name: Name of the defect

        Returns:
            Performance impact description
        """
        classification = self.categorize_defect(defect_name)
        if classification:
            return classification.performance_impact
        return "Impact unknown - requires detailed assessment"

    def prioritize_defects(self, defects: List[str]) -> List[Tuple[str, DefectSeverity]]:
        """
        Prioritize list of defects by severity.

        Args:
            defects: List of defect names

        Returns:
            List of (defect, severity) tuples sorted by priority
        """
        severity_order = {
            DefectSeverity.CRITICAL: 0,
            DefectSeverity.HIGH: 1,
            DefectSeverity.MEDIUM: 2,
            DefectSeverity.LOW: 3
        }

        defect_priorities = []
        for defect in defects:
            severity = self.assess_severity(defect)
            defect_priorities.append((defect, severity))

        # Sort by severity
        defect_priorities.sort(key=lambda x: severity_order[x[1]])

        return defect_priorities

    def generate_action_plan(self, defects: List[str]) -> Dict:
        """
        Generate comprehensive action plan for detected defects.

        Args:
            defects: List of defect names

        Returns:
            Structured action plan
        """
        prioritized = self.prioritize_defects(defects)

        action_plan = {
            "immediate_actions": [],
            "short_term_actions": [],
            "monitoring_required": [],
            "defect_details": []
        }

        for defect, severity in prioritized:
            classification = self.categorize_defect(defect)

            if not classification:
                continue

            defect_info = {
                "defect": defect,
                "severity": severity.value,
                "category": classification.category.value,
                "impact": classification.performance_impact,
                "recommendation": classification.recommended_action,
                "standard": classification.standard_reference
            }

            action_plan["defect_details"].append(defect_info)

            # Categorize actions by severity
            if severity == DefectSeverity.CRITICAL:
                action_plan["immediate_actions"].append(
                    f"{defect}: {classification.recommended_action}"
                )
            elif severity == DefectSeverity.HIGH:
                action_plan["short_term_actions"].append(
                    f"{defect}: {classification.recommended_action}"
                )
            else:
                action_plan["monitoring_required"].append(
                    f"{defect}: {classification.recommended_action}"
                )

        return action_plan

    def get_all_defect_categories(self) -> List[str]:
        """
        Get list of all recognized defect categories.

        Returns:
            List of defect category names
        """
        return [category.value for category in DefectCategory]

    def get_defect_info(self, defect_name: str) -> Dict:
        """
        Get comprehensive information about a defect.

        Args:
            defect_name: Name of the defect

        Returns:
            Dictionary with all defect information
        """
        classification = self.categorize_defect(defect_name)

        if not classification:
            return {
                "found": False,
                "message": f"Defect '{defect_name}' not in IEC database"
            }

        return {
            "found": True,
            "category": classification.category.value,
            "severity": classification.severity.value,
            "description": classification.description,
            "performance_impact": classification.performance_impact,
            "detection_method": classification.detection_method,
            "recommended_action": classification.recommended_action,
            "failure_mode": classification.failure_mode,
            "standard_reference": classification.standard_reference
        }
