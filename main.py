#!/usr/bin/env python3
"""Ship the finished front page to the grader.

The front page is already drawn and stored in this repository as
entry.png. This program draws nothing and fetches nothing: it only
copies that one file into the folder the grader points to with the
MAKEFUN_OUTPUT_DIR environment variable. Because it only reads and
copies, it works even when this repository is mounted read-only.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    dest_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "entry.png"
    shutil.copyfile(source, dest)
    print("entry.png -> %s" % dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
