# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
"""Export the existing planet artwork as a multi-resolution Windows icon.

Requires Pillow only when regenerating the committed ICO. The Windows source is independent of the Linux PNG. Crop coordinates frame the planet rather than the surrounding stars;
a square crop and uniform resampling preserve the original proportions.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'assets/icons/windows/planet.png'
OUTPUT = ROOT / 'assets/icons/io.github.vertexiom.ClearView.ico'
SIZES = (16, 20, 24, 28, 32, 40, 48, 64, 96, 128, 256)


def main():
    with Image.open(SOURCE) as source:
        if source.size != (1254, 1254):
            raise SystemExit('Artwork dimensions changed; review the square crop first.')
        planet = source.convert('RGBA').crop((104, 104, 1150, 1150))
        # Resize each frame directly from the source, never from a smaller icon.
        frames = [planet.resize((size, size), Image.Resampling.LANCZOS) for size in SIZES]
        frames[-1].save(OUTPUT, format='ICO', sizes=[(s, s) for s in SIZES],
                       append_images=frames[:-1])
    print(OUTPUT)


if __name__ == '__main__':
    main()
