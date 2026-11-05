#!/usr/bin/python3
# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""ClearView GTK4 installer. Use --demo for a simulation without game writes."""
import argparse
import sys
from pathlib import Path
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Gio, Pango
from model import Demo, SCENARIOS, NATIVE, FLATPAK
from rain import Rain

HERE = Path(__file__).resolve().parent

def box(vertical=True, spacing=16, css=None):
    b = Gtk.Box(orientation=Gtk.Orientation.VERTICAL if vertical else Gtk.Orientation.HORIZONTAL, spacing=spacing)
    if css:
        b.add_css_class(css)
    return b

def label(text, css=None):
    l = Gtk.Label(label=text, xalign=0, wrap=True)
    l.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    l.set_max_width_chars(65)
    if css:
        for c in css.split():
            l.add_css_class(c)
    return l

def clear(b):
    while b.get_first_child():
        b.remove(b.get_first_child())

class Window(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title='ClearView · Instalador Linux — demonstração')
        self.set_icon_name('io.github.vertexiom.ClearView')
        self.add_css_class('clearview')
        self.set_default_size(1000, 760)
        self.set_size_request(860, 600)
        self.state = Demo()
        self.timer = self.pulse_timer = 0
        self.dialog = None
        self.primary = None
        self.connect('close-request', self.request_close)
        # Let GTK/the window manager provide themed window decorations.
        root = box(spacing=0, css='clearview-ui')
        self.set_child(root)
        lab = box(False, 12, 'lab')
        badge=Gtk.Label(label='DEMO · V2'); badge.add_css_class('attention'); lab.append(badge)
        self.scenarios = Gtk.DropDown.new_from_strings(list(SCENARIOS.values()))
        self.scenarios.set_hexpand(True)
        self.scenarios.connect('notify::selected', lambda *_: self.reset())
        lab.append(self.scenarios)
        lab.append(self.button('Reiniciar', self.reset))
        self.rain = Rain()
        self.motion = self.button('Pausar chuva', self.toggle_rain)
        lab.append(self.motion)
        root.append(lab)
        self.lab_note = box(False, 14, 'lab-note')
        self.lab_text = label('Nada será instalado. Pastas e relatórios são fictícios.', 'small')
        self.lab_text.set_hexpand(True)
        self.lab_note.append(self.lab_text)
        self.recover = self.button('Simular condição resolvida', self.recover_condition)
        self.lab_note.append(self.recover)
        root.append(self.lab_note)
        body = box(False, 0)
        body.set_vexpand(True)
        body.append(self.rain)
        scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.content = box(spacing=18, css='content')
        scroll.set_child(self.content)
        body.append(scroll)
        root.append(body)
        self.footer = box(False, 12, 'footer')
        root.append(self.footer)
        keys = Gtk.EventControllerKey()
        keys.connect('key-pressed', self.key_pressed)
        self.add_controller(keys)
        self.rain.settings.connect('notify::gtk-enable-animations', lambda *_: self.update_motion())
        self.reset()
        self.update_motion()

    def button(self, text, callback, css=None, enabled=True):
        b = Gtk.Button(label=text, sensitive=enabled)
        if css:
            b.add_css_class(css)
        b.connect('clicked', lambda *_: callback())
        return b

    def update_motion(self):
        self.motion.set_label('Animar chuva' if self.rain.paused else 'Pausar chuva')

    def toggle_rain(self):
        self.rain.set_paused(not self.rain.paused)
        self.update_motion()

    def stop(self):
        for attr in ('timer', 'pulse_timer'):
            source = getattr(self, attr)
            if source:
                GLib.source_remove(source)
                setattr(self, attr, 0)
        self.state.generation += 1

    def reset(self):
        self.stop()
        self.close_dialog()
        self.state.reset(list(SCENARIOS)[self.scenarios.get_selected()])
        self.render()

    def show(self, screen):
        self.stop()
        self.state.screen = screen
        self.render()

    def recover_condition(self):
        self.state.recover()
        self.render()

    def heading(self, step, title, desc, tone=''):
        self.content.append(label(step, 'eyebrow '+tone))
        self.heading_label = label(title, 'title '+tone)
        self.content.append(self.heading_label)
        self.content.append(label(desc, 'muted'))

    def foot(self, actions, back=None):
        self.set_default_widget(None)
        clear(self.footer)
        self.primary = None
        if back:
            self.footer.append(self.button('Voltar', back))
        spacer = box()
        spacer.set_hexpand(True)
        self.footer.append(spacer)
        for text, callback, css, enabled in actions:
            b = self.button(text, callback, css, enabled)
            self.footer.append(b)
            if css in ('primary', 'warning') and enabled:
                self.primary = b
        self.set_default_widget(self.primary)

    def field(self):
        self.content.append(label('PASTA DO HYTALE', 'eyebrow'))
        row = box(False, 10)
        entry = Gtk.Entry(editable=False, hexpand=True, placeholder_text='Nenhuma pasta encontrada')
        entry.set_text(self.state.path)
        entry.set_tooltip_text(self.state.path or 'Destino fictício não selecionado')
        row.append(entry)
        row.append(self.button('Procurar…', self.browse, 'primary' if not self.state.path else None))
        self.content.append(row)
        self.content.append(label('Selecione o arquivo HytaleClient na pasta do jogo (sem .exe no Linux).', 'small muted'))

    def card(self, title, text, success=False):
        card = box(spacing=10, css='success-card' if success else 'card')
        card.append(label(title, 'key' if title == 'F9' else 'success' if success else 'attention'))
        card.append(label(text, 'small'))
        self.content.append(card)

    def render(self):
        clear(self.content)
        s = self.state
        self.recover.set_visible(s.scenario in ('missing','running','graphics','conflict','copy') and not s.fixed)
        self.recover.set_sensitive(s.screen != 'progress')
        self.lab_text.set_text('Simulação: nenhum arquivo do jogo será lido ou alterado.')
        cancel = ('Cancelar', lambda: self.show('closed'), None, True)
        if s.screen == 'welcome':
            self.heading('01 / 04 · BEM-VINDO','Seu mundo,\nmais à vista.', 'Ajuste a neblina do Hytale sem mudar a iluminação original do jogo.')
            self.heading_label.add_css_class('hero')
            self.content.append(label('Feche o jogo antes de continuar.\nO Hytale precisa estar instalado.'))
            spacer = box(); spacer.set_vexpand(True); self.content.append(spacer)
            self.content.append(self.button('Já usa o ClearView? Remover instalação', lambda: self.show('remove'), 'link'))
            self.foot([cancel, ('Continuar',lambda: self.show('location'),'primary',True)])
        elif s.screen in ('location','remove'):
            removing = s.screen == 'remove'
            self.heading('REMOÇÃO · 1 / 3' if removing else '02 / 04 · LOCAL DO JOGO',
                         'Remover o ClearView?' if removing else 'Encontramos duas instalações.' if s.scenario == 'multiple' else 'Onde está o Hytale?' if s.path else 'Vamos localizar o jogo.',
                         'Confirme de qual instalação deseja remover o mod.' if removing else 'O ClearView será instalado na pasta do seu jogo.',
                         'attention' if removing or not s.path else '')
            if s.scenario == 'multiple':
                self.content.append(label('Escolha uma instalação antes de continuar.', 'small'))
                first = None
                for title, path in [('Instalação nativa',NATIVE),('Launcher Flatpak',FLATPAK)]:
                    choice = Gtk.CheckButton(label=title)
                    if first: choice.set_group(first)
                    else: first = choice
                    choice.set_tooltip_text(path)
                    choice.set_active(s.path == path)
                    choice.connect('toggled', self.choose_install, path)
                    self.content.append(choice)
            self.field()
            if removing:
                self.card('Seus ajustes ficam guardados.', 'As configurações e logs em .clearview serão preservados. Feche o Hytale antes de continuar.', True)
            elif s.path:
                self.content.append(label('✓ Instalação encontrada (destino de demonstração).','success small'))
            else:
                self.content.append(label('Instale o jogo pelo launcher ou use Procurar… para selecionar um destino fictício.', 'muted small'))
            if s.running:
                self.card('O Hytale está aberto.', 'Feche o jogo antes de continuar.')
            if s.running or not s.path:
                self.content.append(self.button('Verificar novamente', self.render, 'link'))
            text = 'Remover' if removing else 'Atualizar' if s.scenario == 'update' else 'Instalar'
            self.foot([cancel, (text,lambda:self.begin('remove' if removing else 'install'),'warning' if removing else 'primary',s.ready)],lambda:self.show('welcome'))
        elif s.screen == 'progress':
            removing = s.operation == 'remove'
            self.heading('REMOÇÃO · 2 / 3' if removing else '03 / 04 · INSTALAÇÃO','Restaurando o jogo.' if removing else 'Preparando sua visão.','Aguarde a conclusão da operação simulada.')
            steps = ['Verificar instalação','Restaurar arquivos originais','Finalizar remoção'] if removing else ['Verificar arquivos','Testar compatibilidade gráfica','Instalar arquivos']
            for i, text in enumerate(steps):
                self.content.append(label(('✓' if i<s.stage else str(i+1))+'   '+text,'success' if i<s.stage else 'muted' if i>s.stage else ''))
            self.progress = Gtk.ProgressBar()
            self.progress.set_pulse_step(.06)
            self.progress.pulse()
            self.content.append(self.progress)
            self.content.append(label('Etapa simulada por temporizador. Nenhuma operação real está sendo executada.', 'small muted'))
            self.foot([])
            self.status = label('Aguarde a conclusão da operação.', 'small muted')
            self.footer.prepend(self.status)
        elif s.screen == 'error':
            errors={'graphics':('O teste gráfico não passou.','Não foi possível confirmar a compatibilidade nesta simulação.'),
                    'conflict':('Outro mod gráfico encontrado.','Remova o outro mod antes de instalar o ClearView.'),
                    'copy':('Os arquivos não foram instalados.','A etapa de cópia foi interrompida nesta simulação.')}
            title,desc=errors[s.scenario]
            self.heading('INSTALAÇÃO INTERROMPIDA',title,desc,'attention')
            self.card('Tente novamente antes de abrir o jogo.' if s.scenario=='copy' else 'O jogo não foi alterado nesta tentativa.',
                      'Use o controle do laboratório para simular a resolução da causa e tentar novamente.')
            row=box(False,12); row.append(self.button('Abrir relatório', self.report))
            support=label('Discord: tallmannzera','small'); support.set_hexpand(True); row.append(support); self.content.append(row)
            self.foot([('Fechar',lambda:self.show('closed'),None,True),('Tentar novamente',lambda:self.begin('install'),'primary',True)],lambda:self.show('location'))
        elif s.screen in ('complete','removed'):
            removed=s.screen=='removed'
            self.heading('REMOÇÃO · 3 / 3' if removed else '04 / 04 · CONCLUÍDO','Remoção concluída.' if removed else 'Tudo pronto!',
                         'Simulação concluída. Nenhum arquivo real foi alterado.','success')
            self.card('Seus ajustes ficam guardados.' if removed else 'F9', 'Você pode instalar o ClearView novamente quando quiser.' if removed else 'Abra o Hytale pelo launcher. Dentro do jogo, pressione F9 para ajustar a neblina.',True)
            self.foot([('Concluir',lambda:self.show('closed'),'primary',True)])
        else:
            self.heading('DEMONSTRAÇÃO ENCERRADA','Até a próxima.','Nenhum arquivo foi alterado. Reinicie para experimentar outro fluxo.')
            self.foot([('Reabrir',self.reset,'primary',True)])

    def choose_install(self, choice, path):
        if choice.get_active():
            self.state.path = path
            # Rebuild outside the toggled signal to avoid deleting its emitter.
            GLib.idle_add(self.refresh_choice)

    def refresh_choice(self):
        if self.state.screen in ('location','remove'):
            self.render()
        return GLib.SOURCE_REMOVE

    def begin(self, operation):
        self.stop()
        generation=self.state.begin(operation)
        self.render()
        self.pulse_timer=GLib.timeout_add(80,self.pulse)
        self.schedule(generation)

    def pulse(self):
        if self.state.screen != 'progress':
            self.pulse_timer=0
            return GLib.SOURCE_REMOVE
        if not self.rain.paused:
            self.progress.pulse()
        return GLib.SOURCE_CONTINUE

    def schedule(self,generation):
        def advance():
            self.timer=0
            if not self.state.advance(generation): return GLib.SOURCE_REMOVE
            self.render()
            if self.state.screen=='progress':self.schedule(generation)
            elif self.pulse_timer:
                GLib.source_remove(self.pulse_timer); self.pulse_timer=0
            return GLib.SOURCE_REMOVE
        self.timer=GLib.timeout_add([1600,2800,1800][self.state.stage],advance)

    def modal(self,title):
        self.close_dialog()
        self.previous_focus=self.get_focus()
        dlg=Gtk.Window(title=title,transient_for=self,modal=True,default_width=580)
        dlg.add_css_class('clearview')
        dlg.connect('close-request',lambda *_:(self.close_dialog(),True)[1])
        body=box(css='dialog-body');body.add_css_class('clearview-ui');dlg.set_child(body)
        self.dialog=dlg
        return dlg,body

    def close_dialog(self):
        if self.dialog:
            dlg=self.dialog;self.dialog=None;dlg.destroy()
            if self.previous_focus and self.previous_focus.get_root():self.previous_focus.grab_focus()

    def browse(self):
        dlg,body=self.modal('Selecionar HytaleClient · demonstração')
        body.append(label('Escolha um destino fictício','title'))
        body.append(label('Este diálogo não acessa pastas reais. No Linux o executável é HytaleClient, sem .exe.','muted'))
        selection=Gtk.DropDown.new_from_strings(['Instalação nativa','Launcher Flatpak'])
        body.append(selection)
        body.append(label('Arquivo: HytaleClient','success'))
        def select():
            self.state.path=[NATIVE,FLATPAK][selection.get_selected()]
            self.close_dialog();self.render()
        row=box(False,12);row.append(self.button('Cancelar',self.close_dialog));row.append(self.button('Selecionar',select,'primary'));body.append(row)
        dlg.present()

    def report(self):
        dlg,body=self.modal('Relatório de demonstração')
        body.append(label('RELATÓRIO FICTÍCIO','attention'))
        body.append(label(f'Cenário: {SCENARIOS[self.state.scenario]}\nTentativa: {self.state.attempt}\nEtapa: {self.state.stage+1} de 3\n\nNenhum teste gráfico foi executado. Nenhum arquivo foi lido, copiado ou restaurado. Este relatório não foi gravado nem enviado.'))
        body.append(self.button('Fechar',self.close_dialog,'primary'));dlg.present()

    def request_close(self,*_):
        if self.state.screen=='progress':
            self.status.set_text('Aguarde: a operação precisa terminar antes de fechar.')
            self.status.add_css_class('attention')
            return True
        self.stop();self.close_dialog();self.rain.set_paused(True)
        return False

    def key_pressed(self,controller,key,*_):
        if key==Gdk.KEY_Escape:
            if self.state.screen=='progress':self.request_close()
            else:self.show('closed')
            return True
        return False

class App(Gtk.Application):
    def __init__(self,args):
        super().__init__(application_id='io.github.vertexiom.ClearView.Demo' if getattr(args, 'demo', True) else 'io.github.vertexiom.ClearView',flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.args=args

    def do_activate(self):
        icons = HERE.parents[2] / 'assets/icons'
        if icons.is_dir():
            Gtk.IconTheme.get_for_display(Gdk.Display.get_default()).add_search_path(str(icons))
        css=Gtk.CssProvider();css.load_from_path(str(HERE/'style.css'))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        if getattr(self.args, 'demo', True):
            self.window=Window(self)
        else:
            from real import RealWindow
            self.window=RealWindow(self)
        if self.args.scenario:
            self.window.scenarios.set_selected(list(SCENARIOS).index(self.args.scenario))
        if self.args.screen:self.window.show(self.args.screen)
        self.window.present()
        if self.args.snapshot:GLib.timeout_add(1200,self.snapshot)

    def snapshot(self):
        try:
            window=self.window
            paintable=Gtk.WidgetPaintable.new(window)
            snapshot=Gtk.Snapshot()
            paintable.snapshot(snapshot,window.get_width(),window.get_height())
            node=snapshot.to_node()
            texture=window.get_renderer().render_texture(node,None)
            if not texture.save_to_png(self.args.snapshot):raise RuntimeError('PNG save failed')
            print('Snapshot:',self.args.snapshot,flush=True)
        finally:self.quit()
        return GLib.SOURCE_REMOVE

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='Simulate without changing game files')
    parser.add_argument('--snapshot',help='Save a GUI screenshot and exit (development only)')
    parser.add_argument('--scenario',choices=SCENARIOS)
    parser.add_argument('--screen',choices=['welcome','location','remove','error','complete','removed'])
    args=parser.parse_args()
    if (args.scenario or args.screen) and not args.demo:
        parser.error('--scenario and --screen require --demo')
    if args.screen=='error' and args.scenario not in ('graphics','conflict','copy'):
        parser.error('--screen error requires an error scenario')
    sys.exit(App(args).run([sys.argv[0]]))
