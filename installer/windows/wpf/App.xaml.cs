/*
 * Copyright (C) 2026 vertexiom
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * This file is part of Hytale ClearView.
 * Hytale ClearView is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version. See LICENSE for details.
 */
using System.Threading;
using System.Windows;
using System.Windows.Threading;

namespace ClearView.Setup;
public partial class App : Application
{
    private Mutex? instance;
    private EventWaitHandle? activate;
    private DispatcherTimer? activationTimer;
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        instance = new Mutex(false, @"Local\HytaleClearViewInstaller", out bool first);
        if (!first)
        {
            try { using var signal = EventWaitHandle.OpenExisting(@"Local\HytaleClearViewInstallerActivate"); signal.Set(); }
            catch (WaitHandleCannotBeOpenedException) { MessageBox.Show("O instalador já está aberto. Volte para a janela existente.", "ClearView"); }
            Shutdown(); return;
        }
        activate = new EventWaitHandle(false, EventResetMode.AutoReset, @"Local\HytaleClearViewInstallerActivate");
        var window = new MainWindow(e.Args.Contains("--preview"));
        MainWindow = window;
        activationTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(200) };
        activationTimer.Tick += (_, _) => { if (activate.WaitOne(0)) { window.Show(); if (window.WindowState == WindowState.Minimized) window.WindowState = WindowState.Normal; window.Activate(); } };
        activationTimer.Start(); window.Show();
    }
    protected override void OnExit(ExitEventArgs e)
    {
        activationTimer?.Stop(); activate?.Dispose(); instance?.Dispose(); base.OnExit(e);
    }
}
