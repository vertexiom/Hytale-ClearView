# Contributing to ClearView

[Português (Brasil)](CONTRIBUTING.md) | **English**

Start with the [development guide](docs/development/README.md), currently in Portuguese. It covers architecture, building, tests, and known limitations.

Submit changes to `staging`, describing the problem, your solution, and how you tested it. Include the operating system, GPU, driver, and Hytale version when reporting failures. Do not submit credentials, personal worlds, or original game libraries or shaders.

When changing player instructions, update both README languages. Keep commands, download filenames, controls, and compatibility information consistent. Use the actual installer button labels so players can follow the instructions.

Publishing to `staging`, `main`, or Releases requires prior confirmation from the maintainer. Prepare and validate changes locally before requesting that confirmation.

Keep visual prototypes, preview HTML, ASCII experiments, experimental screenshots and session notes local. Commit only product code and assets, build tools, automated tests and maintenance documentation. Application icons belong in `assets/icons/`.

Contributions to the original source code must be compatible with GPL-3.0-or-later. Preserve third-party notices and identify the origin and license of any code or assets you add. Before distributing binaries, include LICENSE and dependency notices, and make the complete corresponding source available under the GPL, including build and installation scripts. Do not assume that reference images are licensed for redistribution.

The GitHub Actions workflow and Windows CI tests belong only on `staging`: do not publish these files or their changes to `main`. Promote product fixes selectively; do not merge staging wholesale into main.
