import json
import csv
from collections import defaultdict

# -------- configuration --------
jsonl_file = "json_file_name.jsonl"
csv_file = "csv_file_name.csv"
# --------------------------------

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
        timestamp = record["timestamp"]
        value = record["value"]

        data[tag]["timestamps"].append(timestamp)
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
