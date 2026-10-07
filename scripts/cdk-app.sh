#!/bin/sh
set -eu

if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "${VIRTUAL_ENV}/bin/python" ]; then
    exec "${VIRTUAL_ENV}/bin/python" app.py
fi

if [ -x .venv/bin/python ]; then
    exec .venv/bin/python app.py
fi

if [ -x venv/bin/python ]; then
    exec venv/bin/python app.py
fi

echo "No project Python environment found; run 'uv sync --frozen --all-groups'." >&2
exit 1
