# Demo Images Directory

This directory contains sample PV (photovoltaic) panel images for testing and demonstration purposes.

## Supported Image Types

### 1. Electroluminescence (EL) Images
- **Description**: Grayscale images showing solar cells under forward bias
- **File naming**: `el_*.jpg` or `el_*.png`
- **Best for detecting**: Cell cracks, micro-cracks, inactive areas, finger interruptions

### 2. Thermal/Infrared (IR) Images
- **Description**: Thermal camera images showing temperature distribution
- **File naming**: `thermal_*.jpg` or `ir_*.png`
- **Best for detecting**: Hot spots, bypass diode failures, abnormal heating

### 3. IV Curve Images
- **Description**: Current-Voltage characteristic plots
- **File naming**: `iv_*.jpg` or `iv_*.png`
- **Best for detecting**: Performance degradation, fill factor issues

### 4. Visual Inspection Images
- **Description**: Standard photographs of solar panels
- **File naming**: `visual_*.jpg` or `photo_*.png`
- **Best for detecting**: Physical damage, discoloration, delamination

## Adding Demo Images

To add your own demo images:

1. Place image files in this directory
2. Ensure images meet minimum requirements:
   - Minimum resolution: 512x512 pixels
   - Recommended: 1024x1024 or higher
   - Supported formats: JPG, PNG, BMP, TIFF

3. Run the demo script:
```bash
python ../demo_analysis.py demo_images/your_image.jpg
```

## Example Usage

```bash
# Analyze a single image
python ../demo_analysis.py demo_images/el_panel1.jpg --mode basic

# Batch process multiple images
python ../demo_analysis.py --mode batch --batch demo_images/el_*.jpg
```

## Image Quality Guidelines

For best results:
- **Focus**: Images should be sharp and in focus
- **Lighting**: Consistent lighting (especially for visual inspection)
- **Resolution**: Higher resolution provides better defect detection
- **Compression**: Minimize JPEG compression artifacts
- **Orientation**: Images should be properly oriented

## Sample Defects to Test

Try images containing:
- ✓ Cell cracks (various orientations)
- ✓ Hot spots (visible in thermal images)
- ✓ Discoloration or browning
- ✓ Broken or inactive cells
- ✓ Junction box issues
- ✓ Delamination
- ✓ Normal, healthy panels (for baseline)

## Data Privacy

**Note**: Do not commit proprietary or sensitive images to version control. This directory is for demonstration purposes only.
