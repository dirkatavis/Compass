# utils/data_loader.py
import csv


def load_mvas(csv_path="data/mva.csv"):
    with open(csv_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        mvas = [row[0].strip() for row in reader if row and not row[0].startswith("#")]
    return mvas
