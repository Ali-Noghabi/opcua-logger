import json
import csv
from collections import defaultdict
from datetime import datetime, timezone

# -------- configuration --------
jsonl_file = "OL_20hr_it.jsonl"
csv_file = "OL_20hr_it_unix.csv"
# --------------------------------

def to_unix_timestamp(ts_str):
    """
    Convert timestamp string like:
    '2026-01-24 16:20:58.742328'
    to Unix timestamp (float seconds)
    """
    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()

# Data structure:
# {
#   tag: {
#       "timestamps": [...],
#       "values": [...]
#   }
# }
data = defaultdict(lambda: {"timestamps": [], "values": []})

# Read JSONL file
with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        record = json.loads(line)
        tag = record["tag"]
        timestamp_unix = to_unix_timestamp(record["timestamp"])
        value = record["value"]

        data[tag]["timestamps"].append(timestamp_unix)
        data[tag]["values"].append(value)

# Write CSV
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    for tag, tag_data in data.items():
        # Row 1: timestamps
        timestamp_row = [f"timestamp_{tag}"] + tag_data["timestamps"]
        writer.writerow(timestamp_row)

        # Row 2: values
        value_row = [f"value_{tag}"] + tag_data["values"]
        writer.writerow(value_row)
