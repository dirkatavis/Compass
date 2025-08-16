# utils/data_loader.py
import csv


def load_mvas(csv_path="data/mva.csv"):
    with open(csv_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header row
        mvas = [row[0].strip() for row in reader if row]
    return mvas

