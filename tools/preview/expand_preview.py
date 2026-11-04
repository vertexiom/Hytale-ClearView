#!/usr/bin/env python3
"""Isolated TerminalTextEffects 0.15.0 Expand demo."""
import json
import shutil
import subprocess
import sys
from ascii_planet import ROOT, CONFIG, OUT, render, terminal_cell_ratio, square_grid


def main():
    engine = ROOT / 'build/ascii-preview/tte-venv/bin/tte'
    if not engine.exists():
        raise SystemExit('Ambiente TTE local nao encontrado.')
    print('CLEARVIEW | Expand | TerminalTextEffects 0.15.0')
    print('Maximize a janela antes de iniciar. As cores originais serao preservadas.')
    while True:
        if input('\nEnter para animar; Q + Enter para sair: ').strip().lower() == 'q':
            return
        settings = json.loads(CONFIG.read_text())
        size = shutil.get_terminal_size()
        ratio = terminal_cell_ratio(settings['cell_ratio'])
        width, height = square_grid(size, settings['columns'], ratio, footer=6)
        _, ansi = render(width, height, settings)
        source = OUT/'expand-input.ansi'
        source.write_text(ansi+'\n')
        sys.stdout.write('\033[2J\033[H'); sys.stdout.flush()
        try:
            result = subprocess.run([str(engine), '--input-file', str(source),
                '--existing-color-handling', 'always', '--frame-rate', '30',
                '--anchor-canvas', 'c', '--anchor-text', 'c',
                'expand', '--movement-speed', '0.8'])
            if result.returncode:
                print(f'Expand terminou com codigo {result.returncode}.')
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout.write('\033[0m\033[?25h'); sys.stdout.flush()

if __name__ == '__main__':
    main()
