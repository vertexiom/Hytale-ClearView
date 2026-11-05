# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Pure demonstration state. No filesystem access or installer imports."""
from dataclasses import dataclass

NATIVE = '/home/player/.local/share/Hytale/install/release/package/game/latest/Client'
FLATPAK = '/home/player/.var/app/com.hypixel.HytaleLauncher/data/Hytale/install/release/package/game/latest/Client'
SCENARIOS = {
    'normal': 'Instalação com sucesso', 'update': 'Atualizar instalação',
    'missing': 'Hytale não encontrado', 'multiple': 'Duas instalações',
    'running': 'Hytale aberto', 'graphics': 'Falha gráfica',
    'conflict': 'Outro mod de shaders', 'copy': 'Falha ao instalar arquivos',
    'remove': 'Remover ClearView',
}

@dataclass
class Demo:
    scenario: str = 'normal'
    screen: str = 'welcome'
    path: str = NATIVE
    running: bool = False
    fixed: bool = False
    stage: int = 0
    operation: str = 'install'
    attempt: int = 0
    generation: int = 0

    def reset(self, scenario):
        if scenario not in SCENARIOS:
            raise ValueError('Unknown scenario')
        self.generation += 1
        self.scenario = scenario
        self.screen = 'remove' if scenario == 'remove' else 'welcome'
        self.path = '' if scenario in ('missing', 'multiple') else NATIVE
        self.running = scenario == 'running'
        self.fixed = False
        self.stage = self.attempt = 0
        self.operation = 'install'

    @property
    def ready(self):
        return bool(self.path) and not self.running

    def begin(self, operation):
        if operation not in ('install', 'remove') or not self.ready:
            raise ValueError('Destination required and game must be closed')
        self.generation += 1
        self.operation = operation
        self.stage = 0
        self.attempt += 1
        self.screen = 'progress'
        return self.generation

    def advance(self, generation):
        if generation != self.generation or self.screen != 'progress':
            return False
        failures = {'conflict': 0, 'graphics': 1, 'copy': 2}
        if self.operation == 'install' and not self.fixed and failures.get(self.scenario) == self.stage:
            self.screen = 'error'
        elif self.stage == 2:
            self.screen = 'removed' if self.operation == 'remove' else 'complete'
        else:
            self.stage += 1
        return True

    def recover(self):
        self.fixed = True
        self.running = False
        if self.scenario == 'missing':
            self.path = NATIVE
