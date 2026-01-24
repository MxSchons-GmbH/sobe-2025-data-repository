#!/usr/bin/env python3
"""
Generate WebP and AVIF versions for hand-drawn figures.

Hand-drawn figures are created externally (not by matplotlib), so they need
separate processing to generate web-optimized formats from their PNG files.

Usage:
    python generate_hand_drawn_web_formats.py
    python generate_hand_drawn_web_formats.py --dry-run
"""

import argparse
import logging
from pathlib import Path

from PIL import Image

import paths

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def generate_web_formats(png_path: Path, dry_run: bool = False) -> tuple[bool, bool]:
    """
    Generate WebP and AVIF versions from a PNG file.

    Parameters
    ----------
    png_path : Path
        Path to the source PNG file
    dry_run : bool
        If True, only report what would be done

    Returns
    -------
    tuple[bool, bool]
        (webp_created, avif_created) - whether each format was created
    """
    webp_path = png_path.with_suffix('.webp')
    avif_path = png_path.with_suffix('.avif')

    webp_created = False
    avif_created = False

    if dry_run:
        if not webp_path.exists():
            logger.info(f"  Would create: {webp_path.name}")
            webp_created = True
        if not avif_path.exists():
            logger.info(f"  Would create: {avif_path.name}")
            avif_created = True
        return webp_created, avif_created

    try:
        with Image.open(png_path) as img:
            # Convert to RGB if necessary (AVIF/WebP don't always handle RGBA well)
            if img.mode == 'RGBA':
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img_rgb = background
            else:
                img_rgb = img.convert('RGB') if img.mode != 'RGB' else img

            # Generate WebP if it doesn't exist
            if not webp_path.exists():
                img_rgb.save(
                    webp_path,
                    'WEBP',
                    quality=90,
                    method=6  # Slower but better compression
                )
                logger.info(f"  Created: {webp_path.name}")
                webp_created = True

            # Generate AVIF if it doesn't exist
            if not avif_path.exists():
                img_rgb.save(
                    avif_path,
                    'AVIF',
                    quality=85,
                    speed=4  # Balance between speed and compression
                )
                logger.info(f"  Created: {avif_path.name}")
                avif_created = True

    except Exception as e:
        logger.error(f"  Error processing {png_path.name}: {e}")

    return webp_created, avif_created


def main():
    parser = argparse.ArgumentParser(
        description='Generate WebP and AVIF versions for hand-drawn figures'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate even if files already exist'
    )
    args = parser.parse_args()

    hand_drawn_dir = paths.OUTPUT_FIGURES_HAND_DRAWN

    if not hand_drawn_dir.exists():
        logger.error(f"Hand-drawn figures directory not found: {hand_drawn_dir}")
        return 1

    # Find all PNG files
    png_files = sorted(hand_drawn_dir.glob('*.png'))

    if not png_files:
        logger.info("No PNG files found in hand-drawn directory")
        return 0

    logger.info(f"Processing {len(png_files)} hand-drawn figures...")
    logger.info(f"Directory: {hand_drawn_dir}")
    logger.info("")

    total_webp = 0
    total_avif = 0

    for png_path in png_files:
        logger.info(f"Processing: {png_path.name}")

        # If force, remove existing files first
        if args.force and not args.dry_run:
            webp_path = png_path.with_suffix('.webp')
            avif_path = png_path.with_suffix('.avif')
            if webp_path.exists():
                webp_path.unlink()
            if avif_path.exists():
                avif_path.unlink()

        webp_created, avif_created = generate_web_formats(png_path, args.dry_run)
        total_webp += webp_created
        total_avif += avif_created

    logger.info("")
    if args.dry_run:
        logger.info(f"Dry run complete. Would create {total_webp} WebP and {total_avif} AVIF files.")
    else:
        logger.info(f"Done. Created {total_webp} WebP and {total_avif} AVIF files.")

    return 0


if __name__ == '__main__':
    exit(main())
