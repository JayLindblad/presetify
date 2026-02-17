# Presetify

**Extract Lightroom presets from images with a beautiful TUI**

Presetify is a cross-platform terminal application that reads Lightroom adjustments from JPEG image metadata and generates XMP preset files you can import into Adobe Lightroom Classic.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🖥️ **Beautiful TUI** - Modern terminal interface built with Textual
- 📊 **Visual Adjustments** - See slider bars for all adjustment values
- 📈 **Tone Curve Visualization** - ASCII art rendering of tone curves
- 🔄 **Batch Processing** - Process multiple images at once
- 🌐 **URL Support** - Download and process images from URLs
- 💾 **XMP Export** - Generate valid Lightroom Classic preset files
- ⚡ **Fast & Lightweight** - No GUI overhead, works entirely in the terminal

## What is this for?

Have you ever seen a photo with beautiful Lightroom adjustments and wished you could extract those settings as a preset? That's what Presetify does!

When you export a JPEG from Lightroom, the adjustment metadata is embedded in the image. Presetify:
1. Reads that embedded XMP metadata
2. Shows you all the adjustments visually
3. Lets you export them as an XMP preset file
4. You can then import that preset into Lightroom Classic and apply it to your own photos

## Installation

### Prerequisites

- Python 3.10 or higher
- ExifTool (see below)

### Install ExifTool

ExifTool is required for reading image metadata:

**macOS:**
```bash
brew install exiftool
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install libimage-exiftool-perl
```

**Linux (Fedora/RHEL):**
```bash
sudo yum install perl-Image-ExifTool
```

**Windows:**
Download from [exiftool.org](https://exiftool.org/)

### Install Presetify

```bash
# Clone the repository
git clone https://github.com/JayLindblad/presetify.git
cd presetify

# Install with Poetry (recommended)
poetry install
poetry run presetify --help

# Or install with pip
pip install .
presetify --help
```

## Usage

### Basic Usage

```bash
# Process a single image
presetify photo.jpg

# Process multiple images
presetify photo1.jpg photo2.jpg photo3.jpg

# Use glob patterns
presetify *.jpg
presetify ~/Photos/exports/*.jpg

# Download from URL
presetify https://example.com/photo.jpg

# Mix local and remote
presetify local.jpg https://example.com/remote.jpg
```

### TUI Navigation

Once the TUI launches:

- **`n` or `→`** - Next image
- **`p` or `←`** - Previous image
- **`e`** - Export current image as XMP preset
- **`q`** - Quit application
- **Mouse clicks** - Click buttons

### What Gets Extracted

Presetify extracts all major Lightroom adjustments:

**Basic Tab:**
- Exposure, Contrast
- Highlights, Shadows, Whites, Blacks

**Color:**
- Temperature, Tint
- Vibrance, Saturation

**Presence:**
- Clarity, Dehaze, Texture

**Tone Curve:**
- Complete curve with all control points

**HSL:**
- Hue, Saturation, Luminance for all 8 color channels

**Details & Effects:**
- Sharpening, Noise Reduction
- Vignette, Grain

## Example Output

When you run Presetify, you'll see something like this:

```
┌─ Presetify ─────────────────────────────────────────────────────┐
│ Image 1 of 3: sunset.jpg                                         │
├──────────────────────────────────────────────────────────────────┤
│ Basic Adjustments                                                │
│ Exposure              +1.20  ████████████░░░░░░░░░░░░  (-5 to +5)│
│ Contrast               +15  ████████████████░░░░░░░░  (-100 to +100)│
│ Highlights             -45  ██████░░░░░░░░░░░░░░░░░░  (-100 to +100)│
│                                                                  │
│ Tone Curve                                                       │
│ Output                                                           │
│ ┌────────────────────────────────┐                              │
│ │          ●────                  │                              │
│ │        ●                        │                              │
│ │      ●                          │                              │
│ │    ●                            │                              │
│ │  ●                              │                              │
│ └────────────────────────────────┘                              │
│                           Input                                  │
│                                                                  │
│ [← Previous]  [Export XMP]  [Next →]                            │
└──────────────────────────────────────────────────────────────────┘
```

## Output Files

Exported XMP presets are saved in the same directory as the source image:

```
photo.jpg → photo_preset.xmp
```

### Importing Presets into Lightroom

1. Open Lightroom Classic
2. Go to **Develop** module
3. In the **Presets** panel, click **+** → **Import Presets**
4. Select the `.xmp` file(s) generated by Presetify
5. The preset will appear in your Presets panel
6. Apply it to any photo!

## Supported Formats

Currently supported:
- ✅ JPEG/JPG with embedded XMP metadata

Planned for future releases:
- 🔲 DNG (Adobe Digital Negative)
- 🔲 RAW formats with XMP sidecars (CR2, NEF, ARW, etc.)

## Limitations

- Only works with images that have been **processed in Lightroom** and exported with metadata
- The source image must have been exported with **"Include Develop Settings"** enabled in Lightroom's export dialog
- Not all Lightroom adjustments may be preserved (e.g., local adjustments, graduated filters)

## Development

### Project Structure

```
src/presetify/
├── cli.py         # Command-line interface
├── app.py         # Main TUI application
├── models.py      # Data models
├── metadata.py    # Metadata extraction
├── xmp.py         # XMP generation
├── fetcher.py     # URL fetching
└── widgets.py     # Custom TUI widgets
```

### Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Roadmap

- [ ] Support for DNG and RAW formats
- [ ] Interactive editing of adjustments in TUI
- [ ] Preset comparison/diff view
- [ ] Batch export with custom naming
- [ ] Standalone binary distributions
- [ ] Preset merging (average multiple images)

## License

MIT License - see LICENSE file for details

## Credits

Built with:
- [Textual](https://textual.textualize.io/) - Modern TUI framework
- [ExifTool](https://exiftool.org/) - Metadata extraction
- [Pillow](https://python-pillow.org/) - Image handling

## Support

- 🐛 [Report a bug](https://github.com/JayLindblad/presetify/issues)
- 💡 [Request a feature](https://github.com/JayLindblad/presetify/issues)
- 📖 [Read the docs](https://github.com/JayLindblad/presetify/blob/main/CLAUDE.md)

---

Made with ❤️ for photographers who love the terminal