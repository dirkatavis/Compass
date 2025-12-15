
# utils/data_loader.py
import csv
import os
import re
from utils.logger import log


def load_mvas(csv_path):
    log.info(f"Loading MVAs from: {csv_path}")
    assert os.path.exists(csv_path), f"CSV file not found: {csv_path}"
    with open(csv_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        mvas = []
        for row in reader:
            if not row:
                continue
            raw = row[0].strip()
            if raw.startswith("#") or raw == "":
                continue

            # Prefer a leading 8-digit MVA (e.g. '12345678AB' -> '12345678')
            m = re.match(r"^(\d{8})", raw)
            if m:
                mva = m.group(1)
            else:
                # Fallback: take the first 8 characters (user requested ignoring trailing data)
                mva = raw[:8]

            mvas.append(mva)

    return mvas
