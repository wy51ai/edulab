#!/usr/bin/env bash
# Cross-platform checks live in Python; this entry point remains compatible.
set -euo pipefail
SCRIPT="$(cd "$(dirname "$0")" && pwd -P)"
for candidate in /usr/bin/python3 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import numpy, requests, pypinyin" 2>/dev/null; then
    exec "$candidate" "$SCRIPT/setup_check.py" "${1:-.}"
  fi
done
echo 'MISSING Python with numpy, requests, pypinyin: python -m pip install numpy requests pypinyin pillow'
exit 1
