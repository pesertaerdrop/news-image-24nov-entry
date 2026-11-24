#!/usr/bin/env python3
"""Deliver the finished front page to the grader.

The front page for Tuesday 24 November 2026 is already drawn and
stored in this repository as entry.png. This program draws nothing
and fetches nothing: it only copies that one file into the folder
the grader names with the MAKEFUN_OUTPUT_DIR environment variable.
Because it only reads and copies, it keeps working when this
repository is mounted read-only.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    print("entry.png -> %s" % target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
