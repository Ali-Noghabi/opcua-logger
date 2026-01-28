import json
import csv
import sys
import os


def json_to_csv(json_path: str, csv_path: str) -> None:
    """Convert JSON data to CSV format with tag and timestamp rows."""
    try:
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        csv_rows = []
        
        # Process each tag
        for tag_name, values in data.items():
            if not values:
                continue
                
            # Data row: tag_name, value1, value2, value3, ...
            data_row = [tag_name] + [str(item['value']) for item in values]
            csv_rows.append(data_row)
            
            # Timestamp row: "timestamp", timestamp1, timestamp2, timestamp3, ...
            timestamp_row = ['timestamp'] + [item['timestamp'] for item in values]
            csv_rows.append(timestamp_row)
        
        # Write to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_rows)
        
        print(f"Successfully converted {json_path} to {csv_path}")
        print(f"Written {len(csv_rows)} rows")
        
    except FileNotFoundError:
        print(f"Error: JSON file {json_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    # Default paths
    default_json = "opcua_data.json"
    default_csv = "opcua_data.csv"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = default_json
    
    if len(sys.argv) > 2:
        csv_path = sys.argv[2]
    else:
        csv_path = default_csv
    
    # Check if JSON file exists
    if not os.path.exists(json_path):
        print(f"JSON file '{json_path}' not found!")
        print(f"Usage: python3 json_to_csv.py [json_file] [csv_file]")
        print(f"Example: python3 json_to_csv.py {default_json} {default_csv}")
        sys.exit(1)
    
    # Convert JSON to CSV
    json_to_csv(json_path, csv_path)


if __name__ == "__main__":
    main()