<h1 align="center">Hytale ClearView</h1>

<p align="center">
  <a href="README.md">English</a> | <a href="README.pt-BR.md">Português (Brasil)</a>
</p>

**ClearView is a mod for controlling Hytale's fog while keeping the game's original lighting.** Open the panel with **F9** and adjust the fog intensity to your liking.

The project is intended for visual customization, not as a cheating tool or a way to bypass game or server rules.

> **Multiplayer disclaimer:** Before using ClearView on any multiplayer server, consult its admin team and confirm that the mod is allowed. If it is not allowed, do not use it on that server.

**Hytale ClearView is in early development — v0.1.2.** Hytale updates may require changes to the mod.


[Aurora Shaders](https://github.com/Kristijan1001/Hytale-Aurora-Shaders) was used as a reference to understand how shaders work and develop ClearView, which has its own independent code.

I'm developing this mod because my friend Lazan is Hytale fog's number one enemy.

## Download

- **Linux v0.1.2:** [ClearView-0.1.2-linux-x64.tar.gz](https://github.com/vertexiom/Hytale-ClearView/releases/download/v0.1.2/ClearView-0.1.2-linux-x64.tar.gz)
- **Windows v0.1.1:** [ClearView-0.1.1-Setup.exe](https://github.com/vertexiom/Hytale-ClearView/releases/download/v0.1.1/ClearView-0.1.1-Setup.exe).

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

The installer interface is currently in Portuguese; button names in this guide are translated into English.

1. Download and open **ClearView-0.1.1-Setup.exe**.
2. Close Hytale. The installer finds the game folder automatically; if needed, click **Browse** and select `HytaleClient.exe`.
3. Click **Install / Update** and wait for confirmation.
4. Open the game through its launcher, enter a world, and press **F9**.

Checks run automatically. You do not need to extract files, use a terminal, install Python, or run scripts. To uninstall, open the same installer and click **Remove**. Updating preserves existing settings.

## Install on Linux

Download **ClearView-0.1.2-linux-x64.tar.gz** and extract the entire folder. Close Hytale, open a terminal inside that folder and run:

```bash
bash install.sh
```

The graphical installer opens directly. Click **Continue**, confirm the game folder, then click **Install**. Wait for completion and open Hytale through its normal launcher. Press **F9** in-game.

The mod is precompiled; no compiler or app store is needed. Run without `sudo`. If the script reports missing interface dependencies, install them on Ubuntu/Debian with:

```bash
sudo apt install python3 python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-4.0
```

Then run `bash install.sh` again. To update or remove the mod, close the game and open the same installer. Deleting the installer folder does not remove the mod.

The Linux x64 package requires glibc 2.38 or later and the system GTK/Python dependencies above. The installer interface is currently in Portuguese; button names above are translated into English.

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
- **The game fails to start:** uninstall ClearView with the game closed. On Windows, open the installer and click **Remove**.
- **If something does not work, message me on Discord: `tallmannzera`.**

## About the project

This repository does not include Aurora/Complementary code or shaders, or original Hytale files.

Want to contribute or understand the code? See the **[development guide](docs/development/README.md)** (Portuguese) and the [contribution guidelines](CONTRIBUTING.en.md).

[Changelog](CHANGELOG.md) (Portuguese)
