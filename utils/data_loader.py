
# utils/data_loader.py
import csv
import os


def load_mvas(csv_path):
    assert os.path.exists(csv_path), f"CSV file not found: {csv_path}"
    with open(csv_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        mvas = [row[0].strip() for row in reader if row and not row[0].startswith("#")]
    return mvas
