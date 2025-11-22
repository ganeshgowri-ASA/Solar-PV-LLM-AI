"""
Report Generator Module

Generates comprehensive analysis reports in multiple formats (PDF, JSON, HTML).
Combines results from CLIP, GPT-4 Vision, and IEC categorization.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import REPORT_OUTPUT_DIR


class ReportGenerator:
    """
    Generates comprehensive PV analysis reports in multiple formats.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize report generator.

        Args:
            output_dir: Directory for report output (uses default if None)
        """
        self.output_dir = Path(output_dir) if output_dir else REPORT_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_report_data(
        self,
        image_path: str,
        clip_results: Optional[Dict] = None,
        vision_results: Optional[Dict] = None,
        iec_classification: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Compile all analysis results into structured report data.

        Args:
            image_path: Path to analyzed image
            clip_results: CLIP classification results
            vision_results: GPT-4 Vision analysis results
            iec_classification: IEC defect categorization
            metadata: Additional metadata

        Returns:
            Structured report data dictionary
        """
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "image_path": str(image_path),
                "analysis_version": "1.0.0"
            },
            "image_info": metadata or {},
            "clip_analysis": clip_results or {},
            "vision_analysis": vision_results or {},
            "iec_classification": iec_classification or {},
            "summary": self._generate_summary(clip_results, vision_results, iec_classification)
        }

        return report_data

    def _generate_summary(
        self,
        clip_results: Optional[Dict],
        vision_results: Optional[Dict],
        iec_classification: Optional[Dict]
    ) -> Dict:
        """
        Generate executive summary from all analyses.

        Args:
            clip_results: CLIP results
            vision_results: Vision results
            iec_classification: IEC classification

        Returns:
            Summary dictionary
        """
        summary = {
            "overall_status": "Unknown",
            "defects_detected": False,
            "critical_issues": [],
            "recommendations": []
        }

        # Analyze CLIP results
        if clip_results and "has_defects" in clip_results:
            summary["defects_detected"] = clip_results["has_defects"]
            if clip_results.get("top_prediction"):
                summary["primary_defect_type"] = clip_results["top_prediction"].get("category")

        # Analyze Vision results
        if vision_results and "overall_condition" in vision_results:
            summary["overall_status"] = vision_results["overall_condition"]

            # Extract critical defects
            if "defects" in vision_results:
                for defect in vision_results["defects"]:
                    if defect.get("severity") == "Critical":
                        summary["critical_issues"].append(defect.get("type", "Unknown"))

            # Extract recommendations
            if "priority_actions" in vision_results:
                summary["recommendations"].extend(vision_results["priority_actions"])

        # Add IEC recommendations
        if iec_classification and "immediate_actions" in iec_classification:
            summary["recommendations"].extend(iec_classification["immediate_actions"])

        return summary

    def export_json(self, report_data: Dict, filename: Optional[str] = None) -> Path:
        """
        Export report as JSON file.

        Args:
            report_data: Report data dictionary
            filename: Output filename (auto-generated if None)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pv_analysis_report_{timestamp}.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return output_path

    def export_html(self, report_data: Dict, filename: Optional[str] = None) -> Path:
        """
        Export report as HTML file.

        Args:
            report_data: Report data dictionary
            filename: Output filename (auto-generated if None)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pv_analysis_report_{timestamp}.html"

        output_path = self.output_dir / filename

        html_content = self._generate_html(report_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _generate_html(self, report_data: Dict) -> str:
        """
        Generate HTML content from report data.

        Args:
            report_data: Report data dictionary

        Returns:
            HTML string
        """
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PV Image Analysis Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header .subtitle {
            opacity: 0.9;
            margin-top: 10px;
        }
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 5px;
        }
        .status-good { background-color: #4CAF50; color: white; }
        .status-fair { background-color: #FF9800; color: white; }
        .status-poor { background-color: #f44336; color: white; }
        .status-critical { background-color: #d32f2f; color: white; }
        .defect-item {
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            background-color: #f9f9f9;
        }
        .defect-item h3 {
            margin-top: 0;
            color: #333;
        }
        .severity-low { border-left-color: #4CAF50; }
        .severity-medium { border-left-color: #FF9800; }
        .severity-high { border-left-color: #f44336; }
        .severity-critical { border-left-color: #d32f2f; }
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .metadata-item {
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
        }
        .metadata-item strong {
            display: block;
            color: #667eea;
            margin-bottom: 5px;
        }
        .recommendations {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
        }
        .recommendations h3 {
            margin-top: 0;
            color: #856404;
        }
        .recommendations ul {
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
"""

        # Header
        metadata = report_data.get("report_metadata", {})
        html += f"""
    <div class="header">
        <h1>🔆 PV Image Analysis Report</h1>
        <div class="subtitle">Generated: {metadata.get("generated_at", "N/A")}</div>
        <div class="subtitle">Image: {Path(metadata.get("image_path", "N/A")).name}</div>
    </div>
"""

        # Summary Section
        summary = report_data.get("summary", {})
        status = summary.get("overall_status", "Unknown")
        status_class = {
            "Good": "status-good",
            "Fair": "status-fair",
            "Poor": "status-poor",
            "Critical": "status-critical"
        }.get(status, "status-fair")

        html += f"""
    <div class="section">
        <h2>Executive Summary</h2>
        <p><strong>Overall Condition:</strong> <span class="status-badge {status_class}">{status}</span></p>
        <p><strong>Defects Detected:</strong> {"Yes" if summary.get("defects_detected") else "No"}</p>
"""

        if summary.get("primary_defect_type"):
            html += f'        <p><strong>Primary Defect Type:</strong> {summary["primary_defect_type"].replace("_", " ").title()}</p>\n'

        if summary.get("critical_issues"):
            html += """
        <div class="recommendations">
            <h3>⚠️ Critical Issues</h3>
            <ul>
"""
            for issue in summary["critical_issues"]:
                html += f"                <li>{issue}</li>\n"
            html += """            </ul>
        </div>
"""

        html += "    </div>\n"

        # Vision Analysis Section
        vision = report_data.get("vision_analysis", {})
        if vision and "defects" in vision:
            html += """
    <div class="section">
        <h2>Detailed Defect Analysis</h2>
"""
            for i, defect in enumerate(vision.get("defects", []), 1):
                severity = defect.get("severity", "Medium")
                severity_class = f"severity-{severity.lower()}"
                html += f"""
        <div class="defect-item {severity_class}">
            <h3>{i}. {defect.get("type", "Unknown Defect")}</h3>
            <p><strong>Location:</strong> {defect.get("location", "Not specified")}</p>
            <p><strong>Severity:</strong> <span class="status-badge status-{severity.lower()}">{severity}</span></p>
            <p><strong>Description:</strong> {defect.get("description", "N/A")}</p>
            <p><strong>Performance Impact:</strong> {defect.get("performance_impact", "N/A")}</p>
            <p><strong>Recommendation:</strong> {defect.get("recommendation", "N/A")}</p>
        </div>
"""
            html += "    </div>\n"

        # CLIP Analysis Section
        clip = report_data.get("clip_analysis", {})
        if clip and "all_predictions" in clip:
            html += """
    <div class="section">
        <h2>AI Classification Results</h2>
        <p>Top defect predictions from CLIP model:</p>
"""
            for pred in clip["all_predictions"][:5]:
                confidence_pct = pred["confidence"] * 100
                html += f"""
        <p>
            <strong>{pred["category"].replace("_", " ").title()}</strong>:
            {confidence_pct:.1f}% confidence
        </p>
"""
            html += "    </div>\n"

        # IEC Classification Section
        iec = report_data.get("iec_classification", {})
        if iec and "defect_details" in iec:
            html += """
    <div class="section">
        <h2>IEC TS 60904-13 Classification</h2>
"""
            for defect_info in iec.get("defect_details", []):
                html += f"""
        <div class="defect-item">
            <h3>{defect_info.get("category", "Unknown")}</h3>
            <p><strong>Severity:</strong> {defect_info.get("severity", "N/A")}</p>
            <p><strong>Performance Impact:</strong> {defect_info.get("impact", "N/A")}</p>
            <p><strong>Recommendation:</strong> {defect_info.get("recommendation", "N/A")}</p>
            <p><strong>Standard Reference:</strong> {defect_info.get("standard", "N/A")}</p>
        </div>
"""
            html += "    </div>\n"

        # Recommendations
        if summary.get("recommendations"):
            html += """
    <div class="section">
        <div class="recommendations">
            <h3>📋 Recommended Actions</h3>
            <ul>
"""
            for rec in summary["recommendations"]:
                html += f"                <li>{rec}</li>\n"
            html += """            </ul>
        </div>
    </div>
"""

        # Footer
        html += """
    <div class="footer">
        <p>This report was automatically generated by the PV Image Analysis System</p>
        <p>Based on IEC TS 60904-13 and industry best practices</p>
    </div>
</body>
</html>
"""

        return html

    def export_pdf(self, report_data: Dict, filename: Optional[str] = None) -> Path:
        """
        Export report as PDF file (simplified version).

        Args:
            report_data: Report data dictionary
            filename: Output filename (auto-generated if None)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pv_analysis_report_{timestamp}.pdf"

        output_path = self.output_dir / filename

        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.units import inch

            # Create PDF
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=30
            )
            story.append(Paragraph("PV Image Analysis Report", title_style))

            # Metadata
            metadata = report_data.get("report_metadata", {})
            story.append(Paragraph(f"<b>Generated:</b> {metadata.get('generated_at', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<b>Image:</b> {metadata.get('image_path', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

            # Summary
            summary = report_data.get("summary", {})
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Paragraph(f"<b>Overall Status:</b> {summary.get('overall_status', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"<b>Defects Detected:</b> {'Yes' if summary.get('defects_detected') else 'No'}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

            # Defects
            vision = report_data.get("vision_analysis", {})
            if vision and "defects" in vision:
                story.append(Paragraph("Detailed Defect Analysis", styles['Heading2']))
                for i, defect in enumerate(vision.get("defects", []), 1):
                    story.append(Paragraph(f"<b>{i}. {defect.get('type', 'Unknown')}</b>", styles['Heading3']))
                    story.append(Paragraph(f"Severity: {defect.get('severity', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"Location: {defect.get('location', 'N/A')}", styles['Normal']))
                    story.append(Paragraph(f"Description: {defect.get('description', 'N/A')}", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))

            # Build PDF
            doc.build(story)

        except ImportError:
            # Fallback: Create HTML and note PDF generation unavailable
            html_path = self.export_html(report_data, filename.replace('.pdf', '.html'))
            print(f"Note: reportlab not available. HTML report generated instead: {html_path}")
            return html_path

        return output_path

    def create_visualization(
        self,
        image_path: Union[str, Path],
        defects: List[Dict],
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Create visualization with defect annotations.

        Args:
            image_path: Path to original image
            defects: List of defect dictionaries with location info
            output_filename: Output filename (auto-generated if None)

        Returns:
            Path to visualization image
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"pv_defect_visualization_{timestamp}.png"

        output_path = self.output_dir / output_filename

        # Load image
        image = Image.open(image_path)

        # Create figure
        fig, ax = plt.subplots(1, figsize=(12, 8))
        ax.imshow(image)

        # Annotate defects
        colors_map = {
            "Low": "green",
            "Medium": "yellow",
            "High": "orange",
            "Critical": "red"
        }

        for i, defect in enumerate(defects, 1):
            severity = defect.get("severity", "Medium")
            color = colors_map.get(severity, "yellow")
            location = defect.get("location", "")

            # Add text annotation
            ax.text(
                10, 30 + (i * 30),
                f"{i}. {defect.get('type', 'Unknown')} ({severity})",
                color=color,
                fontsize=10,
                bbox=dict(boxstyle="round", facecolor='black', alpha=0.7),
                weight='bold'
            )

        ax.axis('off')
        plt.title("PV Panel Defect Analysis", fontsize=16, weight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path

    def generate_complete_report(
        self,
        image_path: Union[str, Path],
        clip_results: Optional[Dict] = None,
        vision_results: Optional[Dict] = None,
        iec_classification: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        formats: List[str] = ["json", "html"]
    ) -> Dict[str, Path]:
        """
        Generate complete report in multiple formats.

        Args:
            image_path: Path to analyzed image
            clip_results: CLIP analysis results
            vision_results: Vision analysis results
            iec_classification: IEC classification results
            metadata: Additional metadata
            formats: List of export formats ("json", "html", "pdf")

        Returns:
            Dictionary mapping format to output path
        """
        # Create report data
        report_data = self.create_report_data(
            image_path,
            clip_results,
            vision_results,
            iec_classification,
            metadata
        )

        # Generate reports in requested formats
        output_files = {}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"pv_report_{timestamp}"

        if "json" in formats:
            output_files["json"] = self.export_json(report_data, f"{base_name}.json")

        if "html" in formats:
            output_files["html"] = self.export_html(report_data, f"{base_name}.html")

        if "pdf" in formats:
            output_files["pdf"] = self.export_pdf(report_data, f"{base_name}.pdf")

        # Create visualization if defects present
        vision = vision_results or {}
        if vision.get("defects"):
            viz_path = self.create_visualization(
                image_path,
                vision["defects"],
                f"{base_name}_visualization.png"
            )
            output_files["visualization"] = viz_path

        return output_files
