# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
"""Embed the licensed Inter faces so the HUD does not depend on installed fonts."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
def generate(destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('w') as out:
        out.write('/* Generated from assets/fonts; see assets/fonts/LICENSES.txt. */\n')
        for name, file in [('regular', 'Inter-Regular.otf'), ('semibold', 'Inter-SemiBold.otf')]:
            data = (ROOT / 'assets/fonts' / file).read_bytes()
            out.write(f'static const unsigned char cv_font_{name}[]={{\n')
            for offset in range(0, len(data), 24):
                out.write(','.join(str(x) for x in data[offset:offset+24])+',\n')
            out.write('};\n')
if __name__ == '__main__':
    generate(sys.argv[1])
