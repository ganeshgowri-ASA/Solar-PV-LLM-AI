"""
GPT-4 Vision Analyzer Module

Wraps OpenAI GPT-4 Vision API for detailed PV panel defect analysis.
Provides spatial coordinates, severity assessment, and detailed descriptions.
"""

import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from io import BytesIO
from PIL import Image
import openai
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import OPENAI_API_KEY, GPT4_VISION_MODEL


class GPT4VisionAnalyzer:
    """
    GPT-4 Vision-based analyzer for detailed PV panel defect analysis.

    Provides:
    - Detailed defect descriptions
    - Approximate spatial coordinates
    - Severity assessment
    - Actionable recommendations
    """

    def __init__(self, api_key: Optional[str] = None, model: str = GPT4_VISION_MODEL):
        """
        Initialize the Vision Analyzer.

        Args:
            api_key: OpenAI API key (uses env var if None)
            model: GPT-4 Vision model name
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = model
        openai.api_key = self.api_key

        # Analysis prompt templates
        self.system_prompt = """You are an expert in photovoltaic (PV) panel inspection and defect analysis.
You specialize in analyzing electroluminescence (EL), thermal, and visual inspection images of solar panels.
Provide detailed, technical analysis of defects including their location, severity, and impact."""

    def _encode_image(self, image: Image.Image) -> str:
        """
        Encode PIL Image to base64 string.

        Args:
            image: PIL Image object

        Returns:
            Base64 encoded string
        """
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def _create_analysis_prompt(self, analysis_type: str = "comprehensive") -> str:
        """
        Create specialized prompt based on analysis type.

        Args:
            analysis_type: Type of analysis requested

        Returns:
            Formatted prompt string
        """
        prompts = {
            "comprehensive": """Analyze this solar panel image in detail. Provide:

1. **Defect Identification**: List all visible defects
2. **Spatial Location**: Describe where each defect is located (e.g., "top-left cell", "third row, second column")
3. **Severity Assessment**: Rate each defect (Low/Medium/High/Critical)
4. **Technical Description**: Explain the nature of each defect
5. **Potential Causes**: What likely caused these defects
6. **Impact Analysis**: How these defects affect panel performance
7. **Recommendations**: Suggested actions (repair, replace, monitor)

Format your response as structured JSON with these fields:
{
    "overall_condition": "Good/Fair/Poor/Critical",
    "defects": [
        {
            "type": "defect type",
            "location": "spatial description",
            "approximate_coordinates": {"x": "description", "y": "description"},
            "severity": "Low/Medium/High/Critical",
            "description": "detailed description",
            "potential_cause": "likely cause",
            "performance_impact": "impact description",
            "recommendation": "action to take"
        }
    ],
    "summary": "overall assessment",
    "priority_actions": ["action 1", "action 2"]
}""",

            "defect_detection": """Identify and locate all defects in this solar panel image.

For each defect found, specify:
- Type of defect
- Location (row/column or position description)
- Severity level
- Brief description

Respond in JSON format.""",

            "severity_assessment": """Assess the severity of defects in this solar panel image.

Rate the overall condition and each defect's severity.
Prioritize which defects need immediate attention.

Respond in JSON format.""",

            "el_image": """Analyze this electroluminescence (EL) image of a solar panel.

Focus on:
- Cell cracks and micro-cracks
- Inactive cell areas
- Current collection issues
- Finger interruptions
- Shunts or low shunt resistance areas

Provide detailed technical analysis in JSON format.""",

            "thermal_image": """Analyze this thermal/infrared image of a solar panel.

Focus on:
- Hot spots and temperature anomalies
- Potential bypass diode issues
- Areas with abnormal heat distribution
- Signs of electrical problems
- Temperature gradients

Provide detailed technical analysis in JSON format.""",

            "iv_curve": """Analyze this IV (Current-Voltage) curve of a solar panel.

Focus on:
- Curve shape and characteristics
- Open-circuit voltage (Voc)
- Short-circuit current (Isc)
- Maximum power point
- Fill factor
- Any abnormalities or degradation signs

Provide detailed technical analysis in JSON format."""
        }

        return prompts.get(analysis_type, prompts["comprehensive"])

    def analyze_image(
        self,
        image: Union[Image.Image, str, Path],
        analysis_type: str = "comprehensive",
        custom_prompt: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Dict:
        """
        Analyze PV panel image using GPT-4 Vision.

        Args:
            image: PIL Image, path to image, or base64 string
            analysis_type: Type of analysis ("comprehensive", "defect_detection", etc.)
            custom_prompt: Custom analysis prompt (overrides analysis_type)
            max_tokens: Maximum tokens in response

        Returns:
            Analysis results dictionary
        """
        # Handle different image input types
        if isinstance(image, (str, Path)):
            if Path(image).exists():
                image = Image.open(image)
                image_data = self._encode_image(image)
            else:
                # Assume it's already base64
                image_data = image
        elif isinstance(image, Image.Image):
            image_data = self._encode_image(image)
        else:
            raise ValueError("Image must be PIL Image, file path, or base64 string")

        # Prepare prompt
        prompt = custom_prompt or self._create_analysis_prompt(analysis_type)

        # Create API request
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.1  # Low temperature for consistent technical analysis
            )

            # Extract response
            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                # Look for JSON in markdown code blocks
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                result = json.loads(content)
                result["raw_response"] = content
                result["analysis_type"] = analysis_type
            except json.JSONDecodeError:
                # If not valid JSON, return as text
                result = {
                    "raw_response": content,
                    "analysis_type": analysis_type,
                    "parsed": False
                }

            # Add metadata
            result["model"] = self.model
            result["tokens_used"] = response.usage.total_tokens

            return result

        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": analysis_type,
                "success": False
            }

    def analyze_batch(
        self,
        images: List[Union[Image.Image, str, Path]],
        analysis_type: str = "comprehensive"
    ) -> List[Dict]:
        """
        Analyze multiple images in sequence.

        Args:
            images: List of images (PIL Image, path, or base64)
            analysis_type: Type of analysis

        Returns:
            List of analysis results
        """
        results = []
        for i, image in enumerate(images):
            try:
                result = self.analyze_image(image, analysis_type)
                result["image_index"] = i
                results.append(result)
            except Exception as e:
                results.append({
                    "image_index": i,
                    "error": str(e),
                    "success": False
                })

        return results

    def get_defect_coordinates(self, analysis_result: Dict) -> List[Dict]:
        """
        Extract defect coordinates from analysis result.

        Args:
            analysis_result: Result from analyze_image

        Returns:
            List of defect coordinates
        """
        coordinates = []

        if "defects" in analysis_result:
            for defect in analysis_result["defects"]:
                if "approximate_coordinates" in defect or "location" in defect:
                    coordinates.append({
                        "type": defect.get("type", "unknown"),
                        "location": defect.get("location", ""),
                        "coordinates": defect.get("approximate_coordinates", {}),
                        "severity": defect.get("severity", "unknown")
                    })

        return coordinates

    def compare_analyses(
        self,
        image1: Union[Image.Image, str, Path],
        image2: Union[Image.Image, str, Path]
    ) -> Dict:
        """
        Compare two PV panel images to identify changes or degradation.

        Args:
            image1: First image (e.g., initial inspection)
            image2: Second image (e.g., follow-up inspection)

        Returns:
            Comparison analysis
        """
        # Analyze both images
        result1 = self.analyze_image(image1, "comprehensive")
        result2 = self.analyze_image(image2, "comprehensive")

        # Create comparison prompt
        comparison_prompt = """Compare these two solar panel images and identify:
1. New defects that appeared
2. Existing defects that worsened
3. Any improvements or repairs
4. Overall degradation trend

Provide structured comparison in JSON format."""

        # Note: This would require multi-image support in API
        # For now, return both analyses
        return {
            "initial_analysis": result1,
            "followup_analysis": result2,
            "comparison_note": "Detailed comparison requires manual review of both analyses"
        }

    def generate_inspection_report(self, analysis_result: Dict) -> str:
        """
        Generate human-readable inspection report from analysis.

        Args:
            analysis_result: Result from analyze_image

        Returns:
            Formatted report string
        """
        if "error" in analysis_result:
            return f"Analysis Error: {analysis_result['error']}"

        report = "=== SOLAR PANEL INSPECTION REPORT ===\n\n"

        # Overall condition
        if "overall_condition" in analysis_result:
            report += f"Overall Condition: {analysis_result['overall_condition']}\n\n"

        # Defects
        if "defects" in analysis_result and analysis_result["defects"]:
            report += f"DEFECTS IDENTIFIED: {len(analysis_result['defects'])}\n"
            report += "-" * 50 + "\n\n"

            for i, defect in enumerate(analysis_result["defects"], 1):
                report += f"{i}. {defect.get('type', 'Unknown Defect')}\n"
                report += f"   Location: {defect.get('location', 'N/A')}\n"
                report += f"   Severity: {defect.get('severity', 'N/A')}\n"
                report += f"   Description: {defect.get('description', 'N/A')}\n"
                report += f"   Recommendation: {defect.get('recommendation', 'N/A')}\n\n"
        else:
            report += "No defects identified.\n\n"

        # Summary
        if "summary" in analysis_result:
            report += f"SUMMARY:\n{analysis_result['summary']}\n\n"

        # Priority actions
        if "priority_actions" in analysis_result and analysis_result["priority_actions"]:
            report += "PRIORITY ACTIONS:\n"
            for action in analysis_result["priority_actions"]:
                report += f"- {action}\n"

        return report
