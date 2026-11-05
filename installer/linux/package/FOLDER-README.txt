CLEARVIEW 0.1.2 — LINUX x64

1. Extract the entire folder. Do not move install.sh on its own.
2. Close Hytale.
3. Open a terminal in this folder and run:

   bash install.sh

4. In the installer, continue, confirm the Hytale folder, and install.
5. Once finished, open the game through its normal launcher. Press F9
   in-game to open the fog controls.

The same command opens the interface to update or remove the mod.
Your settings are preserved. Do not run install.sh with sudo.
No .deb package, app store, or compiler is required.

The interface requires system-provided Python 3, GTK 4, PyGObject, and Cairo.
If dependencies are missing on Ubuntu/Debian, install them once:

   sudo apt install python3 python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-4.0

Then run bash install.sh again, without sudo.

This package was built on Ubuntu 26.04 amd64. The mod requires glibc >= 2.38.
Other distributions and runtimes still need compatibility validation.
GTK dependencies are not bundled; this is not a system-independent executable.

The mod is installed in the Hytale folder. Deleting this installer folder
will not uninstall the mod. Use the removal option inside the installer.
No original Hytale files are included in this package.

Discord support: tallmannzera
Project: https://github.com/vertexiom/Hytale-ClearView

Advanced command-line usage: bash install.sh --cli --help

When opened, the installer registers its name and icon in
~/.local/share/applications and ~/.local/share/icons (or XDG_DATA_HOME),
without sudo. If you move the folder, run bash install.sh again to update
the shortcut.
