"""Entry point for news-image-20261124.

Copies the pre-built entry.png from this repo directory into the
directory named by MAKEFUN_OUTPUT_DIR. No network, no subprocess,
no image generation at runtime: the image is built offline by
make_image.py and committed, so the graded run only copies bytes.
"""

import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if not out_dir:
        raise SystemExit("MAKEFUN_OUTPUT_DIR is not set")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)


if __name__ == "__main__":
    main()
