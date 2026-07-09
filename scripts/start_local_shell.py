#!/usr/bin/env python3
"""Stable local start entrypoint for the CoQuery terminal shell."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app_shell.terminal_shell_prototype.server import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
