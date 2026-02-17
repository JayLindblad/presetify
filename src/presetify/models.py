"""Data models for Lightroom adjustments and presets."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class ToneCurve:
    """Represents a tone curve with control points."""

    points: List[Tuple[int, int]] = field(default_factory=list)  # (input, output) pairs

    def __str__(self) -> str:
        """String representation for XMP."""
        if not self.points:
            return ""
        return ", ".join(f"{x}, {y}" for x, y in self.points)


@dataclass
class LightroomAdjustments:
    """All Lightroom adjustment parameters extracted from an image."""

    # Basic adjustments
    exposure: Optional[float] = None  # -5.0 to +5.0
    contrast: Optional[int] = None  # -100 to +100
    highlights: Optional[int] = None  # -100 to +100
    shadows: Optional[int] = None  # -100 to +100
    whites: Optional[int] = None  # -100 to +100
    blacks: Optional[int] = None  # -100 to +100

    # Color adjustments
    temperature: Optional[int] = None  # Kelvin offset
    tint: Optional[int] = None  # -150 to +150
    vibrance: Optional[int] = None  # -100 to +100
    saturation: Optional[int] = None  # -100 to +100

    # Presence
    clarity: Optional[int] = None  # -100 to +100
    dehaze: Optional[int] = None  # -100 to +100
    texture: Optional[int] = None  # -100 to +100

    # Tone curve
    tone_curve: Optional[ToneCurve] = None

    # Sharpening
    sharpness: Optional[int] = None  # 0 to 150

    # Noise reduction
    luminance_noise_reduction: Optional[int] = None  # 0 to 100
    color_noise_reduction: Optional[int] = None  # 0 to 100

    # Effects
    vignette_amount: Optional[int] = None  # -100 to +100
    grain_amount: Optional[int] = None  # 0 to 100

    # HSL adjustments (simplified - we can expand later)
    hue_adjustments: dict[str, int] = field(default_factory=dict)
    saturation_adjustments: dict[str, int] = field(default_factory=dict)
    luminance_adjustments: dict[str, int] = field(default_factory=dict)

    # Metadata
    source_file: Optional[str] = None

    def has_adjustments(self) -> bool:
        """Check if any adjustments were found."""
        basic_adjustments = [
            self.exposure, self.contrast, self.highlights, self.shadows,
            self.whites, self.blacks, self.temperature, self.tint,
            self.vibrance, self.saturation, self.clarity, self.dehaze,
            self.texture, self.sharpness
        ]
        return any(adj is not None for adj in basic_adjustments) or bool(self.tone_curve)


@dataclass
class PresetMetadata:
    """Metadata for the generated preset."""

    name: str
    description: Optional[str] = None
    uuid: Optional[str] = None
