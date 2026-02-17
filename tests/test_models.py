"""Tests for data models."""

import pytest
from presetify.models import LightroomAdjustments, ToneCurve, PresetMetadata


def test_tone_curve_creation():
    """Test creating a tone curve with points."""
    curve = ToneCurve(points=[(0, 0), (128, 128), (255, 255)])
    assert len(curve.points) == 3
    assert curve.points[0] == (0, 0)
    assert curve.points[1] == (128, 128)
    assert curve.points[2] == (255, 255)


def test_tone_curve_string_representation():
    """Test tone curve string conversion for XMP."""
    curve = ToneCurve(points=[(0, 0), (64, 80), (255, 255)])
    result = str(curve)
    assert result == "0, 0, 64, 80, 255, 255"


def test_adjustments_has_adjustments_true():
    """Test has_adjustments returns True when adjustments exist."""
    adj = LightroomAdjustments(exposure=1.5, contrast=20)
    assert adj.has_adjustments() is True


def test_adjustments_has_adjustments_false():
    """Test has_adjustments returns False when no adjustments exist."""
    adj = LightroomAdjustments()
    assert adj.has_adjustments() is False


def test_adjustments_with_tone_curve():
    """Test adjustments with tone curve."""
    curve = ToneCurve(points=[(0, 0), (255, 255)])
    adj = LightroomAdjustments(tone_curve=curve)
    assert adj.has_adjustments() is True
    assert adj.tone_curve is not None


def test_preset_metadata_creation():
    """Test creating preset metadata."""
    metadata = PresetMetadata(
        name="Test Preset",
        description="A test preset",
        uuid="test-uuid-123"
    )
    assert metadata.name == "Test Preset"
    assert metadata.description == "A test preset"
    assert metadata.uuid == "test-uuid-123"


def test_adjustments_hsl_dictionaries():
    """Test HSL adjustment dictionaries."""
    adj = LightroomAdjustments(
        hue_adjustments={"red": 10, "blue": -5},
        saturation_adjustments={"green": 15},
        luminance_adjustments={"orange": -20}
    )
    assert adj.hue_adjustments["red"] == 10
    assert adj.saturation_adjustments["green"] == 15
    assert adj.luminance_adjustments["orange"] == -20
