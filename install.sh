#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# Keep the explicit CLI and legacy automation arguments available.
case "${1:-}" in
  --cli|--client-dir|--mode|--uninstall|--validate-only|--json|--payload)
    if [[ "${1:-}" == --cli ]]; then shift; fi
    if [[ -f "$root/build/libSDL3.so" ]]; then
      exec /usr/bin/python3 "$root/installer/linux/install.py" --payload "$root/build/libSDL3.so" "$@"
    fi
    exec /usr/bin/python3 "$root/installer/linux/install.py" "$@"
    ;;
esac
if [[ "$EUID" -eq 0 ]]; then
  echo 'Abra com seu usuário normal: bash install.sh (sem sudo).' >&2
  exit 1
fi
if ! /usr/bin/python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_foreign('cairo'); from gi.repository import Gtk; import cairo" 2>/dev/null; then
  echo 'Faltam dependências para abrir a interface ClearView.' >&2
  echo 'No Ubuntu/Debian, instale uma vez:' >&2
  echo 'sudo apt install python3 python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-4.0' >&2
  echo 'Depois execute novamente: bash install.sh' >&2
  exit 1
fi
if [[ ! -f "$root/build/libSDL3.so" || ! -f "$root/build/linux-manifest.json" ]]; then
  echo 'Pacote incompleto: use a pasta Linux completa, com o mod pré-compilado.' >&2
  echo 'Se estiver desenvolvendo pelo código-fonte: bash tools/build/build_linux.sh' >&2
  exit 1
fi
exec /usr/bin/python3 "$root/installer/linux/gui/app.py" "$@"
