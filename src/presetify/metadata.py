"""Extract Lightroom metadata from images."""

import json
from pathlib import Path
from typing import Optional
import exiftool

from .models import LightroomAdjustments, ToneCurve


class MetadataExtractor:
    """Extract Lightroom adjustments from image metadata using ExifTool."""

    # XMP namespace tags used by Lightroom
    LR_TAGS = {
        "XMP:Exposure2012": "exposure",
        "XMP:Contrast2012": "contrast",
        "XMP:Highlights2012": "highlights",
        "XMP:Shadows2012": "shadows",
        "XMP:Whites2012": "whites",
        "XMP:Blacks2012": "blacks",
        "XMP:Temperature": "temperature",
        "XMP:Tint": "tint",
        "XMP:Vibrance": "vibrance",
        "XMP:Saturation": "saturation",
        "XMP:Clarity2012": "clarity",
        "XMP:Dehaze": "dehaze",
        "XMP:Texture": "texture",
        "XMP:Sharpness": "sharpness",
        "XMP:LuminanceSmoothing": "luminance_noise_reduction",
        "XMP:ColorNoiseReduction": "color_noise_reduction",
        "XMP:PostCropVignetteAmount": "vignette_amount",
        "XMP:GrainAmount": "grain_amount",
        "XMP:ToneCurvePV2012": "tone_curve",
        "XMP:ToneCurvePV2012Red": "tone_curve_red",
        "XMP:ToneCurvePV2012Green": "tone_curve_green",
        "XMP:ToneCurvePV2012Blue": "tone_curve_blue",
    }

    def extract(self, image_path: str | Path) -> LightroomAdjustments:
        """
        Extract Lightroom adjustments from an image file.

        Args:
            image_path: Path to the image file

        Returns:
            LightroomAdjustments object with extracted data
        """
        image_path = Path(image_path)
        adjustments = LightroomAdjustments(source_file=str(image_path))

        try:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(str(image_path))

                if not metadata:
                    return adjustments

                # ExifTool returns a list with one dict per file
                data = metadata[0] if isinstance(metadata, list) else metadata

                # Extract basic adjustments
                for xmp_tag, attr_name in self.LR_TAGS.items():
                    if xmp_tag in data:
                        value = data[xmp_tag]

                        # Handle tone curve specially
                        if attr_name == "tone_curve":
                            adjustments.tone_curve = self._parse_tone_curve(value)
                        else:
                            setattr(adjustments, attr_name, value)

                # Extract HSL adjustments
                self._extract_hsl_adjustments(data, adjustments)

        except Exception as e:
            print(f"Error extracting metadata from {image_path}: {e}")

        return adjustments

    def _parse_tone_curve(self, curve_data: str | list) -> Optional[ToneCurve]:
        """
        Parse tone curve data from XMP.

        Lightroom stores tone curves as a list of points like:
        "0, 0, 32, 22, 64, 56, 128, 128, 192, 196, 255, 255"
        """
        if not curve_data:
            return None

        try:
            # If it's a string, split it
            if isinstance(curve_data, str):
                values = [int(v.strip()) for v in curve_data.split(",")]
            elif isinstance(curve_data, list):
                values = [int(v) for v in curve_data]
            else:
                return None

            # Parse pairs of (input, output)
            points = []
            for i in range(0, len(values), 2):
                if i + 1 < len(values):
                    points.append((values[i], values[i + 1]))

            return ToneCurve(points=points) if points else None

        except (ValueError, TypeError):
            return None

    def _extract_hsl_adjustments(self, data: dict, adjustments: LightroomAdjustments) -> None:
        """Extract HSL (Hue/Saturation/Luminance) adjustments."""
        colors = ["Red", "Orange", "Yellow", "Green", "Aqua", "Blue", "Purple", "Magenta"]

        for color in colors:
            # Hue adjustments
            hue_tag = f"XMP:HueAdjustment{color}"
            if hue_tag in data:
                adjustments.hue_adjustments[color.lower()] = data[hue_tag]

            # Saturation adjustments
            sat_tag = f"XMP:SaturationAdjustment{color}"
            if sat_tag in data:
                adjustments.saturation_adjustments[color.lower()] = data[sat_tag]

            # Luminance adjustments
            lum_tag = f"XMP:LuminanceAdjustment{color}"
            if lum_tag in data:
                adjustments.luminance_adjustments[color.lower()] = data[lum_tag]
