#!/usr/bin/env python3
"""
Generate PWA icons in various sizes
This creates simple SVG-based placeholder icons
For production, replace with your actual app icons
"""

from pathlib import Path

# Icon sizes needed for PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# SVG template with dynamic size
SVG_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2196F3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1976D2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="{size}" height="{size}" fill="url(#grad)" rx="{radius}"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="{font_size}"
        font-weight="bold" fill="white" text-anchor="middle" dy=".35em">M</text>
</svg>
"""


def generate_icon(size: int, output_path: Path):
    """Generate a single icon of the specified size"""
    # Calculate proportional radius and font size
    radius = size * 0.15
    font_size = size * 0.6

    svg_content = SVG_TEMPLATE.format(size=size, radius=radius, font_size=int(font_size))

    output_file = output_path / f"icon-{size}x{size}.png.svg"
    with open(output_file, "w") as f:
        f.write(svg_content)

    print(f"Generated: {output_file}")


def main():
    """Generate all icon sizes"""
    # Get the icons directory
    icons_dir = Path(__file__).parent / "static" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    print("Generating PWA icons...")
    print(f"Output directory: {icons_dir}")
    print("-" * 50)

    for size in ICON_SIZES:
        generate_icon(size, icons_dir)

    print("-" * 50)
    print(f"✓ Generated {len(ICON_SIZES)} icon files")
    print("\nNote: These are SVG placeholder icons.")
    print("For production, convert these to PNG or replace with actual app icons.")
    print("\nTo convert SVG to PNG (requires ImageMagick or similar):")
    for size in ICON_SIZES:
        print(f"  convert icon-{size}x{size}.png.svg -resize {size}x{size} icon-{size}x{size}.png")


if __name__ == "__main__":
    main()
