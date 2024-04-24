import csv
import sqlite3
import sqlite_utils
from pathlib import Path
from datetime import datetime
import re

# Path to the original alerts.csv
csv_file_path = 'clean_nametype.csv'

# Path to the directory containing the .txt files
txt_files_directory = Path('combined_text')
# Path to the SQLite database
db_path = 'docs_clean.db'

# Create or open the SQLite database
db = sqlite_utils.Database(db_path)

# Define a function to read the text from a .txt file
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Assuming alerts.csv is already modified to include a 'filename' column
rows = []
with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    # Add 'filename' to the fieldnames if it's not already included
    fieldnames = reader.fieldnames + ['filename'] if 'filename' not in reader.fieldnames else reader.fieldnames
    # Assume 'date' is the name of the date column to be transformed
    fieldnames = [fn for fn in fieldnames if fn != 'date'] + ['date'] + ['text'] + ['license_num'] + ['case_num'] # Ensure 'date' is in the last position for reordering if needed
    for row in reader:
        # Generate the path to the .txt file based on the filename column
        txt_file_path = txt_files_directory / row['filename']
        # Check if the .txt file exists
        if txt_file_path.exists():
            # Read the content of the .txt file
            row['text'] = read_text_file(txt_file_path)
            text_file = read_text_file(txt_file_path).upper()
            if re.search("LICENSE NUMBER: (\w+)", text_file):
                license_num = re.search("LICENSE NUMBER: (\w+)", text_file)
                row['license_num'] = str(license_num.group(0)).replace("LICENSE NUMBER:", "").strip()
            elif re.search("LICENSE NO.: (\w+)", text_file):
                license_num = re.search("LICENSE NO.: (\w+)", text_file)
                row['license_num'] = str(license_num.group(0)).replace("LICENSE NO.:", "").strip()
            if re.search("CASE NUMBER: (\d{4}-\d{4})", text_file):
                case_num = re.search("CASE NUMBER: (\d{4}-\d{4})", text_file)
                row['case_num'] = str(case_num.group(1)).strip()
            elif re.search("CASE NO.: (\d{4}-\d{4})", text_file):
                case_num = re.search("CASE NO.: (\d{4}-\d{4})", text_file)
                row['case_num'] = str(case_num.group(1)).replace("CASE NO.:", "").strip()
        else:
            # If the file does not exist, set the text to None or an empty string
            row['text'] = None
            row['license_num'] = None
            row['case_num'] = None
        rows.append(row)

with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# Read the CSV file and insert its data into the SQLite database
def csv_to_sqlite(csv_file, table_name):
    with open(csv_file, "r", newline="") as file:
        reader = csv.DictReader(file)
        db = sqlite_utils.Database(db_path)
        db[table_name].insert_all(reader)

# Call the function to convert CSV to SQLite
csv_to_sqlite(csv_file_path, "alerts")

db["alerts"].enable_fts(["text"], tokenize="porter", replace=True)