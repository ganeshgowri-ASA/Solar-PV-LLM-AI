"""
Demo Script for PV Image Analysis Module

This script demonstrates how to use the PV Image Analysis module
for detecting and analyzing defects in solar panel images.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pv_image_analysis import (
    ImageProcessor,
    CLIPDefectClassifier,
    GPT4VisionAnalyzer,
    IECDefectCategorizer,
    ReportGenerator
)


def demo_basic_analysis(image_path: str):
    """
    Demonstrate basic image analysis workflow.

    Args:
        image_path: Path to PV panel image
    """
    print("=" * 70)
    print("PV IMAGE ANALYSIS DEMO - Basic Analysis")
    print("=" * 70)
    print()

    # Step 1: Image Processing
    print("Step 1: Loading and preprocessing image...")
    processor = ImageProcessor()

    try:
        processed = processor.process_image_pipeline(
            image_path,
            image_type="auto",
            enhance=True
        )
        print(f"✓ Image loaded successfully: {processed['metadata']['original_size']}")
        print(f"  Format: {processed['metadata']['format']}")
        print(f"  Enhanced: {processed['metadata']['enhanced']}")
        print()
    except Exception as e:
        print(f"✗ Error loading image: {e}")
        return

    # Step 2: CLIP Classification
    print("Step 2: Running CLIP defect classification...")
    try:
        clip_classifier = CLIPDefectClassifier()
        clip_results = clip_classifier.detect_defects(processed['clip_ready'])

        print(f"✓ CLIP Analysis complete")
        print(f"  Defects detected: {clip_results['has_defects']}")
        print(f"  Top prediction: {clip_results['top_prediction']['category']}")
        print(f"  Confidence: {clip_results['top_prediction']['confidence']:.2%}")
        print()

        # Show top 3 predictions
        print("  Top 3 defect predictions:")
        for i, pred in enumerate(clip_results['all_predictions'][:3], 1):
            print(f"    {i}. {pred['category'].replace('_', ' ').title()}: {pred['confidence']:.2%}")
        print()
    except Exception as e:
        print(f"✗ Error in CLIP analysis: {e}")
        clip_results = None

    # Step 3: IEC Classification
    print("Step 3: IEC TS 60904-13 defect categorization...")
    try:
        iec_categorizer = IECDefectCategorizer()

        if clip_results and clip_results['detected_defects']:
            defect_names = [d['category'] for d in clip_results['detected_defects']]
            action_plan = iec_categorizer.generate_action_plan(defect_names)

            print(f"✓ IEC Classification complete")
            print(f"  Defects categorized: {len(defect_names)}")

            if action_plan['immediate_actions']:
                print(f"  ⚠️  Immediate actions required: {len(action_plan['immediate_actions'])}")

            if action_plan['short_term_actions']:
                print(f"  Short-term actions: {len(action_plan['short_term_actions'])}")

            print()
        else:
            print("  No defects to categorize")
            action_plan = None
            print()
    except Exception as e:
        print(f"✗ Error in IEC classification: {e}")
        action_plan = None

    # Step 4: Generate Report
    print("Step 4: Generating analysis report...")
    try:
        report_gen = ReportGenerator()

        output_files = report_gen.generate_complete_report(
            image_path=image_path,
            clip_results=clip_results,
            vision_results=None,  # Skip Vision API for basic demo
            iec_classification=action_plan,
            metadata=processed['metadata'],
            formats=["json", "html"]
        )

        print("✓ Reports generated:")
        for format_type, file_path in output_files.items():
            print(f"  {format_type.upper()}: {file_path}")
        print()
    except Exception as e:
        print(f"✗ Error generating report: {e}")

    print("=" * 70)
    print("Basic analysis complete!")
    print("=" * 70)
    print()


def demo_advanced_analysis(image_path: str):
    """
    Demonstrate advanced analysis with GPT-4 Vision.

    Args:
        image_path: Path to PV panel image
    """
    print("=" * 70)
    print("PV IMAGE ANALYSIS DEMO - Advanced Analysis (with GPT-4 Vision)")
    print("=" * 70)
    print()

    # Step 1: Image Processing
    print("Step 1: Loading and preprocessing image...")
    processor = ImageProcessor()

    try:
        processed = processor.process_image_pipeline(
            image_path,
            image_type="el",  # Specify EL image type
            enhance=True
        )
        print(f"✓ Image loaded and enhanced")
        print()
    except Exception as e:
        print(f"✗ Error loading image: {e}")
        return

    # Step 2: CLIP Classification
    print("Step 2: CLIP defect classification...")
    try:
        clip_classifier = CLIPDefectClassifier()
        clip_results = clip_classifier.detect_defects(processed['clip_ready'])
        print(f"✓ CLIP: {clip_results['top_prediction']['category']}")
        print()
    except Exception as e:
        print(f"✗ CLIP error: {e}")
        clip_results = None

    # Step 3: GPT-4 Vision Analysis
    print("Step 3: GPT-4 Vision detailed analysis...")
    print("  (This requires valid OpenAI API key in .env file)")
    try:
        vision_analyzer = GPT4VisionAnalyzer()
        vision_results = vision_analyzer.analyze_image(
            processed['vision_ready'],
            analysis_type="el_image"  # Specialized for EL images
        )

        if "error" not in vision_results:
            print("✓ Vision analysis complete")

            if "defects" in vision_results:
                print(f"  Defects found: {len(vision_results['defects'])}")
                for i, defect in enumerate(vision_results['defects'][:3], 1):
                    print(f"    {i}. {defect.get('type', 'Unknown')} - {defect.get('severity', 'N/A')}")
            print()
        else:
            print(f"✗ Vision API error: {vision_results['error']}")
            vision_results = None
            print()
    except Exception as e:
        print(f"✗ Vision analysis error: {e}")
        print("  Make sure OPENAI_API_KEY is set in .env file")
        vision_results = None
        print()

    # Step 4: IEC Classification
    print("Step 4: IEC classification and recommendations...")
    try:
        iec_categorizer = IECDefectCategorizer()

        defect_names = []
        if clip_results and clip_results['detected_defects']:
            defect_names.extend([d['category'] for d in clip_results['detected_defects']])

        if vision_results and 'defects' in vision_results:
            defect_names.extend([d.get('type', '') for d in vision_results['defects']])

        if defect_names:
            action_plan = iec_categorizer.generate_action_plan(defect_names)
            print(f"✓ Action plan generated")

            if action_plan['immediate_actions']:
                print("  ⚠️  IMMEDIATE ACTIONS:")
                for action in action_plan['immediate_actions']:
                    print(f"    • {action}")

            if action_plan['short_term_actions']:
                print("  SHORT-TERM ACTIONS:")
                for action in action_plan['short_term_actions'][:3]:
                    print(f"    • {action}")
            print()
        else:
            action_plan = None
            print("  No defects to categorize")
            print()
    except Exception as e:
        print(f"✗ IEC classification error: {e}")
        action_plan = None

    # Step 5: Generate Comprehensive Report
    print("Step 5: Generating comprehensive report...")
    try:
        report_gen = ReportGenerator()

        output_files = report_gen.generate_complete_report(
            image_path=image_path,
            clip_results=clip_results,
            vision_results=vision_results,
            iec_classification=action_plan,
            metadata=processed['metadata'],
            formats=["json", "html", "pdf"]
        )

        print("✓ Reports generated:")
        for format_type, file_path in output_files.items():
            print(f"  {format_type.upper()}: {file_path}")
        print()
    except Exception as e:
        print(f"✗ Report generation error: {e}")

    print("=" * 70)
    print("Advanced analysis complete!")
    print("=" * 70)
    print()


def demo_batch_analysis(image_paths: list):
    """
    Demonstrate batch processing of multiple images.

    Args:
        image_paths: List of image paths
    """
    print("=" * 70)
    print("PV IMAGE ANALYSIS DEMO - Batch Processing")
    print("=" * 70)
    print()

    processor = ImageProcessor()
    clip_classifier = CLIPDefectClassifier()

    print(f"Processing {len(image_paths)} images...")
    print()

    results = []

    for i, image_path in enumerate(image_paths, 1):
        print(f"[{i}/{len(image_paths)}] Analyzing: {Path(image_path).name}")

        try:
            # Process image
            processed = processor.process_image_pipeline(image_path)

            # CLIP classification
            clip_results = clip_classifier.detect_defects(processed['clip_ready'])

            results.append({
                "image": image_path,
                "success": True,
                "has_defects": clip_results['has_defects'],
                "top_defect": clip_results['top_prediction']['category'],
                "confidence": clip_results['top_prediction']['confidence']
            })

            status = "✓ PASS" if not clip_results['has_defects'] else "⚠ DEFECTS FOUND"
            print(f"  {status} - {clip_results['top_prediction']['category']}")

        except Exception as e:
            results.append({
                "image": image_path,
                "success": False,
                "error": str(e)
            })
            print(f"  ✗ ERROR: {e}")

        print()

    # Summary
    print("=" * 70)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 70)
    successful = sum(1 for r in results if r['success'])
    with_defects = sum(1 for r in results if r.get('has_defects', False))

    print(f"Total images: {len(image_paths)}")
    print(f"Successfully processed: {successful}")
    print(f"Images with defects: {with_defects}")
    print(f"Images without defects: {successful - with_defects}")
    print()


def main():
    """Main demo function."""
    import argparse

    parser = argparse.ArgumentParser(description="PV Image Analysis Demo")
    parser.add_argument(
        "image_path",
        nargs="?",
        help="Path to PV panel image"
    )
    parser.add_argument(
        "--mode",
        choices=["basic", "advanced", "batch"],
        default="basic",
        help="Analysis mode"
    )
    parser.add_argument(
        "--batch",
        nargs="+",
        help="Multiple image paths for batch processing"
    )

    args = parser.parse_args()

    # If no image provided, show usage
    if not args.image_path and not args.batch:
        print("=" * 70)
        print("PV IMAGE ANALYSIS MODULE - DEMO")
        print("=" * 70)
        print()
        print("Usage:")
        print("  python demo_analysis.py <image_path> [--mode basic|advanced]")
        print("  python demo_analysis.py --mode batch --batch <image1> <image2> ...")
        print()
        print("Examples:")
        print("  python demo_analysis.py demo_images/panel1.jpg")
        print("  python demo_analysis.py demo_images/panel1.jpg --mode advanced")
        print("  python demo_analysis.py --mode batch --batch img1.jpg img2.jpg")
        print()
        print("Features:")
        print("  • Image upload and preprocessing for EL, thermal, and IV curve images")
        print("  • CLIP-based defect classification")
        print("  • GPT-4o Vision detailed analysis (requires API key)")
        print("  • IEC TS 60904-13 based defect categorization")
        print("  • Comprehensive report generation (JSON, HTML, PDF)")
        print()
        print("Setup:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Copy .env.example to .env")
        print("  3. Add your OpenAI API key to .env (for advanced mode)")
        print("  4. Place test images in examples/demo_images/")
        print()
        return

    # Run appropriate demo
    if args.mode == "batch" and args.batch:
        demo_batch_analysis(args.batch)
    elif args.mode == "advanced":
        demo_advanced_analysis(args.image_path)
    else:
        demo_basic_analysis(args.image_path)


if __name__ == "__main__":
    main()
