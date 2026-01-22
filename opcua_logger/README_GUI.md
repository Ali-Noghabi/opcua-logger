# OPC UA Logger GUI

A comprehensive GUI for configuring and running the OPC UA logger with the following features:

## Features

### Configuration Tab
- **Server Configuration**: Configure OPC UA server connection settings
  - Server URL
  - Security Policy (combobox with options: None, Basic128Rsa15, Basic256, Basic256Sha256, Aes128Sha256RsaOaep)
  - Message Security Mode (combobox with options: None, Sign, SignAndEncrypt)
  - Username/Password (only available for proper authentication modes)
  - Certificate/Private Key paths with browse buttons
- **Logging Configuration**: 
  - Data file path
  - Timestamp format (combobox with common formats)

### Tags Tab
- **Table View**: Display all configured tags in a table format
- **Tag Management**: Add, Edit, Delete tags
- **CSV Import/Export**: Import tags from CSV file or export current tags to CSV
  - CSV format requires columns: `name,node_id`

### Actions Tab
- **Certificate Generation**: 
  - Generate self-signed certificates for secure connections
  - Configure Common Name, Organization, Country
  - Choose output directory
  - Automatically updates config.yaml with certificate paths
- **Data Conversion**:
  - Convert JSON data to CSV format
  - Select input JSON file and output CSV file

### Logs Tab
- **Logger Control**: Start/Stop the OPC UA logger
- **Log Viewer**: Real-time display of logger output
- **Clear Logs**: Clear the log display

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the GUI:
```bash
python3 run_gui.py
```

or

```bash
python3 opcua_logger_gui.py
```

## Usage

### Basic Setup
1. **Configure Server**: Set your OPC UA server URL in the Configuration tab
2. **Add Tags**: Add tags you want to monitor in the Tags tab
   - You can add tags manually or import from CSV
   - Sample CSV format provided in `sample_tags.csv`
3. **Save Configuration**: Click "Save Configuration" to save your settings

### Running the Logger
1. Go to the Logs tab
2. Click "Start Logger" to begin data collection
3. Monitor the log output for connection status and data collection
4. Click "Stop Logger" to stop data collection

### Security Setup
1. Go to the Actions tab
2. Configure certificate details
3. Click "Generate Certificate" to create certificates
4. Set Security Policy and Message Security Mode in Configuration tab
5. Save configuration and restart logger

### Data Conversion
1. Go to the Actions tab
2. Select input JSON file and output CSV file
3. Click "Convert JSON to CSV" to convert collected data

## File Structure

- `opcua_logger_gui.py` - Main GUI application
- `run_gui.py` - Launcher script
- `config.yaml` - Configuration file
- `opcua_logger.py` - Core OPC UA logger
- `generate_cert.py` - Certificate generation script
- `json_to_csv.py` - Data conversion script
- `sample_tags.csv` - Sample tags for import

## Security Options

The GUI supports all security combinations available in the OPC UA logger:
- No Security (None/None)
- Basic128Rsa15 (Sign/SignAndEncrypt)
- Basic256 (Sign/SignAndEncrypt)
- Basic256Sha256 (Sign/SignAndEncrypt)
- Aes128Sha256RsaOaep (Sign/SignAndEncrypt)

## Troubleshooting

1. **Connection Issues**: Check server URL and security settings
2. **Certificate Issues**: Generate new certificates using the Actions tab
3. **Tag Issues**: Verify node IDs are correct for your OPC UA server
4. **Import Issues**: Ensure CSV file has correct column headers (name,node_id)

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- asyncua
- pyyaml
- cryptography
- pandas