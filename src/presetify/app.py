"""Main TUI application for Presetify."""

import asyncio
from pathlib import Path
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, Label, DirectoryTree, Input
from textual.binding import Binding
from textual.screen import Screen

from .models import LightroomAdjustments, PresetMetadata
from .metadata import MetadataExtractor
from .xmp import XMPGenerator
from .fetcher import ImageFetcher
from .widgets import AdjustmentsPanel


class ImageListScreen(Screen):
    """Screen for selecting images to process."""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "back", "Back", priority=True),
    ]

    def __init__(self, image_paths: List[Path], **kwargs):
        super().__init__(**kwargs)
        self.image_paths = image_paths
        self.current_index = 0

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        yield Container(
            Label(f"[bold cyan]Found {len(self.image_paths)} images[/bold cyan]", id="image-count"),
            VerticalScroll(
                Static(id="image-list"),
            ),
            Horizontal(
                Button("Process All", variant="primary", id="process-all"),
                Button("Back", variant="default", id="back-btn"),
                id="button-row",
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount."""
        self._update_image_list()

    def _update_image_list(self) -> None:
        """Update the list of images."""
        lines = []
        for i, path in enumerate(self.image_paths, 1):
            lines.append(f"{i}. {path.name}")

        image_list = self.query_one("#image-list", Static)
        image_list.update("\n".join(lines))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "process-all":
            await self._process_images()
        elif event.button.id == "back-btn":
            self.app.pop_screen()

    async def _process_images(self) -> None:
        """Process all images and switch to viewing screen."""
        if self.image_paths:
            self.app.push_screen(ImageViewScreen(self.image_paths))

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class ImageViewScreen(Screen):
    """Screen for viewing image adjustments and exporting presets."""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("n", "next_image", "Next", priority=True),
        Binding("p", "prev_image", "Previous", priority=True),
        Binding("e", "export", "Export", priority=True),
        Binding("escape", "back", "Back", priority=True),
    ]

    def __init__(self, image_paths: List[Path], **kwargs):
        super().__init__(**kwargs)
        self.image_paths = image_paths
        self.current_index = 0
        self.adjustments: Optional[LightroomAdjustments] = None
        self.extractor = MetadataExtractor()
        self.generator = XMPGenerator()

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        yield Container(
            Label("", id="image-info"),
            VerticalScroll(
                Static(id="adjustments-panel"),
                id="scroll-area",
            ),
            Horizontal(
                Button("← Previous (p)", variant="default", id="prev-btn"),
                Button("Export XMP (e)", variant="primary", id="export-btn"),
                Button("Next → (n)", variant="default", id="next-btn"),
                id="button-row",
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Handle screen mount."""
        self._load_current_image()

    def _load_current_image(self) -> None:
        """Load and display the current image's adjustments."""
        if not self.image_paths:
            return

        current_path = self.image_paths[self.current_index]

        # Update info label
        info_label = self.query_one("#image-info", Label)
        info_label.update(
            f"[bold]Image {self.current_index + 1} of {len(self.image_paths)}:[/bold] "
            f"[cyan]{current_path.name}[/cyan]"
        )

        # Extract metadata
        self.adjustments = self.extractor.extract(current_path)

        # Display adjustments
        panel = self.query_one("#adjustments-panel", Static)
        if self.adjustments and self.adjustments.has_adjustments():
            adjustments_widget = AdjustmentsPanel(self.adjustments)
            panel.update(adjustments_widget.render())
        else:
            panel.update("[yellow]No Lightroom adjustments found in this image[/yellow]")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "next-btn":
            self.action_next_image()
        elif event.button.id == "prev-btn":
            self.action_prev_image()
        elif event.button.id == "export-btn":
            self.action_export()

    def action_next_image(self) -> None:
        """Move to next image."""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self._load_current_image()

    def action_prev_image(self) -> None:
        """Move to previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self._load_current_image()

    def action_export(self) -> None:
        """Export current adjustments as XMP preset."""
        if not self.adjustments or not self.adjustments.has_adjustments():
            self.notify("No adjustments to export", severity="warning")
            return

        # Generate output filename
        current_path = self.image_paths[self.current_index]
        output_path = current_path.parent / f"{current_path.stem}_preset.xmp"

        # Create preset metadata
        metadata = PresetMetadata(
            name=current_path.stem,
            description=f"Preset extracted from {current_path.name}",
        )

        # Generate XMP file
        try:
            self.generator.generate(self.adjustments, metadata, output_path)
            self.notify(f"✓ Preset saved to {output_path.name}", severity="information")
        except Exception as e:
            self.notify(f"Error exporting preset: {e}", severity="error")

    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class PresetifyApp(App):
    """Main Presetify TUI application."""

    CSS = """
    Screen {
        align: center middle;
    }

    Container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    #image-info {
        height: 3;
        content-align: center middle;
        background: $panel;
        border: solid $primary;
        margin-bottom: 1;
    }

    #image-count {
        height: 3;
        content-align: center middle;
        background: $panel;
        border: solid $primary;
        margin-bottom: 1;
    }

    #scroll-area {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }

    #adjustments-panel {
        width: 100%;
    }

    #image-list {
        width: 100%;
    }

    #button-row {
        height: auto;
        width: 100%;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    TITLE = "Presetify - Lightroom Preset Extractor"

    def __init__(self, image_paths: List[Path], **kwargs):
        super().__init__(**kwargs)
        self.image_paths = image_paths

    def on_mount(self) -> None:
        """Handle app mount."""
        if self.image_paths:
            self.push_screen(ImageViewScreen(self.image_paths))
        else:
            self.exit(message="No images provided")
