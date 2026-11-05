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
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Automation;
using System.Windows.Threading;
using System.Reflection;
using Microsoft.Win32;

namespace ClearView.Setup;
public partial class MainWindow : Window
{
    private readonly bool preview;
    private readonly InstallerService service = new();
    private string screen = "welcome", client = "", operation = "install", message = "";
    private bool busy;
    private TextBlock? status;
    private ProgressBar? progress;
    private Button? startButton;
    private TextBox? locationBox;
    public MainWindow(bool preview)
    {
        this.preview = preview; InitializeComponent();
        if (preview) PlatformLabel.Text += " · Prévia (não altera o jogo)";
        Closing += ClosingWindow;
        Closed += (_, _) => { Rain.Stop(); service.Dispose(); };
        StateChanged += (_, _) => Rain.Suspended = WindowState == WindowState.Minimized;
        Render();
    }
    private static Brush Color(string color) => (Brush)new BrushConverter().ConvertFromString(color)!;
    private TextBlock Text(string text, double size = 15, string color = "#E6EDF5") => new() { Text = text, FontSize = size, FontStyle = FontStyles.Normal, FontWeight = size >= 30 ? FontWeights.SemiBold : FontWeights.Normal, Foreground = Color(color), Margin = new Thickness(0, 0, 0, 18), TextWrapping = TextWrapping.Wrap };
    private Button Button(string title, Action action, bool primary = false)
    {
        var button = new Button { Content = title };
        if (primary) { button.Background = Color("#8DD2F4"); button.Foreground = Color("#092132"); button.IsDefault = true; }
        button.Click += (_, _) => action(); return button;
    }
    private void Card(string title, string body)
    {
        var panel = new StackPanel(); panel.Children.Add(Text(title, 24, "#85D8AF")); panel.Children.Add(Text(body));
        Body.Children.Add(new Border { Background = Color("#17352F"), CornerRadius = new CornerRadius(18), Padding = new Thickness(22), Margin = new Thickness(0, 12, 0, 20), Child = panel });
    }
    private void Navigate(string next) { if (busy) return; screen = next; Render(); }
    private void Render()
    {
        Body.Children.Clear(); Actions.Children.Clear(); status = null; progress = null; startButton = null; locationBox = null;
        Back.Visibility = screen is "location" or "remove" ? Visibility.Visible : Visibility.Collapsed;
        if (screen == "welcome")
        {
            Body.Children.Add(Text("01 / 04 · BEM-VINDO", 12, "#8DD2F4"));
            Body.Children.Add(Text("Seu mundo,\nmais à vista.", 40));
            Body.Children.Add(Text("Ajuste a neblina do Hytale sem mudar a iluminação original do jogo.", 16, "#A8B9CB"));
            Body.Children.Add(Text("Feche o jogo antes de continuar. O Hytale precisa estar instalado."));
            Card(preview ? "Prévia visual" : "Seus ajustes ficam guardados", preview ? "Você pode explorar as etapas sem alterar arquivos do jogo." : "O instalador mantém os arquivos necessários para remover o mod e preserva seus ajustes ao atualizar.");
            Body.Children.Add(Button("Já usa o ClearView? Remover instalação", () => Navigate("remove")));
            Actions.Children.Add(Button("Cancelar", Close)); Actions.Children.Add(Button("Continuar", () => Navigate("location"), true));
        }
        else if (screen is "location" or "remove")
        {
            bool remove = screen == "remove";
            Body.Children.Add(Text(remove ? "REMOÇÃO" : "02 / 04 · LOCAL DO JOGO", 12, "#8DD2F4"));
            Body.Children.Add(Text(remove ? "Remover o ClearView?" : "Onde está o Hytale?", 32));
            Body.Children.Add(Text(remove ? "Os arquivos originais serão restaurados. Seus ajustes ficam guardados." : "Confirme a pasta do jogo. Uma instalação existente será atualizada.", 15, "#A8B9CB"));
            var found = preview ? new[] { @"C:\Jogos\Hytale\Client (demonstração)" } : InstallerService.Discover();
            if (client.Length == 0 && found.Length == 1) client = found[0];
            foreach (var path in found.Length > 1 ? found : Array.Empty<string>())
            {
                var choice = new RadioButton { Content = path, IsChecked = path == client, Foreground = Color("#E6EDF5"), Margin = new Thickness(0, 5, 0, 8) };
                choice.Checked += (_, _) => { client = path; if (locationBox != null) locationBox.Text = client; if (startButton != null) startButton.IsEnabled = true; }; Body.Children.Add(choice);
            }
            Body.Children.Add(Text("PASTA DO HYTALE", 12, "#A8B9CB"));
            locationBox = new TextBox { Text = client, IsReadOnly = true, TextWrapping = TextWrapping.Wrap, Background = Color("#121D2A"), Foreground = Color("#E6EDF5"), Padding = new Thickness(12), Margin = new Thickness(0, 0, 0, 12) };
            AutomationProperties.SetName(locationBox, "Pasta do Hytale");
            Body.Children.Add(locationBox);
            Body.Children.Add(Button("Procurar…", Browse));
            Body.Children.Add(Text("Selecione HytaleClient.exe na pasta do jogo.", 13, "#A8B9CB"));
            Actions.Children.Add(Button("Cancelar", Close));
            startButton = Button(remove ? "Remover" : "Instalar", () => Begin(remove ? "remove" : "install"), true); startButton.IsEnabled = client.Length > 0; Actions.Children.Add(startButton);
        }
        else if (screen == "progress")
        {
            Body.Children.Add(Text("03 / 04 · EM ANDAMENTO", 12, "#8DD2F4")); Body.Children.Add(Text(operation == "remove" ? "Removendo…" : "Instalando…", 32));
            Body.Children.Add(Text("Mantenha o Hytale fechado e aguarde a conclusão.", 15, "#A8B9CB"));
            progress = new ProgressBar { Maximum = 3, Height = 8, Margin = new Thickness(0, 20, 0, 24), Foreground = Color("#8DD2F4"), Background = Color("#2B3D4F") }; Body.Children.Add(progress);
            status = Text("Preparando a operação…");
            AutomationProperties.SetLiveSetting(status, AutomationLiveSetting.Polite);
            AutomationProperties.SetName(progress, "Etapas da instalação");
            Body.Children.Add(status);
        }
        else if (screen == "error")
        {
            Body.Children.Add(Text("OPERAÇÃO INTERROMPIDA", 12, "#F0C782")); Body.Children.Add(Text("Não foi possível concluir.", 32)); Body.Children.Add(Text(message));
            Body.Children.Add(Text("Para ajuda, envie uma mensagem no Discord: tallmannzera. O relatório fica apenas nesta máquina.", 14, "#A8B9CB"));
            AddReport(); Actions.Children.Add(Button("Voltar", () => Navigate(operation == "remove" ? "remove" : "location"), true));
        }
        else
        {
            Body.Children.Add(Text("04 / 04 · CONCLUÍDO", 12, "#8DD2F4")); Body.Children.Add(Text(preview ? "Prévia concluída." : operation == "remove" ? "ClearView removido." : "Tudo pronto!", 32));
            if (preview) Card("Nenhum arquivo foi alterado", "Esta execução demonstrou somente as etapas da interface.");
            else if (operation == "install") Card("F9", "Abra o Hytale pelo launcher normal. Dentro do jogo, F9 abre o painel de neblina.");
            else Body.Children.Add(Text("Os arquivos originais foram restaurados. Seus ajustes foram preservados."));
            AddReport(); Actions.Children.Add(Button("Concluir", Close, true));
        }
        Dispatcher.BeginInvoke(DispatcherPriority.Loaded, new Action(() =>
        {
            var target = Actions.Children.OfType<Button>().FirstOrDefault(b => b.IsDefault && b.IsEnabled)
                ?? Actions.Children.OfType<Button>().FirstOrDefault(b => b.IsEnabled);
            target?.Focus();
        }));
    }
    private void ShowLicense(object sender, RoutedEventArgs e)
    {
        using var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("ClearView.License.txt");
        if (stream == null) { MessageBox.Show(this, "Licença indisponível.", "ClearView"); return; }
        using var reader = new StreamReader(stream);
        var body = new DockPanel { Margin = new Thickness(24) };
        var dialog = new Window { Owner = this, Title = "ClearView · GPL-3.0-or-later", Width = 720, Height = 600,
            MinWidth = 480, MinHeight = 360, WindowStartupLocation = WindowStartupLocation.CenterOwner,
            Background = Background, Foreground = Foreground, Content = body };
        var close = Button("Fechar", dialog.Close, true); close.IsCancel = true;
        DockPanel.SetDock(close, Dock.Bottom); body.Children.Add(close);
        var heading = Text("Copyright (C) 2026 vertexiom\nGNU GPL v3.0 ou posterior · Sem garantia", 18);
        DockPanel.SetDock(heading, Dock.Top); body.Children.Add(heading);
        using var thirdPartyStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("ClearView.ThirdParty.txt");
        using var thirdParty = thirdPartyStream == null ? null : new StreamReader(thirdPartyStream);
        var license = new TextBox { Text = reader.ReadToEnd() + "\n\nTHIRD-PARTY NOTICES\n\n" + thirdParty?.ReadToEnd(), IsReadOnly = true, TextWrapping = TextWrapping.Wrap,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto, Background = Background, Foreground = Foreground,
            BorderThickness = new Thickness(0), Padding = new Thickness(8), Margin = new Thickness(0, 12, 0, 16) };
        AutomationProperties.SetName(license, "Texto completo da licença GPL");
        body.Children.Add(license); dialog.Loaded += (_, _) => close.Focus(); dialog.ShowDialog();
    }
    private void Browse()
    {
        if (preview) { client = @"C:\Jogos\Hytale\Client (demonstração)"; Render(); return; }
        var picker = new OpenFileDialog { Title = "Selecione HytaleClient.exe", Filter = "Hytale|HytaleClient.exe", CheckFileExists = true };
        if (picker.ShowDialog(this) == true) { client = Path.GetDirectoryName(picker.FileName)!; Render(); }
    }
    private async void Begin(string selected)
    {
        if (busy) return;
        operation = selected; busy = true; screen = "progress"; Render();
        try
        {
            var updates = new Progress<(int Step, string Message)>(value => { if (progress != null) progress.Value = value.Step; if (status != null) status.Text = value.Message; });
            if (preview)
            {
                for (int i = 0; i < 3; i++) { progress!.Value = i; status!.Text = "Demonstração das etapas — nenhum arquivo será alterado."; await Task.Delay(900); }
            }
            else await service.RunAsync(client, operation, updates);
            screen = "complete";
        }
        catch (Exception ex) { message = ex.Message; screen = "error"; }
        finally { busy = false; Render(); }
    }
    private void AddReport() { if (service.LogFile != null) Actions.Children.Add(Button("Ver relatório", ShowReport)); }
    private void ShowReport()
    {
        try { var p = new ProcessStartInfo(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "System32", "notepad.exe")) { UseShellExecute = false }; p.ArgumentList.Add(service.LogFile!); Process.Start(p); }
        catch (Exception ex) { MessageBox.Show(this, "Não foi possível abrir o relatório: " + ex.Message, "ClearView"); }
    }
    private void ToggleRain(object sender, RoutedEventArgs e) { Rain.Paused = !Rain.Paused; Motion.Content = Rain.Paused ? "Animar chuva" : "Pausar chuva"; }
    private void GoBack(object sender, RoutedEventArgs e) => Navigate("welcome");
    private void ClosingWindow(object? sender, CancelEventArgs e)
    {
        if (busy) { e.Cancel = true; if (status != null) status.Text = "Aguarde a operação terminar antes de fechar."; }
    }
}
