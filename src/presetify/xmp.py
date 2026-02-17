"""Generate Lightroom XMP preset files."""

import uuid
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.dom import minidom

from .models import LightroomAdjustments, PresetMetadata


class XMPGenerator:
    """Generate Lightroom Classic XMP preset files."""

    # XMP namespaces
    NAMESPACES = {
        "x": "adobe:ns:meta/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "crs": "http://ns.adobe.com/camera-raw-settings/1.0/",
    }

    def generate(
        self,
        adjustments: LightroomAdjustments,
        metadata: PresetMetadata,
        output_path: str | Path,
    ) -> None:
        """
        Generate an XMP preset file from Lightroom adjustments.

        Args:
            adjustments: Lightroom adjustments to include in preset
            metadata: Preset metadata (name, description)
            output_path: Path where XMP file should be saved
        """
        output_path = Path(output_path)

        # Build XMP structure
        xmp_doc = self._build_xmp_structure(adjustments, metadata)

        # Write to file with proper formatting
        xml_string = self._prettify_xml(xmp_doc)
        output_path.write_text(xml_string, encoding="utf-8")

    def _build_xmp_structure(
        self, adjustments: LightroomAdjustments, metadata: PresetMetadata
    ) -> ET.Element:
        """Build the XMP XML structure."""
        # Register namespaces
        for prefix, uri in self.NAMESPACES.items():
            ET.register_namespace(prefix, uri)

        # Root element
        root = ET.Element(
            f"{{{self.NAMESPACES['x']}}}xmpmeta",
            attrib={f"{{{self.NAMESPACES['x']}}}xmptk": "Adobe XMP Core 7.0-c000 1.000000"},
        )

        # RDF element
        rdf = ET.SubElement(root, f"{{{self.NAMESPACES['rdf']}}}RDF")

        # Description element with all adjustments
        desc_attribs = {
            f"{{{self.NAMESPACES['rdf']}}}about": "",
            f"{{{self.NAMESPACES['crs']}}}Version": "16.5",  # Lightroom Classic version
            f"{{{self.NAMESPACES['crs']}}}ProcessVersion": "11.0",
        }

        # Add adjustment attributes
        self._add_adjustments_to_attribs(adjustments, desc_attribs)

        desc = ET.SubElement(rdf, f"{{{self.NAMESPACES['rdf']}}}Description", attrib=desc_attribs)

        # Add tone curve as nested element if present
        if adjustments.tone_curve and adjustments.tone_curve.points:
            self._add_tone_curve_element(desc, adjustments.tone_curve)

        return root

    def _add_adjustments_to_attribs(
        self, adjustments: LightroomAdjustments, attribs: dict
    ) -> None:
        """Add adjustment values as XML attributes."""
        crs = self.NAMESPACES["crs"]

        # Map model attributes to XMP tags
        mappings = {
            "exposure": (f"{{{crs}}}Exposure2012", adjustments.exposure),
            "contrast": (f"{{{crs}}}Contrast2012", adjustments.contrast),
            "highlights": (f"{{{crs}}}Highlights2012", adjustments.highlights),
            "shadows": (f"{{{crs}}}Shadows2012", adjustments.shadows),
            "whites": (f"{{{crs}}}Whites2012", adjustments.whites),
            "blacks": (f"{{{crs}}}Blacks2012", adjustments.blacks),
            "temperature": (f"{{{crs}}}Temperature", adjustments.temperature),
            "tint": (f"{{{crs}}}Tint", adjustments.tint),
            "vibrance": (f"{{{crs}}}Vibrance", adjustments.vibrance),
            "saturation": (f"{{{crs}}}Saturation", adjustments.saturation),
            "clarity": (f"{{{crs}}}Clarity2012", adjustments.clarity),
            "dehaze": (f"{{{crs}}}Dehaze", adjustments.dehaze),
            "texture": (f"{{{crs}}}Texture", adjustments.texture),
            "sharpness": (f"{{{crs}}}Sharpness", adjustments.sharpness),
            "luminance_noise_reduction": (
                f"{{{crs}}}LuminanceSmoothing",
                adjustments.luminance_noise_reduction,
            ),
            "color_noise_reduction": (
                f"{{{crs}}}ColorNoiseReduction",
                adjustments.color_noise_reduction,
            ),
            "vignette_amount": (
                f"{{{crs}}}PostCropVignetteAmount",
                adjustments.vignette_amount,
            ),
            "grain_amount": (f"{{{crs}}}GrainAmount", adjustments.grain_amount),
        }

        # Add non-null values
        for key, (xmp_tag, value) in mappings.items():
            if value is not None:
                # Format float values properly
                if isinstance(value, float):
                    attribs[xmp_tag] = f"{value:+.2f}" if value >= 0 else f"{value:.2f}"
                else:
                    attribs[xmp_tag] = str(value)

        # Add HSL adjustments
        self._add_hsl_adjustments(attribs, adjustments)

    def _add_hsl_adjustments(self, attribs: dict, adjustments: LightroomAdjustments) -> None:
        """Add HSL adjustments to attributes."""
        crs = self.NAMESPACES["crs"]
        colors = ["Red", "Orange", "Yellow", "Green", "Aqua", "Blue", "Purple", "Magenta"]

        for color in colors:
            color_lower = color.lower()

            if color_lower in adjustments.hue_adjustments:
                attribs[f"{{{crs}}}HueAdjustment{color}"] = str(
                    adjustments.hue_adjustments[color_lower]
                )

            if color_lower in adjustments.saturation_adjustments:
                attribs[f"{{{crs}}}SaturationAdjustment{color}"] = str(
                    adjustments.saturation_adjustments[color_lower]
                )

            if color_lower in adjustments.luminance_adjustments:
                attribs[f"{{{crs}}}LuminanceAdjustment{color}"] = str(
                    adjustments.luminance_adjustments[color_lower]
                )

    def _add_tone_curve_element(self, parent: ET.Element, tone_curve) -> None:
        """Add tone curve as a nested RDF Seq element."""
        crs = self.NAMESPACES["crs"]
        rdf = self.NAMESPACES["rdf"]

        # Create ToneCurvePV2012 element
        curve_elem = ET.SubElement(parent, f"{{{crs}}}ToneCurvePV2012")
        seq = ET.SubElement(curve_elem, f"{{{rdf}}}Seq")

        # Add each point as an li element
        for x, y in tone_curve.points:
            li = ET.SubElement(seq, f"{{{rdf}}}li")
            li.text = f"{x}, {y}"

    def _prettify_xml(self, elem: ET.Element) -> str:
        """Format XML with proper indentation."""
        rough_string = ET.tostring(elem, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
