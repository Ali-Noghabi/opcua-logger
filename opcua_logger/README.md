# OPC UA Logger

A Python application that subscribes to OPC UA tags and logs data changes to JSON files with CSV conversion capability.

## Features

- ✅ Subscribe to OPC UA server tags (not polling)
- ✅ Log only data changes (efficient logging)
- ✅ Configurable server connection and authentication
- ✅ Support for all security policies and message modes
- ✅ Certificate generation for encrypted connections
- ✅ JSON output with tag names and timestamps
- ✅ JSON to CSV conversion utility
- ✅ Proper exception handling and logging

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Security Configuration

### All Available Security Policies:
- `None` - No encryption
- `Basic128Rsa15` - Basic 128-bit RSA encryption
- `Basic256` - Basic 256-bit encryption
- `Basic256Sha256` - Basic 256-bit with SHA-256
- `Aes128Sha256RsaOaep` - AES 128-bit with SHA-256 and RSA-OAEP
- `Aes256Sha256RsaPss` - AES 256-bit with SHA-256 and RSA-PSS

### All Available Message Security Modes:
- `None` - No security
- `Sign` - Sign messages only
- `SignAndEncrypt` - Sign and encrypt messages

### Certificate Generation

For encrypted connections, generate certificates:

```bash
# Generate certificates and update config automatically
./setup_certificates.sh

# Or generate manually
python generate_cert.py --cn "MyOPCUAClient" --org "MyCompany" --days 3650 --update-config
```

## Configuration

Edit `config.yaml` to configure your OPC UA server and tags:

```yaml
# OPC UA Server Configuration
server:
  url: "opc.tcp://your-server:4840"
  security_policy: "None"  # None, Basic128Rsa15, Basic256, Basic256Sha256, Aes128Sha256RsaOaep, Aes256Sha256RsaPss
  message_security_mode: "None"  # None, Sign, SignAndEncrypt
  username: null
  password: null
  certificate_path: certs/opcua_client_certificate.pem  # Required for encrypted connections
  private_key_path: certs/opcua_client_private_key.pem  # Required for encrypted connections

# Tags to subscribe to
tags:
  - node_id: "ns=2;s=Temperature"
    name: "Temperature"
  - node_id: "ns=2;s=Pressure" 
    name: "Pressure"

# JSON logging configuration
logging:
  json_file: "opcua_data.json"
  timestamp_format: "%Y-%m-%d %H:%M:%S.%f"
```

## Usage

### Basic Usage (No Encryption)
```bash
./run_logger.sh
```

### Convert JSON to CSV
```bash
# Convert default JSON file to CSV
python3 json_to_csv.py

# Convert specific JSON file to CSV
python3 json_to_csv.py opcua_data.json opcua_data.csv
```

### With Encryption
```bash
# 1. Generate certificates
./setup_certificates.sh

# 2. Edit config.yaml to set security policy and mode
# security_policy: "Basic256Sha256"
# message_security_mode: "SignAndEncrypt"

# 3. Run the logger
./run_logger.sh
```

### Testing
```bash
# Test with built-in test server
./test_connection.sh
```

## JSON and CSV Output Format

### JSON Output
The logger saves data in JSON format with the following structure:
```json
{
  "Temperature": [
    {
      "timestamp": "2024-01-15 10:30:15.123456",
      "value": 25.5
    },
    {
      "timestamp": "2024-01-15 10:30:20.234567", 
      "value": 26.0
    }
  ],
  "Pressure": [
    {
      "timestamp": "2024-01-15 10:30:15.123456",
      "value": 101.3
    },
    {
      "timestamp": "2024-01-15 10:30:20.234567",
      "value": 101.5
    }
  ]
}
```

### CSV Output (after conversion)
The CSV file contains two rows for each data update:

Row 1 (Data): `tag_name, value1, value2, value3, ...`
Row 2 (Timestamps): `update_timestamp, timestamp1, timestamp2, timestamp3, ...`

Example:
```
tag_name,Temperature,Pressure,FlowRate
update_timestamp,2024-01-15 10:30:15.123456,2024-01-15 10:30:15.123456,2024-01-15 10:30:15.123456
25.5,101.3,15.2
2024-01-15 10:30:20.234567,2024-01-15 10:30:20.234567,2024-01-15 10:30:20.234567
26.0,101.5,15.8
2024-01-15 10:30:25.345678,2024-01-15 10:30:25.345678,2024-01-15 10:30:25.345678
```

## Security Policy Combinations

The logger supports all combinations of security policies and message modes:

| Security Policy | Message Mode | asyncua Security Type |
|---------------|--------------|---------------------|
| None | None | NoSecurity |
| Basic128Rsa15 | Sign | Basic128Rsa15_Sign |
| Basic128Rsa15 | SignAndEncrypt | Basic128Rsa15_SignAndEncrypt |
| Basic256 | Sign | Basic256_Sign |
| Basic256 | SignAndEncrypt | Basic256_SignAndEncrypt |
| Basic256Sha256 | Sign | Basic256Sha256_Sign |
| Basic256Sha256 | SignAndEncrypt | Basic256Sha256_SignAndEncrypt |
| Aes128Sha256RsaOaep | Sign | Aes128Sha256RsaOaep_Sign |
| Aes128Sha256RsaOaep | SignAndEncrypt | Aes128Sha256RsaOaep_SignAndEncrypt |

## Dependencies

- `asyncua`: Modern async OPC UA client library
- `pyyaml`: YAML configuration file parsing
- `cryptography`: Certificate generation

## Troubleshooting

### Connection Issues
1. Verify server URL and port
2. Check if server allows anonymous connections
3. For encrypted connections, ensure certificates are generated
4. Check firewall settings

### Node ID Issues
1. Verify node IDs match server configuration
2. Use OPC UA client tools to browse available nodes
3. Check namespace index (ns=) is correct

### Certificate Issues
1. Ensure certificate files exist and are readable
2. Check certificate paths in config.yaml
3. Regenerate certificates if needed

## Files

- `opcua_logger.py` - Main application
- `config.yaml` - Configuration file
- `generate_cert.py` - Certificate generator
- `json_to_csv.py` - JSON to CSV conversion utility
- `setup_certificates.sh` - Certificate setup script
- `test_server.py` - Test OPC UA server
- `test_connection.sh` - Connection test script
- `run_logger.sh` - Main application runner