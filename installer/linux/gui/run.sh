#!/bin/sh
# Use distro Python: PyGObject/GTK are provided by the system packages.
set -eu
GUI_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec /usr/bin/python3 "$GUI_DIR/app.py" "$@"
