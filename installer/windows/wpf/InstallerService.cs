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
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text;

namespace ClearView.Setup;
public sealed class InstallerService : IDisposable
{
    private string? folder;
    private Process? worker;
    public string? LogFile { get; private set; }
    public static string[] Discover() => new[] { Environment.SpecialFolder.ApplicationData, Environment.SpecialFolder.LocalApplicationData }
        .Select(p => Path.Combine(Environment.GetFolderPath(p), @"Hytale\install\release\package\game\latest\Client"))
        .Where(p => File.Exists(Path.Combine(p, "HytaleClient.exe"))).Distinct(StringComparer.OrdinalIgnoreCase).ToArray();

    public async Task RunAsync(string client, string operation, IProgress<(int Step, string Message)> progress)
    {
        if (operation is not ("install" or "remove")) throw new ArgumentException("Operação inválida.");
        if (worker != null) throw new InvalidOperationException("Uma operação já está em andamento.");
        if (!Environment.Is64BitOperatingSystem || !OperatingSystem.IsWindowsVersionAtLeast(10, 0, 17763))
            throw new InvalidOperationException("Requer Windows 10 1809 ou superior, de 64 bits.");
        if (!File.Exists(Path.Combine(client, "HytaleClient.exe"))) throw new InvalidOperationException("Selecione a pasta que contém HytaleClient.exe.");
        var games = Process.GetProcessesByName("HytaleClient");
        bool running = games.Length != 0; foreach (var game in games) game.Dispose();
        if (running) throw new InvalidOperationException("Feche o Hytale antes de continuar.");
        string logs = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "ClearView", "Logs");
        Directory.CreateDirectory(logs);
        LogFile = Path.Combine(logs, "wpf-" + Guid.NewGuid().ToString("N") + ".txt");
        await File.WriteAllTextAsync(LogFile, "ClearView WPF · " + operation + Environment.NewLine);
        try
        {
            await Task.Run(ExtractPayload);
            string engine = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), @"System32\WindowsPowerShell\v1.0\powershell.exe");
            var start = new ProcessStartInfo(engine) { UseShellExecute = false, CreateNoWindow = true, WorkingDirectory = folder!, RedirectStandardOutput = true, RedirectStandardError = true };
            foreach (string arg in new[] { "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", Path.Combine(folder!, "wpf-runner.ps1"), "-Engine", engine, "-Payload", folder!, "-Client", client, "-Log", LogFile, "-Operation", operation }) start.ArgumentList.Add(arg);
            worker = new Process { StartInfo = start };
            if (!worker.Start()) throw new InvalidOperationException("Não foi possível iniciar a operação.");
            var stdout = worker.StandardOutput.ReadToEndAsync();
            var stderr = worker.StandardError.ReadToEndAsync();
            Task finished = worker.WaitForExitAsync();
            while (!finished.IsCompleted)
            {
                string stage = ReadStage();
                string text = operation == "remove" ? "Restaurando arquivos originais…" : stage switch {
                    "1" => "Verificando o Hytale e os arquivos do mod…",
                    "2" => "Testando a compatibilidade gráfica (até 60 segundos)…",
                    "3" => "Instalando e verificando os arquivos…",
                    _ => "Preparando a operação…" };
                progress.Report((int.TryParse(stage, out int step) ? Math.Clamp(step-1, 0, 2) : 0, text));
                await Task.WhenAny(finished, Task.Delay(150));
            }
            await finished;
            string output = await stdout, errors = await stderr;
            await File.AppendAllTextAsync(LogFile, output + errors + $"\nProcesso encerrado com código: {worker.ExitCode}\n");
            if (worker.ExitCode != 0 || ReadStage() != "complete")
                throw new InvalidOperationException("A operação não foi concluída. Consulte o relatório; não houve confirmação de sucesso.");
            progress.Report((3, "Concluído."));
        }
        catch (Exception ex)
        {
            // Keep the window busy until any started worker has stopped writing.
            if (worker != null) { try { await worker.WaitForExitAsync(); } catch (InvalidOperationException) { } }
            try { await File.AppendAllTextAsync(LogFile, "\nErro: " + ex.Message + "\n"); } catch (IOException) { }
            throw;
        }
        finally { worker?.Dispose(); worker = null; Cleanup(); }
    }
    private string ReadStage()
    {
        try { return File.ReadAllText(LogFile + ".stage").Trim(); }
        catch (IOException) { return ""; }
    }
    private void ExtractPayload()
    {
        Cleanup(); folder = Path.Combine(Path.GetTempPath(), "ClearView-WPF-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(folder);
        using Stream input = Assembly.GetExecutingAssembly().GetManifestResourceStream("ClearView.Payload.zip") ?? throw new InvalidDataException("Pacote ausente.");
        using var archive = new ZipArchive(input);
        var expected = new HashSet<string>(StringComparer.Ordinal) { "manifest.json", "install.ps1", "smoke-test.ps1", "workflow.ps1", "wpf-runner.ps1", "bin/opengl32.dll", "bin/clearview-smoke.exe" };
        foreach (var entry in archive.Entries)
        {
            if (!expected.Remove(entry.FullName)) throw new InvalidDataException("Arquivo inesperado no pacote.");
            string target = Path.Combine(folder, entry.FullName.Replace('/', Path.DirectorySeparatorChar));
            Directory.CreateDirectory(Path.GetDirectoryName(target)!); entry.ExtractToFile(target);
        }
        if (expected.Count != 0) throw new InvalidDataException("Pacote incompleto.");
        using var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(folder, "manifest.json")));
        foreach (var name in new[] { "opengl32.dll", "clearview-smoke.exe" })
        {
            string hash = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(folder, "bin", name))));
            string? expectedHash = manifest.RootElement.GetProperty("files").GetProperty(name).GetString();
            if (!string.Equals(hash, expectedHash, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Verificação de integridade falhou: " + name);
        }
    }
    private void Cleanup()
    {
        if (folder == null) return;
        try { Directory.Delete(folder, true); folder = null; } catch (IOException) { } catch (UnauthorizedAccessException) { }
    }
    public void Dispose() { if (worker == null) Cleanup(); }
}
