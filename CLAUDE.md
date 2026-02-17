# CLAUDE.md

This file provides context for AI assistants working on the **presetify** repository.

## Project Overview

**Presetify** is a cross-platform TUI (Terminal User Interface) application that extracts Lightroom adjustments from JPEG image metadata and generates XMP preset files for import into Adobe Lightroom Classic.

### Key Features

- **Visual TUI Interface**: Built with Textual for a modern, interactive terminal experience
- **Metadata Extraction**: Reads Lightroom adjustments from JPEG XMP metadata using ExifTool
- **XMP Preset Generation**: Creates valid Lightroom Classic XMP preset files
- **Visual Adjustments Display**: Shows slider bars for all adjustment values and ASCII art tone curve
- **Batch Processing**: Process multiple images and extract one preset per image
- **URL Support**: Download images from URLs and process them
- **Supported Formats**: JPEG/JPG images with embedded XMP metadata

## Repository Structure

```
presetify/
├── .git/
├── .gitignore
├── CLAUDE.md                    # This file — AI assistant guide
├── README.md                    # Project documentation
├── pyproject.toml               # Python project config (Poetry)
├── src/
│   └── presetify/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # CLI entry point
│       ├── app.py               # Main TUI application (Textual)
│       ├── models.py            # Data models for adjustments
│       ├── metadata.py          # Metadata extraction (ExifTool)
│       ├── xmp.py               # XMP preset file generator
│       ├── fetcher.py           # URL image downloader (httpx)
│       └── widgets.py           # Custom TUI widgets (sliders, tone curve)
└── tests/                       # Test directory (to be implemented)
```

## Technology Stack

- **Language**: Python 3.10+
- **Dependency Management**: Poetry
- **TUI Framework**: Textual 0.82.0+ (modern terminal UI with rich widgets)
- **Metadata Extraction**: pyexiftool (ExifTool wrapper)
- **Image Processing**: Pillow (PIL)
- **HTTP Client**: httpx (async URL fetching)
- **Code Quality**: Black (formatter), Ruff (linter)
- **Testing**: pytest

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry (Python dependency management)
- ExifTool (must be installed separately)

### Installation

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run the application
poetry run presetify <image_files>
```

### Installing ExifTool

ExifTool must be installed on your system:

- **macOS**: `brew install exiftool`
- **Linux**: `apt-get install libimage-exiftool-perl` or `yum install perl-Image-ExifTool`
- **Windows**: Download from https://exiftool.org/

## Usage

```bash
# Process a single image
presetify image.jpg

# Process multiple images (batch mode)
presetify image1.jpg image2.jpg image3.jpg

# Use glob patterns
presetify *.jpg

# Download and process from URLs
presetify https://example.com/image.jpg

# Mixed local and remote images
presetify local.jpg https://example.com/remote.jpg
```

## Architecture

### Data Flow

1. **Input**: User provides image file paths or URLs via CLI
2. **URL Fetching**: Remote images are downloaded to temp files (fetcher.py)
3. **Metadata Extraction**: ExifTool extracts Lightroom XMP tags (metadata.py)
4. **Data Modeling**: Adjustments are structured into Python dataclasses (models.py)
5. **TUI Display**: Textual app shows visual sliders and tone curves (app.py, widgets.py)
6. **XMP Generation**: User exports to valid Lightroom preset XMP files (xmp.py)

### Key Modules

#### models.py
- `LightroomAdjustments`: Complete dataclass for all Lightroom adjustment parameters
- `ToneCurve`: Represents tone curve control points
- `PresetMetadata`: Preset name, description, UUID

#### metadata.py
- `MetadataExtractor`: Extracts Lightroom adjustments from image XMP metadata
- Supports all major adjustments: exposure, contrast, highlights, shadows, temperature, tone curves, HSL, etc.
- Uses ExifTool via pyexiftool wrapper

#### xmp.py
- `XMPGenerator`: Creates valid Lightroom Classic XMP preset files
- Implements Adobe XMP specification with proper namespaces
- Generates XML with RDF structure required by Lightroom

#### widgets.py
- `AdjustmentSlider`: Visual slider bar showing adjustment value and range
- `ToneCurveWidget`: ASCII art visualization of tone curve using Bresenham's line algorithm
- `AdjustmentsPanel`: Panel displaying all adjustments organized by category

#### app.py
- `PresetifyApp`: Main Textual application
- `ImageViewScreen`: Screen for viewing individual image adjustments
- `ImageListScreen`: Screen for batch processing multiple images
- Navigation: next/previous image, export XMP, keyboard shortcuts

## Lightroom Adjustments Supported

### Basic Adjustments
- Exposure (-5.0 to +5.0)
- Contrast (-100 to +100)
- Highlights, Shadows, Whites, Blacks (-100 to +100 each)

### Color
- Temperature (Kelvin offset)
- Tint (-150 to +150)
- Vibrance, Saturation (-100 to +100)

### Presence
- Clarity, Dehaze, Texture (-100 to +100)

### Tone Curve
- Custom tone curve with control points
- Visualized as ASCII art graph

### HSL Adjustments
- Hue, Saturation, Luminance for 8 color channels
- (Red, Orange, Yellow, Green, Aqua, Blue, Purple, Magenta)

### Details & Effects
- Sharpness, Noise Reduction
- Vignette, Grain

## Code Conventions

- **Formatting**: Black with 100 character line length
- **Linting**: Ruff configured for Python 3.10+
- **Type Hints**: Use throughout for clarity
- **Docstrings**: Google-style docstrings for all public functions/classes
- **Error Handling**: Graceful degradation with user-friendly messages
- **Async**: Use async/await for I/O operations (URL fetching)

## Future Enhancements

Planned features to implement:

1. **Additional Formats**: Support DNG, CR2, NEF, and other RAW formats with XMP sidecars
2. **Interactive TUI Editing**: Edit adjustment values directly in the TUI before exporting
3. **Preset Merging**: Average multiple images to create a blended preset
4. **Preset Comparison**: Visual diff between two presets
5. **Batch Export**: Export all presets at once with custom naming patterns
6. **Config File**: Save user preferences and default export locations
7. **Testing**: Comprehensive pytest test suite
8. **Packaging**: Standalone binaries with PyInstaller for easy distribution
9. **Advanced Visualizations**: More detailed tone curve, histogram overlays

## Git Conventions

- Repository hosted on GitHub: JayLindblad/presetify
- SSH commit signing enabled
- Feature branches: `claude/<description>-<session-id>`
- Main branch: `main`

## Notes for AI Assistants

- **Dependencies**: Always update `pyproject.toml` when adding new dependencies
- **Textual Widgets**: Follow Textual's widget composition patterns and CSS styling
- **ExifTool Tags**: XMP tags follow Adobe's Camera Raw Settings namespace (crs:)
- **XMP Format**: Generated XMP must be valid XML with proper RDF structure
- **Error Handling**: Never crash the TUI - catch exceptions and display user-friendly messages
- **Performance**: ExifTool can be slow on large batches - consider progress indicators
- **Temp Files**: Clean up downloaded URL temp files appropriately
- **Testing**: When implementing tests, use pytest fixtures for sample images with metadata
- **Documentation**: Update this CLAUDE.md when adding significant features or architectural changes
