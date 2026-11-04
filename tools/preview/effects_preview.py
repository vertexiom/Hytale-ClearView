#!/usr/bin/env python3
"""Interactive TerminalTextEffects 0.15.0 comparison."""
import json
import shutil
import subprocess
import sys
from ascii_planet import ROOT, CONFIG, OUT, render, terminal_cell_ratio, square_grid


def main():
    engine = ROOT / 'build/ascii-preview/tte-venv/bin/tte'
    if not engine.exists():
        raise SystemExit('Ambiente TTE local nao encontrado.')
    choices = {
        '1': ('decrypt', 'Simbolos se resolvem no planeta', ['--typing-speed', '150'], 'always'),
        '2': ('wipe', 'Revelacao diagonal', [], 'always'),
        '3': ('scattered', 'Caracteres dispersos se juntam', ['--movement-speed', '1.2'], 'always'),
        '4': ('highlight', 'Brilho atravessa o planeta pronto', ['--highlight-width', '12'], 'dynamic'),
        '5': ('expand', 'Expansao a partir do centro', ['--movement-speed', '0.8'], 'always'),
    }
    selected = '1'
    print('CLEARVIEW | Animacoes | TerminalTextEffects 0.15.0')
    print('Maximize a janela antes de iniciar. As cores originais serao preservadas.')
    while True:
        print('\n' + ' | '.join(f'{key}: {value[0].title()}' for key,value in choices.items()))
        answer = input(f'Numero + Enter; Enter repete {choices[selected][0]}; Q sai: ').strip().lower()
        if answer == 'q':
            return
        if answer:
            if answer not in choices:
                continue
            selected = answer
        effect, description, options, color_mode = choices[selected]
        settings = json.loads(CONFIG.read_text())
        size = shutil.get_terminal_size()
        ratio = terminal_cell_ratio(settings['cell_ratio'])
        width, height = square_grid(size, settings['columns'], ratio, footer=8)
        _, ansi = render(width, height, settings)
        source = OUT/'effects-input.ansi'
        source.write_text(ansi+'\n')
        sys.stdout.write('\033[2J\033[H'); sys.stdout.flush()
        try:
            result = subprocess.run([str(engine), '--input-file', str(source),
                '--existing-color-handling', color_mode, '--frame-rate', '30',
                '--anchor-canvas', 'c', '--anchor-text', 'c',
                effect, *options])
            if result.returncode:
                print(f'{effect} terminou com codigo {result.returncode}.')
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout.write('\033[0m\033[?25h'); sys.stdout.flush()

if __name__ == '__main__':
    main()
