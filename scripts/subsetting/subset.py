"""Finds all "data" characters across all html files in a directory.

This tool was written to find all visible files in HTML documents,
which may be used to subset fonts. Whitespace characters are excluded.
"""
import argparse
import logging
from html.parser import HTMLParser
from pathlib import Path
import string
import subprocess


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--html-directory",
        help="Directory with HTML files for which to create a font subset.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--font-file",
        help="The font file to subset.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--output-file",
        help="The name for the generated subset font file.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--output-format",
        help="Format to save the desired subset font in.",
        type=str,
        default="woff2",
    )
    return parser.parse_args()


def extract_characters(html: str) -> set[str]:
    """Extract all "data" characters from a valid HTML document."""
    character_set = set()

    class CharacterExtractor(HTMLParser):
        def handle_data(self, data: str):
            character_set.update(data)

    CharacterExtractor().feed(html)
    return character_set

def extract_characters_from_all_html_in_directory(directory: Path) -> str:
    characters = set()
    for file in directory.glob("*.html"):
        characters |= extract_characters(file.read_text())
    return ''.join(c for c in sorted(characters - set(string.whitespace)))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    characters_to_keep = extract_characters_from_all_html_in_directory(args.html_directory)
    logging.info(f"Keeping characters: '{characters_to_keep}'")

    cmd = f"""
        pyftsubset {args.font_file}
           --text={characters_to_keep}
           --output-file={args.output_file}
           --layout-features-=frac,dnom,numr
           --name-IDs=1
           --flavor={args.output_format}
        """.split()
    logging.info(f"running: {' '.join(cmd)}")
    subprocess.run(cmd)
    logging.info(f"Done.")
