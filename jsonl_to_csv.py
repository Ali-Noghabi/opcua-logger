import json
import csv
from collections import defaultdict
from typing import Dict, List, Any, Optional

class JSONLToCSVConverter:
    """A class to convert JSONL files to CSV format without running as a script."""
    
    def __init__(self):
        self.data = defaultdict(lambda: {"timestamps": [], "values": []})
    
    def load_jsonl(self, jsonl_file: str) -> bool:
        """
        Load data from a JSONL file.
        
        Args:
            jsonl_file: Path to the JSONL file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.data = defaultdict(lambda: {"timestamps": [], "values": []})
            
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    record = json.loads(line)
                    tag = record["tag"]
                    timestamp = record["timestamp"]
                    value = record["value"]
                    
                    self.data[tag]["timestamps"].append(timestamp)
                    self.data[tag]["values"].append(value)
            
            return True
        except Exception as e:
            print(f"Error loading JSONL file: {e}")
            return False
    
    def convert_to_csv(self, csv_file: str, format_type: str = "default") -> bool:
        """
        Convert loaded data to CSV format.
        
        Args:
            csv_file: Path to output CSV file
            format_type: Format type - "default" or "old_format"
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                if format_type == "default":
                    # Default format: timestamp and value rows for each tag
                    for tag, tag_data in self.data.items():
                        # Row 1: timestamps
                        timestamp_row = [f"timestamp_{tag}"] + tag_data["timestamps"]
                        writer.writerow(timestamp_row)
                        
                        # Row 2: values
                        value_row = [f"value_{tag}"] + tag_data["values"]
                        writer.writerow(value_row)
                else:
                    # Old format: tag_name row followed by timestamp row
                    for tag, tag_data in self.data.items():
                        if not tag_data["values"]:
                            continue
                        # Value row
                        data_row = [tag] + [str(v) for v in tag_data["values"]]
                        writer.writerow(data_row)
                        # Timestamp row
                        timestamp_row = ["timestamp"] + tag_data["timestamps"]
                        writer.writerow(timestamp_row)
            
            return True
        except Exception as e:
            print(f"Error writing CSV file: {e}")
            return False
    
    def convert_jsonl_to_csv(self, jsonl_file: str, csv_file: str, format_type: str = "default") -> bool:
        """
        Convert JSONL file directly to CSV.
        
        Args:
            jsonl_file: Path to input JSONL file
            csv_file: Path to output CSV file
            format_type: Format type - "default" or "old_format"
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.load_jsonl(jsonl_file):
            return self.convert_to_csv(csv_file, format_type)
        return False
    
    def get_tags(self) -> List[str]:
        """Get list of tags loaded from JSONL."""
        return list(self.data.keys())
    
    def get_tag_count(self, tag: str) -> int:
        """Get number of data points for a specific tag."""
        return len(self.data[tag]["values"]) if tag in self.data else 0
    
    def get_data_summary(self) -> Dict[str, int]:
        """Get summary of loaded data."""
        return {tag: len(data["values"]) for tag, data in self.data.items()}