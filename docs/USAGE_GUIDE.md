# PV Image Analysis Module - Usage Guide

## Overview

The PV Image Analysis Module is a comprehensive AI-powered system for detecting and analyzing defects in photovoltaic (solar) panels. It supports multiple image types including:

- **EL (Electroluminescence)** images
- **Thermal/IR** images
- **IV curve** plots
- **Visual inspection** images

## Features

### 1. Image Processing Pipeline
- Automatic image loading and validation
- Format support: JPG, PNG, BMP, TIFF
- Intelligent preprocessing and enhancement
- Auto-detection of image type

### 2. CLIP-Based Defect Classification
- Zero-shot defect detection using OpenAI's CLIP model
- 15+ defect categories
- Confidence scoring
- Batch processing support

### 3. GPT-4 Vision Analysis
- Detailed defect descriptions
- Spatial location identification
- Severity assessment
- Root cause analysis
- Performance impact estimation

### 4. IEC TS 60904-13 Compliance
- Standards-based defect categorization
- Severity classification (Low/Medium/High/Critical)
- Recommended actions
- Failure mode analysis
- Standard references

### 5. Report Generation
- Multiple export formats: JSON, HTML, PDF
- Comprehensive analysis reports
- Defect visualization
- Action plans

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key (required for GPT-4 Vision features):

```
OPENAI_API_KEY=your_api_key_here
```

### 3. Download CLIP Model

The CLIP model will be downloaded automatically on first use.

## Quick Start

### Basic Usage

```python
from pv_image_analysis import (
    ImageProcessor,
    CLIPDefectClassifier,
    ReportGenerator
)

# 1. Load and preprocess image
processor = ImageProcessor()
processed = processor.process_image_pipeline("panel.jpg")

# 2. Classify defects
classifier = CLIPDefectClassifier()
results = classifier.detect_defects(processed['clip_ready'])

# 3. Generate report
report_gen = ReportGenerator()
reports = report_gen.generate_complete_report(
    image_path="panel.jpg",
    clip_results=results,
    formats=["json", "html"]
)
```

### Advanced Usage with GPT-4 Vision

```python
from pv_image_analysis import (
    ImageProcessor,
    CLIPDefectClassifier,
    GPT4VisionAnalyzer,
    IECDefectCategorizer,
    ReportGenerator
)

# 1. Process image
processor = ImageProcessor()
processed = processor.process_image_pipeline(
    "panel.jpg",
    image_type="el",  # Specify EL image
    enhance=True
)

# 2. CLIP classification
clip_classifier = CLIPDefectClassifier()
clip_results = clip_classifier.detect_defects(processed['clip_ready'])

# 3. GPT-4 Vision detailed analysis
vision_analyzer = GPT4VisionAnalyzer()
vision_results = vision_analyzer.analyze_image(
    processed['vision_ready'],
    analysis_type="el_image"
)

# 4. IEC categorization
iec_categorizer = IECDefectCategorizer()
defect_names = [d['category'] for d in clip_results['detected_defects']]
action_plan = iec_categorizer.generate_action_plan(defect_names)

# 5. Generate comprehensive report
report_gen = ReportGenerator()
reports = report_gen.generate_complete_report(
    image_path="panel.jpg",
    clip_results=clip_results,
    vision_results=vision_results,
    iec_classification=action_plan,
    formats=["json", "html", "pdf"]
)
```

### Batch Processing

```python
from pv_image_analysis import ImageProcessor, CLIPDefectClassifier

processor = ImageProcessor()
classifier = CLIPDefectClassifier()

image_paths = ["panel1.jpg", "panel2.jpg", "panel3.jpg"]

# Batch process images
processed_images = processor.batch_process(image_paths)

# Batch classify
for processed in processed_images:
    if processed['success']:
        results = classifier.detect_defects(processed['clip_ready'])
        print(f"{processed['path']}: {results['top_prediction']['category']}")
```

## Module Reference

### ImageProcessor

Handles image loading, validation, and preprocessing.

**Methods:**
- `load_image(image_path)` - Load image from file
- `validate_image(image)` - Validate image quality
- `resize_image(image, max_size)` - Resize maintaining aspect ratio
- `enhance_image(image, image_type)` - Apply type-specific enhancement
- `process_image_pipeline(image_path, image_type, enhance)` - Complete pipeline
- `batch_process(image_paths, image_type, enhance)` - Batch processing

### CLIPDefectClassifier

CLIP-based defect classification.

**Methods:**
- `classify_image(image, top_k)` - Classify single image
- `classify_batch(images, top_k)` - Classify multiple images
- `detect_defects(image, threshold)` - Detect defects above threshold
- `compare_images(image1, image2)` - Compare two images
- `add_custom_categories(categories)` - Add custom defect types

**Defect Categories:**
- Cell cracks (various types)
- Hot spots
- Delamination
- Discoloration
- Snail trails
- PID (Potential Induced Degradation)
- Burn marks
- Broken cells
- Micro-cracks
- Inactive cells
- Finger interruption
- Busbar corrosion
- Soldering defects
- Junction box issues

### GPT4VisionAnalyzer

GPT-4 Vision API wrapper for detailed analysis.

**Methods:**
- `analyze_image(image, analysis_type, custom_prompt, max_tokens)` - Analyze image
- `analyze_batch(images, analysis_type)` - Batch analysis
- `get_defect_coordinates(analysis_result)` - Extract coordinates
- `compare_analyses(image1, image2)` - Compare two analyses
- `generate_inspection_report(analysis_result)` - Generate text report

**Analysis Types:**
- `comprehensive` - Full analysis with all details
- `defect_detection` - Focus on defect identification
- `severity_assessment` - Focus on severity rating
- `el_image` - Specialized for EL images
- `thermal_image` - Specialized for thermal images
- `iv_curve` - Specialized for IV curves

### IECDefectCategorizer

IEC TS 60904-13 based defect categorization.

**Methods:**
- `categorize_defect(defect_name)` - Get IEC classification
- `get_recommendation(defect_name)` - Get recommendation
- `assess_severity(defect_name)` - Get severity level
- `get_performance_impact(defect_name)` - Get impact estimate
- `prioritize_defects(defects)` - Sort by severity
- `generate_action_plan(defects)` - Create action plan
- `get_defect_info(defect_name)` - Get full information

**Severity Levels:**
- Low
- Medium
- High
- Critical

### ReportGenerator

Generate comprehensive reports in multiple formats.

**Methods:**
- `create_report_data(...)` - Compile report data
- `export_json(report_data, filename)` - Export as JSON
- `export_html(report_data, filename)` - Export as HTML
- `export_pdf(report_data, filename)` - Export as PDF
- `create_visualization(image_path, defects, output_filename)` - Create annotated image
- `generate_complete_report(...)` - Generate all formats

## Demo Script

Run the demo script to test the system:

### Basic Analysis (No API Key Required)

```bash
python examples/demo_analysis.py path/to/image.jpg --mode basic
```

### Advanced Analysis (Requires OpenAI API Key)

```bash
python examples/demo_analysis.py path/to/image.jpg --mode advanced
```

### Batch Processing

```bash
python examples/demo_analysis.py --mode batch --batch image1.jpg image2.jpg image3.jpg
```

## Report Output

Reports are generated in the `reports/` directory:

- **JSON**: Structured data for programmatic access
- **HTML**: Interactive web-based report with styling
- **PDF**: Printable document (requires reportlab)
- **Visualization**: Annotated image with defect markers

## Best Practices

### Image Quality

1. **Resolution**: Minimum 512x512 pixels, 2048x2048 recommended
2. **Format**: PNG or JPEG with minimal compression
3. **Lighting**: Consistent lighting for EL/thermal images
4. **Focus**: Sharp, in-focus images

### Analysis Workflow

1. **Start with CLIP**: Fast, no API costs
2. **Use Vision for Critical Cases**: Detailed analysis when needed
3. **Apply IEC Standards**: Get actionable recommendations
4. **Generate Reports**: Document findings

### API Usage

- **Rate Limits**: GPT-4 Vision has rate limits; batch carefully
- **Cost Management**: Vision API has per-image costs
- **Error Handling**: Always handle API errors gracefully

## Troubleshooting

### CLIP Model Issues

If CLIP model fails to load:
```python
# Try different model variant
classifier = CLIPDefectClassifier(model_name="ViT-L/14")
```

### Vision API Errors

Common issues:
- Invalid API key → Check `.env` file
- Rate limit → Add delays between requests
- Image too large → Reduce size before processing

### Memory Issues

For large batches:
```python
# Process in smaller chunks
chunk_size = 10
for i in range(0, len(images), chunk_size):
    chunk = images[i:i+chunk_size]
    results = processor.batch_process(chunk)
```

## Performance Optimization

### CPU vs GPU

CLIP runs faster on GPU:
```python
classifier = CLIPDefectClassifier(device="cuda")
```

### Batch Processing

Process multiple images together:
```python
images = [processor.load_image(path) for path in paths]
results = classifier.classify_batch(images)
```

### Caching

Cache processed images:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_processed_image(path):
    return processor.process_image_pipeline(path)
```

## Integration Examples

### Web API Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
processor = ImageProcessor()
classifier = CLIPDefectClassifier()

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['image']
    processed = processor.process_image_pipeline(file)
    results = classifier.detect_defects(processed['clip_ready'])
    return jsonify(results)
```

### Database Storage

```python
import json
import sqlite3

# Store analysis results
conn = sqlite3.connect('pv_analysis.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY,
        image_path TEXT,
        timestamp TEXT,
        results TEXT
    )
''')

cursor.execute(
    'INSERT INTO analyses (image_path, timestamp, results) VALUES (?, ?, ?)',
    (image_path, datetime.now().isoformat(), json.dumps(results))
)
conn.commit()
```

## Citation

If you use this module in research, please cite:

```
PV Image Analysis Module (2024)
AI-Powered Defect Detection for Photovoltaic Panels
Based on IEC TS 60904-13 Standards
```

## Support

For issues and questions:
- Check documentation
- Review demo scripts
- Examine example outputs

## License

See LICENSE file for details.
