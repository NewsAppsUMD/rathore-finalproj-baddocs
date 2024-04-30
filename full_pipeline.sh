#!/bin/bash
pip install csvkit
pip install pdf2image-cli
pip install datasette
pip install sqlite-utils
datasette install datasette-codespaces

python3 scrape.py
Rscript license_mutations.R
bash get_pdfs.sh
bash images.sh
bash ocr.sh
bash combine_text.sh
python3 mod_alerts.py
Rscript data_cleaning.R
bash database_creation.sh



