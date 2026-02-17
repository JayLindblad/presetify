"""Command-line interface for Presetify."""

import asyncio
import sys
from pathlib import Path
from typing import List

from .app import PresetifyApp
from .fetcher import ImageFetcher


def parse_arguments() -> List[Path]:
    """
    Parse command-line arguments.

    Returns:
        List of image file paths to process
    """
    args = sys.argv[1:]

    if not args:
        print("Usage: presetify <image_files_or_urls...>")
        print("\nExamples:")
        print("  presetify image.jpg")
        print("  presetify *.jpg")
        print("  presetify https://example.com/image.jpg")
        print("  presetify image1.jpg image2.jpg https://example.com/image3.jpg")
        sys.exit(1)

    image_paths = []
    urls = []

    for arg in args:
        if arg.startswith(("http://", "https://")):
            urls.append(arg)
        else:
            # Handle glob patterns and regular paths
            path = Path(arg)
            if path.exists() and path.is_file():
                image_paths.append(path)
            else:
                # Try to expand glob
                parent = path.parent if path.parent.exists() else Path.cwd()
                matches = list(parent.glob(path.name))
                image_paths.extend(p for p in matches if p.is_file())

    return image_paths, urls


async def fetch_urls(urls: List[str]) -> List[Path]:
    """
    Download images from URLs.

    Args:
        urls: List of image URLs

    Returns:
        List of downloaded image paths
    """
    if not urls:
        return []

    print(f"Downloading {len(urls)} images from URLs...")
    fetcher = ImageFetcher()
    paths = []

    for url in urls:
        print(f"  Fetching: {url}")
        path = await fetcher.fetch(url)
        if path:
            paths.append(path)
            print(f"    ✓ Saved to {path}")
        else:
            print(f"    ✗ Failed to download")

    return paths


def main():
    """Main entry point for the CLI."""
    try:
        # Parse arguments
        image_paths, urls = parse_arguments()

        # Download URLs if any
        if urls:
            downloaded_paths = asyncio.run(fetch_urls(urls))
            image_paths.extend(downloaded_paths)

        if not image_paths:
            print("Error: No valid image files found")
            sys.exit(1)

        # Filter for supported image formats
        supported_extensions = {".jpg", ".jpeg", ".JPG", ".JPEG"}
        valid_images = [p for p in image_paths if p.suffix in supported_extensions]

        if not valid_images:
            print("Error: No supported image files found (only JPEG supported)")
            sys.exit(1)

        print(f"\nFound {len(valid_images)} image(s) to process")
        print("Starting Presetify TUI...\n")

        # Launch TUI application
        app = PresetifyApp(valid_images)
        app.run()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
