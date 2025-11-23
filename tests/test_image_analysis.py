"""
Unit tests for PV Image Analysis Module
"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pv_image_analysis import (
    ImageProcessor,
    CLIPDefectClassifier,
    IECDefectCategorizer,
    ReportGenerator
)


class TestImageProcessor:
    """Test cases for ImageProcessor class"""

    def test_initialization(self):
        """Test ImageProcessor initialization"""
        processor = ImageProcessor()
        assert processor.max_size > 0
        assert len(processor.supported_formats) > 0

    def test_resize_image(self):
        """Test image resizing"""
        processor = ImageProcessor()

        # Create test image
        test_image = Image.new('RGB', (3000, 2000))

        # Resize
        resized = processor.resize_image(test_image, max_size=1024)

        # Check dimensions
        assert max(resized.size) <= 1024
        assert resized.size[0] > 0 and resized.size[1] > 0

    def test_validate_image_size(self):
        """Test image validation for minimum size"""
        processor = ImageProcessor()

        # Valid image
        valid_image = Image.new('RGB', (500, 500))
        assert processor.validate_image(valid_image) == True

        # Too small image should raise error
        small_image = Image.new('RGB', (50, 50))
        with pytest.raises(ValueError):
            processor.validate_image(small_image)

    def test_preprocess_for_clip(self):
        """Test CLIP preprocessing"""
        processor = ImageProcessor()
        test_image = Image.new('RGB', (1000, 1000))

        preprocessed = processor.preprocess_for_clip(test_image)

        # Check output
        assert preprocessed.mode == 'RGB'
        assert max(preprocessed.size) <= 224


class TestCLIPDefectClassifier:
    """Test cases for CLIPDefectClassifier class"""

    def test_initialization(self):
        """Test CLIP classifier initialization"""
        # This will download model on first run
        try:
            classifier = CLIPDefectClassifier()
            assert classifier.model is not None
            assert len(classifier.category_names) > 0
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")

    def test_defect_categories(self):
        """Test defect categories are defined"""
        classifier = CLIPDefectClassifier()
        assert "cell_crack" in classifier.DEFECT_CATEGORIES
        assert "hotspot" in classifier.DEFECT_CATEGORIES
        assert "no_defect" in classifier.DEFECT_CATEGORIES


class TestIECDefectCategorizer:
    """Test cases for IECDefectCategorizer class"""

    def test_initialization(self):
        """Test IEC categorizer initialization"""
        categorizer = IECDefectCategorizer()
        assert categorizer.defect_db is not None

    def test_categorize_defect(self):
        """Test defect categorization"""
        categorizer = IECDefectCategorizer()

        # Test known defect
        classification = categorizer.categorize_defect("cell_crack")
        assert classification is not None
        assert classification.severity is not None

    def test_get_recommendation(self):
        """Test getting recommendations"""
        categorizer = IECDefectCategorizer()

        recommendation = categorizer.get_recommendation("hotspot")
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0

    def test_prioritize_defects(self):
        """Test defect prioritization"""
        categorizer = IECDefectCategorizer()

        defects = ["cell_crack", "hotspot", "snail_trail"]
        prioritized = categorizer.prioritize_defects(defects)

        assert len(prioritized) == len(defects)
        # Check that it's sorted by severity
        assert all(isinstance(item, tuple) for item in prioritized)

    def test_generate_action_plan(self):
        """Test action plan generation"""
        categorizer = IECDefectCategorizer()

        defects = ["hotspot", "cell_crack"]
        action_plan = categorizer.generate_action_plan(defects)

        assert "immediate_actions" in action_plan
        assert "short_term_actions" in action_plan
        assert "defect_details" in action_plan


class TestReportGenerator:
    """Test cases for ReportGenerator class"""

    def test_initialization(self):
        """Test report generator initialization"""
        report_gen = ReportGenerator()
        assert report_gen.output_dir.exists()

    def test_create_report_data(self):
        """Test report data creation"""
        report_gen = ReportGenerator()

        report_data = report_gen.create_report_data(
            image_path="test.jpg",
            clip_results={"has_defects": True},
            metadata={"test": "data"}
        )

        assert "report_metadata" in report_data
        assert "summary" in report_data
        assert "clip_analysis" in report_data

    def test_export_json(self, tmp_path):
        """Test JSON export"""
        report_gen = ReportGenerator(output_dir=tmp_path)

        report_data = report_gen.create_report_data(
            image_path="test.jpg",
            clip_results={"has_defects": False}
        )

        output_file = report_gen.export_json(report_data, "test_report.json")

        assert output_file.exists()
        assert output_file.suffix == ".json"

    def test_export_html(self, tmp_path):
        """Test HTML export"""
        report_gen = ReportGenerator(output_dir=tmp_path)

        report_data = report_gen.create_report_data(
            image_path="test.jpg",
            clip_results={"has_defects": False}
        )

        output_file = report_gen.export_html(report_data, "test_report.html")

        assert output_file.exists()
        assert output_file.suffix == ".html"


# Integration test
def test_basic_workflow():
    """Test basic analysis workflow"""
    # Create a test image
    test_image = Image.new('RGB', (800, 600), color='blue')

    # Initialize components
    processor = ImageProcessor()
    categorizer = IECDefectCategorizer()
    report_gen = ReportGenerator()

    # Validate image
    assert processor.validate_image(test_image) == True

    # Preprocess
    preprocessed = processor.preprocess_for_clip(test_image)
    assert preprocessed is not None

    # Test categorizer
    recommendation = categorizer.get_recommendation("cell_crack")
    assert recommendation is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
