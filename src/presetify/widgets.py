"""Custom TUI widgets for visualizing Lightroom adjustments."""

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual.widget import Widget
from textual.widgets import Static

from .models import LightroomAdjustments, ToneCurve


class AdjustmentSlider(Static):
    """Visual representation of a single Lightroom adjustment slider."""

    def __init__(
        self,
        label: str,
        value: float | int | None,
        min_val: float,
        max_val: float,
        unit: str = "",
        **kwargs,
    ):
        """
        Create an adjustment slider widget.

        Args:
            label: Name of the adjustment (e.g., "Exposure")
            value: Current value of the adjustment
            min_val: Minimum possible value
            max_val: Maximum possible value
            unit: Optional unit suffix (e.g., "K" for temperature)
        """
        super().__init__("", **kwargs)
        self.label = label
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit

    def render(self) -> str:
        """Render the slider as text."""
        if self.value is None:
            return f"{self.label:20s} [dim]Not adjusted[/dim]"

        # Calculate percentage position
        range_val = self.max_val - self.min_val
        normalized = (self.value - self.min_val) / range_val if range_val != 0 else 0.5
        percentage = max(0, min(1, normalized))

        # Create slider bar (40 characters wide)
        bar_width = 40
        filled = int(percentage * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        # Format value with proper sign and unit
        if isinstance(self.value, float):
            value_str = f"{self.value:+.2f}{self.unit}"
        else:
            value_str = f"{self.value:+d}{self.unit}"

        # Color based on value
        if self.value > 0:
            color = "cyan"
        elif self.value < 0:
            color = "yellow"
        else:
            color = "white"

        return (
            f"{self.label:20s} {value_str:>10s}  "
            f"[{color}]{bar}[/{color}]  "
            f"[dim]({self.min_val:+.0f} to {self.max_val:+.0f})[/dim]"
        )


class ToneCurveWidget(Static):
    """Visual representation of a Lightroom tone curve."""

    def __init__(self, tone_curve: ToneCurve | None, **kwargs):
        """
        Create a tone curve widget.

        Args:
            tone_curve: ToneCurve object to visualize
        """
        super().__init__("", **kwargs)
        self.tone_curve = tone_curve

    def render(self) -> str:
        """Render the tone curve as ASCII art."""
        if not self.tone_curve or not self.tone_curve.points:
            return "[dim]No tone curve adjustments[/dim]"

        # Create ASCII art tone curve
        width = 60
        height = 20
        points = self.tone_curve.points

        # Initialize grid
        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Draw axes
        for y in range(height):
            grid[y][0] = "│"
        for x in range(width):
            grid[height - 1][x] = "─"
        grid[height - 1][0] = "└"

        # Normalize and plot points
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            # Normalize to grid coordinates
            gx1 = int((x1 / 255) * (width - 2)) + 1
            gy1 = height - 2 - int((y1 / 255) * (height - 2))
            gx2 = int((x2 / 255) * (width - 2)) + 1
            gy2 = height - 2 - int((y2 / 255) * (height - 2))

            # Draw line between points using Bresenham's algorithm
            self._draw_line(grid, gx1, gy1, gx2, gy2)

        # Convert grid to string
        lines = ["".join(row) for row in grid]
        curve_str = "\n".join(lines)

        return (
            f"[bold cyan]Tone Curve[/bold cyan]\n"
            f"[dim]Output[/dim]\n"
            f"{curve_str}\n"
            f"{' ' * (width - 10)}[dim]Input[/dim]"
        )

    def _draw_line(self, grid, x1, y1, x2, y2):
        """Draw a line on the grid using Bresenham's algorithm."""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        height = len(grid)
        width = len(grid[0])

        while True:
            # Plot point if within bounds
            if 0 <= y1 < height and 0 <= x1 < width:
                if grid[y1][x1] == " " or grid[y1][x1] == "─":
                    grid[y1][x1] = "●"

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy


class AdjustmentsPanel(Static):
    """Panel displaying all Lightroom adjustments with sliders."""

    def __init__(self, adjustments: LightroomAdjustments, **kwargs):
        """
        Create an adjustments panel.

        Args:
            adjustments: LightroomAdjustments object to display
        """
        super().__init__("", **kwargs)
        self.adjustments = adjustments

    def render(self) -> str:
        """Render all adjustments as sliders."""
        if not self.adjustments.has_adjustments():
            return "[yellow]No Lightroom adjustments found in this image[/yellow]"

        sections = []

        # Basic adjustments
        basic = [
            ("Exposure", self.adjustments.exposure, -5.0, 5.0, ""),
            ("Contrast", self.adjustments.contrast, -100, 100, ""),
            ("Highlights", self.adjustments.highlights, -100, 100, ""),
            ("Shadows", self.adjustments.shadows, -100, 100, ""),
            ("Whites", self.adjustments.whites, -100, 100, ""),
            ("Blacks", self.adjustments.blacks, -100, 100, ""),
        ]

        basic_lines = ["[bold]Basic Adjustments[/bold]"]
        for label, value, min_val, max_val, unit in basic:
            if value is not None:
                slider = AdjustmentSlider(label, value, min_val, max_val, unit)
                basic_lines.append(slider.render())

        if len(basic_lines) > 1:
            sections.append("\n".join(basic_lines))

        # Color adjustments
        color = [
            ("Temperature", self.adjustments.temperature, -10000, 10000, "K"),
            ("Tint", self.adjustments.tint, -150, 150, ""),
            ("Vibrance", self.adjustments.vibrance, -100, 100, ""),
            ("Saturation", self.adjustments.saturation, -100, 100, ""),
        ]

        color_lines = ["[bold]Color Adjustments[/bold]"]
        for label, value, min_val, max_val, unit in color:
            if value is not None:
                slider = AdjustmentSlider(label, value, min_val, max_val, unit)
                color_lines.append(slider.render())

        if len(color_lines) > 1:
            sections.append("\n".join(color_lines))

        # Presence
        presence = [
            ("Clarity", self.adjustments.clarity, -100, 100, ""),
            ("Dehaze", self.adjustments.dehaze, -100, 100, ""),
            ("Texture", self.adjustments.texture, -100, 100, ""),
        ]

        presence_lines = ["[bold]Presence[/bold]"]
        for label, value, min_val, max_val, unit in presence:
            if value is not None:
                slider = AdjustmentSlider(label, value, min_val, max_val, unit)
                presence_lines.append(slider.render())

        if len(presence_lines) > 1:
            sections.append("\n".join(presence_lines))

        # Tone curve
        if self.adjustments.tone_curve:
            curve_widget = ToneCurveWidget(self.adjustments.tone_curve)
            sections.append(curve_widget.render())

        return "\n\n".join(sections)
