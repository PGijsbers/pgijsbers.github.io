# Scripts for Website Font Subsetting

This directory contains all scripts used for the font subsetting of my homepage.
It requires a Python environment with `fonttools[woff]` installed:

```text
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
./subset.sh WEBSITE_DIRECTORY FONT_FILE OUTPUT_FILE
```

Where:
 - `WEBSITE_DIRECTORY`: a directory in which all `html` files will be checked for used characters.
 - `FONT_FILE`: a font file to subset
 - `OUTPUT_FILE`: the subset font file in `woff2` format.
