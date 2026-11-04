<h1 align="center">Hytale ClearView</h1>

<p align="center">
  <a href="README.md">English</a> | <a href="README.pt-BR.md">Português (Brasil)</a>
</p>

**Hytale ClearView is in early development — v0.1.0.** Testing and compatibility validation are ongoing, and Hytale updates may require changes to the mod.

[Aurora Shaders](https://github.com/Kristijan1001/Hytale-Aurora-Shaders) was used as a reference to understand how shaders work and develop ClearView, which has its own independent code.

The goal is to control Hytale's fog while keeping the game's original lighting. Open the panel with **F9** and adjust visibility to your liking.

## Download

**[Download ClearView v0.1.0](https://github.com/vertexiom/Hytale-ClearView/releases/tag/v0.1.0)**

- **Windows:** download `ClearView-0.1.0-Setup.exe`.
- **Linux:** download `ClearView-0.1.0-linux-source.tar.gz` and follow the instructions below.

## What you can adjust

- **Distance:** fog that obscures the horizon and distant terrain.
- **Atmosphere:** fog related to weather, height, and the environment.
- **Depth:** fog related to distance within the environment, including water.

Each control ranges from **0%** (removes that effect) to **100%** (original intensity). Settings are saved automatically. The mod does not increase render distance or guarantee higher FPS.

## Compatibility

- Windows 10 x64 version 1809 or later, and Windows 11.
- Linux x86_64, including the Flatpak launcher.
- A working Hytale installation and a graphics driver supporting OpenGL 4.1.

ClearView does not replace [Hytale's system requirements](https://hytale.com/news/2025/12/hytale-hardware-requirements). Compatibility across computers and multiplayer is still being evaluated.

## Install on Windows

The installer currently uses Portuguese labels. The instructions below include the exact button names.

1. Download and open **ClearView-0.1.0-Setup.exe**.
2. Close Hytale. The installer finds the game folder automatically; if needed, click **Localizar** (Browse) and select `HytaleClient.exe`.
3. Click **Instalar / Atualizar** (Install / Update) and wait for confirmation.
4. Open the game through its launcher, enter a world, and press **F9**.

Checks run automatically. You do not need to extract files, use a terminal, install Python, or run scripts. To uninstall, open the same installer and click **Remover** (Remove). Updating preserves existing settings.

## Install on Linux

Extract the package. Installation builds the mod and requires Python 3, a C compiler, pkg-config, and Cairo. On Ubuntu, install the dependencies:

```bash
sudo apt install python3 build-essential pkg-config libcairo2-dev
```

With Hytale closed, open a terminal in the extracted folder:

```bash
bash install.sh
```

Then open the game through its usual launcher. To uninstall, close the game and run:

```bash
bash install.sh --uninstall
```

## Controls

| Key | Action |
| --- | --- |
| **F9** | Open/close the panel |
| ↑ / ↓ | Select a fog control |
| ← / → | Decrease/increase by 5% |
| V | Distance 0%, atmosphere 20%, depth 100% |
| R | Restore all fog controls to 100% |
| Esc | Close the panel |

The panel uses keyboard controls and is separate from the game's graphics settings.

## If something goes wrong

- **F9 does not open the panel:** make sure you installed this version with the game closed, then restart Hytale.
- **Another shader mod is installed:** remove it before installing ClearView; do not install over Aurora or another mod using the same library.
- **The game fails to start:** uninstall ClearView with the game closed. On Windows, open the installer and click **Remover** (Remove).
- **If something does not work, message me on Discord: `tallmannzera`.**

## About the project

This repository does not include Aurora/Complementary code or shaders, or original Hytale files.

Want to contribute or understand the code? See the **[development guide](docs/development/README.md)** (Portuguese) and the [contribution guidelines](CONTRIBUTING.en.md).

[Changelog](CHANGELOG.md) (Portuguese)
