#!/usr/bin/env python3
"""
compress_photos.py

Batch-resizes and recompresses JPEGs for the photo portfolio, since the
Gallery theme only ever displays images at a max of 1600px anyway — there's
no visual benefit to shipping full 20MB camera-resolution originals into
the git repo.

Usage:
    python compress_photos.py <input_folder> [options]

Examples:
    # Preview what would happen, no files touched
    python compress_photos.py content/wildlife --dry-run

    # Resize in place (overwrites originals) — do this only after a dry run
    python compress_photos.py content/wildlife

    # Write to a separate output folder instead of overwriting
    python compress_photos.py content/wildlife --output compressed/wildlife

    # Custom size/quality
    python compress_photos.py content/wildlife --max-dimension 3000 --quality 80

    # Also strip GPS EXIF data (recommended if shooting specific real-world
    # locations you don't want geotagged, e.g. nature park spots)
    python compress_photos.py content/wildlife --strip-gps
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Pillow is required. Install it with: pip install pillow")
    sys.exit(1)

IMAGE_EXTENSIONS = {".jpg", ".jpeg"}

# EXIF GPS IFD tag id (0x8825) — used to strip GPS block specifically
GPS_TAG_ID = 0x8825


def find_images(folder: Path, recursive: bool):
    pattern = "**/*" if recursive else "*"
    for path in folder.glob(pattern):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def compress_image(
    src: Path,
    dst: Path,
    max_dimension: int,
    quality: int,
    strip_gps: bool,
):
    with Image.open(src) as img:
        # Respect EXIF orientation before resizing, then drop the tag so
        # viewers don't double-rotate
        img = ImageOps.exif_transpose(img)

        exif = img.getexif()
        if strip_gps and GPS_TAG_ID in exif:
            del exif[GPS_TAG_ID]

        width, height = img.size
        longest_edge = max(width, height)

        if longest_edge > max_dimension:
            scale = max_dimension / longest_edge
            new_size = (round(width * scale), round(height * scale))
            img = img.resize(new_size, Image.LANCZOS)

        dst.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs = {
            "format": "JPEG",
            "quality": quality,
            "optimize": True,
        }
        if exif:
            save_kwargs["exif"] = exif

        img.save(dst, **save_kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Folder containing photos to compress")
    parser.add_argument("--output", type=Path, default=None, help="Output folder (default: overwrite in place)")
    parser.add_argument("--max-dimension", type=int, default=3500, help="Max long-edge size in px (default: 3500)")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality 1-100 (default: 85)")
    parser.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    parser.add_argument("--strip-gps", action="store_true", help="Remove GPS EXIF data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing files")
    args = parser.parse_args()

    if not args.input.is_dir():
        print(f"Error: {args.input} is not a folder")
        sys.exit(1)

    in_place = args.output is None
    images = sorted(find_images(args.input, args.recursive))

    if not images:
        print(f"No .jpg/.jpeg files found in {args.input}")
        return

    total_before = 0
    total_after = 0

    for src in images:
        rel = src.relative_to(args.input)
        dst = src if in_place else args.output / rel

        size_before = src.stat().st_size
        total_before += size_before

        if args.dry_run:
            with Image.open(src) as img:
                w, h = img.size
            print(f"[dry-run] {rel}  {w}x{h}  {size_before / 1_048_576:.1f}MB -> would resize/recompress")
            continue

        # Write to a temp path first when overwriting in place, so a crash
        # mid-write never corrupts the source file
        tmp_dst = dst.with_suffix(dst.suffix + ".tmp") if in_place else dst
        compress_image(src, tmp_dst, args.max_dimension, args.quality, args.strip_gps)

        if in_place:
            tmp_dst.replace(dst)

        size_after = dst.stat().st_size
        total_after += size_after

        pct = 100 * (1 - size_after / size_before)
        print(f"{rel}  {size_before / 1_048_576:.1f}MB -> {size_after / 1_048_576:.1f}MB  (-{pct:.0f}%)")

    if not args.dry_run and total_before:
        pct_total = 100 * (1 - total_after / total_before)
        print(f"\nTotal: {total_before / 1_048_576:.1f}MB -> {total_after / 1_048_576:.1f}MB  (-{pct_total:.0f}%)")
    elif args.dry_run:
        print(f"\n[dry-run] {len(images)} file(s) found, {total_before / 1_048_576:.1f}MB total. No files modified.")


if __name__ == "__main__":
    main()
