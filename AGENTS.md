# AGENTS.md - OPC UA Logger Project Guide

This document helps agents work effectively with the OPC UA Logger project.

## Project Overview

OPC UA Logger is a Python application that subscribes to OPC UA tags and logs data changes to JSON files with CSV conversion capability. It includes both CLI and GUI versions.

## Key Commands

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt          # Runtime dependencies
pip install -r requirements_build.txt    # Build dependencies (includes PyInstaller)

# Run the application
./run_logger.sh                          # CLI version
python run_gui.py                        # GUI version

# Test connection
./test_connection.sh

# Build executables
pyinstaller opcua_logger_gui.spec --clean --noconfirm  # Cross-platform
./build_windows.bat                     # Windows-specific
```

### Release Commands
```bash
# To create a new release:
git tag v1.0.0
git push origin v1.0.0
# This triggers GitHub Actions to build and release executables
```

## Project Structure

### Core Files
- `opcua_logger.py` - Main CLI application
- `opcua_logger_gui.py` - GUI application (Tkinter-based)
- `config.yaml` - Configuration file for OPC UA connections
- `generate_cert.py` - Certificate generation utility
- `json_to_csv.py` - JSON to CSV conversion utility

### Build Files
- `opcua_logger_gui.spec` - PyInstaller specification for GUI executable
- `requirements_build.txt` - Build-time dependencies
- `version_info.txt` - Windows executable version information
- `build_windows.bat` - Windows build script

### Configuration Files
- `sample_tags.csv` - Sample OPC UA tags configuration
- `test_server.py` - Test OPC UA server

## Code Patterns and Conventions

### Configuration Management
- All configuration is in `config.yaml`
- Supports multiple security policies and message modes
- Certificate paths are configurable for encrypted connections

### OPC UA Connection Patterns
- Uses asyncua library for async OPC UA operations
- Supports all standard security policies:
  - None, Basic128Rsa15, Basic256, Basic256Sha256, Aes128Sha256RsaOaep, Aes256Sha256RsaPss
- Message security modes: None, Sign, SignAndEncrypt

### Logging Pattern
- Logs only data changes (not polling)
- JSON format with timestamps
- Tag-based organization: `{"TagName": [{"timestamp": "...", "value": ...}]}`

### GUI Architecture
- Tkinter-based GUI
- Separate thread for OPC UA operations to prevent UI freezing
- Queue-based communication between GUI and OPC UA threads

## Testing

### Local Testing
```bash
# Test with built-in test server
./test_connection.sh

# Manual testing
python test_server.py  # Start test server in one terminal
./run_logger.sh        # Run logger in another
```

### Build Testing
Always test executables on clean systems without Python installed to ensure they're truly standalone.

## Release Process

### Automated Releases
1. Push a version tag (e.g., `v1.0.0`)
2. GitHub Actions automatically:
   - Creates a GitHub release
   - Builds executables for Windows, Linux, and macOS
   - Uploads assets to the release

### Manual Testing Before Release
1. Test the build locally
2. Verify executable works without Python dependencies
3. Test all security policies and authentication methods

## Important Gotchas

### PyInstaller Issues
- Hidden imports must be explicitly listed in `.spec` file
- Certificate files need to be included as data files
- Windows-specific version info requires `version_info.txt`

### OPC UA Security
- Certificates must be generated before using encrypted connections
- Certificate paths in config must be absolute or relative to executable
- Different servers may require different security policies

### Cross-Platform Considerations
- Windows uses `copy` command, Unix systems use `cp`
- Path separators differ (use `os.path.join()` in code)
- Archive formats: Windows (zip), macOS/Linux (tar.gz)

### Dependencies
- asyncua is the core OPC UA library
- cryptography needed for certificate handling
- pandas required for CSV conversion
- PyInstaller for executable creation

## GitHub Actions Workflow

The `.github/workflows/build.yml` workflow:
1. Triggers on tags (v*), pushes to main/master, and releases
2. Creates releases automatically when tags are pushed
3. Builds on Windows, Linux, and macOS
4. Uploads artifacts and release assets

## Security Considerations

- Executables include all dependencies (large attack surface)
- Always scan final executables with antivirus
- Consider code signing for Windows releases
- Keep dependencies updated for security patches