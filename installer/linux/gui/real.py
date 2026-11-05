# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Real GTK workflow. Files are modified exclusively by the subprocess backend."""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from datetime import datetime
from app import Window, box, label, clear, Gtk, GLib, Gio

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'installer/linux'))
import install as backend

class RealWindow(Window):
    def reset(self):
        self.stop()
        self.close_dialog()
        self.targets = backend.discover()
        self.state.path = str(self.targets[0]) if len(self.targets) == 1 else ''
        self.state.screen = 'welcome'
        self.message = ''
        self.log_path = None
        self.result = None
        self.render()

    def __init__(self, app):
        super().__init__(app)
        self.set_title('ClearView · Instalador Linux')
        lab = self.scenarios.get_parent()
        self.scenarios.set_visible(False)
        lab.get_first_child().set_label('Linux · v0.1.3')
        self.scenarios.get_next_sibling().set_visible(False)
        self.lab_note.set_visible(False)

    def show(self, screen):
        if self.state.screen == 'progress':
            return
        if screen == 'closed':
            self.close()
            return
        self.state.screen = screen
        self.render()

    def render(self):
        clear(self.content)
        s = self.state
        cancel = ('Cancelar', self.close, None, True)
        if s.screen == 'welcome':
            self.heading('01 / 04 · BEM-VINDO', 'Seu mundo,\nmais à vista.',
                         'Ajuste a neblina do Hytale sem mudar a iluminação original do jogo.')
            self.heading_label.add_css_class('hero')
            self.content.append(label('Feche o jogo antes de continuar. O Hytale precisa estar instalado.'))
            self.card('Instalação real', 'O arquivo original do jogo fica guardado para você poder remover o mod. Seus ajustes existentes serão preservados.')
            self.content.append(self.button('Já usa o ClearView? Remover instalação', lambda: self.show('remove'), 'link'))
            self.foot([cancel, ('Continuar', lambda: self.show('location'), 'primary', True)])
        elif s.screen in ('location', 'remove'):
            removing = s.screen == 'remove'
            self.heading('REMOÇÃO' if removing else '02 / 04 · LOCAL DO JOGO',
                         'Remover o ClearView?' if removing else 'Onde está o Hytale?',
                         'Restaura a biblioteca original e mantém seus ajustes.' if removing else 'Confirme a pasta do jogo. Uma instalação existente do ClearView será atualizada.')
            if len(self.targets) > 1:
                for target in self.targets:
                    self.content.append(self.button(str(target), lambda p=target: self.select(p)))
            self.field()
            self.content.append(label('O backup e os arquivos serão verificados antes de qualquer alteração.', 'small muted'))
            self.foot([cancel, ('Remover' if removing else 'Instalar',
                lambda: self.begin('remove' if removing else 'install'),
                'warning' if removing else 'primary', bool(s.path))], lambda: self.show('welcome'))
        elif s.screen == 'progress':
            self.heading('03 / 04 · EM ANDAMENTO', 'Removendo…' if s.operation == 'remove' else 'Instalando…',
                         'Aguarde até a conclusão. Mantenha o Hytale fechado.')
            self.progress = Gtk.ProgressBar()
            self.progress.set_fraction(s.stage / 3)
            self.content.append(self.progress)
            self.status = label(self.message, 'success')
            self.content.append(self.status)
            self.content.append(label('O progresso acompanha as etapas reais de verificação e gravação.', 'small muted'))
            self.foot([])
        elif s.screen == 'error':
            self.heading('OPERAÇÃO INTERROMPIDA', 'Não foi possível concluir.', self.message, 'attention')
            self.content.append(label('Para ajuda, envie uma mensagem no Discord: tallmannzera. O relatório fica apenas nesta máquina.', 'small'))
            self.foot([('Ver relatório', self.report, None, bool(self.log_path)),
                       ('Voltar', lambda: self.show('remove' if s.operation == 'remove' else 'location'), 'primary', True)])
        else:
            removing = s.screen == 'removed'
            updated = self.result and self.result.get('operation') == 'update'
            self.heading('04 / 04 · CONCLUÍDO', 'ClearView removido.' if removing else 'ClearView atualizado!' if updated else 'Tudo pronto!',
                         'A biblioteca original foi restaurada.' if removing else 'Os arquivos foram instalados e verificados. Abra o Hytale pelo launcher normal.')
            if not removing:
                self.card('F9', 'Dentro do jogo, abra o painel para ajustar a neblina.', True)
            self.content.append(label('Seus ajustes de neblina foram preservados.' if removing or updated else 'Você pode remover o mod por este instalador.', 'small muted'))
            self.foot([('Ver relatório', self.report, None, bool(self.log_path)), ('Concluir', self.close, 'primary', True)])

    def select(self, path):
        self.state.path = str(path)
        self.render()

    def browse(self):
        chooser = Gtk.FileChooserNative.new('Selecione HytaleClient', self,
            Gtk.FileChooserAction.OPEN, 'Selecionar', 'Cancelar')
        filt = Gtk.FileFilter(); filt.set_name('HytaleClient'); filt.add_pattern('HytaleClient')
        chooser.add_filter(filt)
        def selected(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                if file and file.get_path(): self.select(Path(file.get_path()).parent)
            dialog.destroy()
            self.chooser = None
        chooser.connect('response', selected)
        self.chooser = chooser
        chooser.show()

    def begin(self, operation):
        if self.state.screen == 'progress' or not self.state.path:
            return
        self.state.operation = operation
        self.state.stage = 0
        self.state.screen = 'progress'
        self.message = 'Iniciando verificação…'
        self.result = None
        self.render()
        command = ['/usr/bin/python3', str(ROOT/'installer/linux/install.py'),
                   '--client-dir', self.state.path, '--json', '--payload', str(ROOT/'build/libSDL3.so')]
        if operation == 'remove': command.append('--uninstall')
        threading.Thread(target=self.worker, args=(command,), daemon=True).start()

    def worker(self, command):
        result = None
        error = None
        process = None
        try:
            logs = Path(os.environ.get('XDG_STATE_HOME', Path.home()/'.local/state'))/'clearview/logs'
            logs.mkdir(parents=True, exist_ok=True)
            self.log_path = logs/(datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.log')
            with self.log_path.open('x', encoding='utf-8') as log:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in process.stdout:
                    log.write(line); log.flush()
                    try: event = json.loads(line)
                    except ValueError: continue
                    if not isinstance(event, dict): continue
                    if event.get('event') == 'progress':
                        GLib.idle_add(self.on_progress, event)
                    elif event.get('event') == 'complete': result = event
                    elif event.get('event') == 'error': error = event.get('message')
                code = process.wait()
                log.write(f'Código de saída: {code}\n')
            if code != 0 or result is None:
                result = None
                error = error or 'O processo não confirmou a conclusão. Consulte o relatório antes de abrir o jogo.'
        except Exception as exc:
            # Do not unlock the UI while a worker might still be writing files.
            if process is not None:
                process.communicate()
            result = None
            error = f'Não foi possível concluir a operação: {exc}'
        GLib.idle_add(self.finished, result, error)

    def on_progress(self, event):
        self.state.stage = event['stage']
        self.message = event['message']
        self.render()
        return GLib.SOURCE_REMOVE

    def finished(self, result, error):
        self.result = result
        self.message = error or ''
        self.state.screen = ('removed' if self.state.operation == 'remove' else 'complete') if result else 'error'
        self.render()
        return GLib.SOURCE_REMOVE

    def report(self):
        dlg, body = self.modal('Relatório da instalação')
        text = self.log_path.read_text() if self.log_path and self.log_path.exists() else 'Nenhum relatório disponível.'
        view = Gtk.TextView(editable=False, monospace=True, wrap_mode=Gtk.WrapMode.WORD_CHAR)
        view.get_buffer().set_text(text)
        scroll = Gtk.ScrolledWindow(min_content_height=300, min_content_width=550)
        scroll.set_child(view); body.append(scroll)
        body.append(self.button('Fechar', self.close_dialog, 'primary'))
        dlg.present()
