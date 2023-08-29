"""Script to prepare a website build for publication. To be ran from the 2023 directory.

This script performs the following actions:
 - create a font subset and update HTML and CSS files accordingly.
 - TODO: in-line css
 - TODO: Create derived images (file formats, resolutions)
"""
import argparse
import logging
import hashlib
from pathlib import Path
import shutil
import subprocess

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("build"),
    )
    return parser.parse_args()

def copy_directory_structure(directory: Path, to: Path):
    to.mkdir(exist_ok=True)
    for subdirectory in (d for d in directory.iterdir() if d.is_dir() and d != to):
        copy_directory_structure(subdirectory, to / subdirectory.name)


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=logging.INFO)

    # We don't support incremental builds right now,
    # to avoid shipping old files (or having other unwanted side-effects)
    # we always clear the build folder.
    build_directory = args.output_directory
    shutil.rmtree(build_directory, ignore_errors=True)
    copy_directory_structure(directory=Path(), to=build_directory)

    font = Path("Figtree.woff2")
    subset_font = build_directory / "fonts/Figtree.subset.woff2"
    logging.info(f"Subsetting {font!s}")
    subprocess.run([
        "python",
        "../scripts/subsetting/subset.py",
        "--html-directory=.",
        f"--font-file=fonts/{font!s}",
        f"--output-file={subset_font!s}",
    ])

    # We want to encode the hash in the file name, to avoid a possible cache hit
    # when the subset has changed (extended) and the user should download the
    # new subset with additional glyphs.
    font_hash = hashlib.md5(subset_font.read_bytes()).hexdigest()[:8]
    name_with_hash = subset_font.with_name(f"{font.stem}-{font_hash}.woff2")
    subset_font = subset_font.rename(name_with_hash)

    logging.info(f"\nReplacing references to `{font!s}` with `{subset_font!s}`")
    for file in Path().iterdir():
        if not file.is_file() or file.suffix not in [".html", ".css"]:
            continue
        updated_content = file.read_text().replace(font.name, subset_font.name)
        (build_directory / file.name).write_text(updated_content)


    # TODO: in-line CSS

    # TODO: generate derivative images (sizes, formats)
    # placeholder: copy over manually created images
    shutil.copytree("img", build_directory / "img", dirs_exist_ok=True)
