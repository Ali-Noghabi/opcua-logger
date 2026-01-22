# Deployment Guide for OPC UA Logger GUI

This guide explains how to create standalone executables for the OPC UA Logger GUI on different platforms.

## Prerequisites

### For Building on Linux/Manjaro:
```bash
# Install Python 3.7+ if not already installed
sudo pacman -S python python-pip

# Install build dependencies
pip install -r requirements_build.txt
```

### For Building on Windows:
1. Install Python 3.7+ from [python.org](https://www.python.org/downloads/)
2. Make sure to add Python to PATH during installation
3. Open Command Prompt or PowerShell as Administrator
4. Install build dependencies:
```cmd
pip install -r requirements_build.txt
```

## Building the Executable

### Option 1: On Linux/Manjaro (for Linux executable)
```bash
# Make the build script executable
chmod +x build_linux.sh

# Run the build script
./build_linux.sh
```

### Option 2: On Windows (for Windows executable)
1. Open Command Prompt or PowerShell
2. Navigate to the project directory
3. Run the build script:
```cmd
build_windows.bat
```

### Option 3: Manual Build (Cross-platform)
```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable
pyinstaller opcua_logger_gui.spec --clean --noconfirm
```

## Output Structure

After successful build, you'll find:

```
dist/
├── OPCUALoggerGUI.exe (Windows) or OPCUALoggerGUI (Linux)
└── OPCUALoggerGUI_Distribution/
    ├── OPCUALoggerGUI.exe (or OPCUALoggerGUI)
    ├── README_GUI.md
    ├── sample_tags.csv
    └── config.yaml
```

## Distribution

### For Windows Users:
1. Navigate to `dist/OPCUALoggerGUI_Distribution/`
2. ZIP the entire folder
3. Distribute the ZIP file to end users
4. Users can extract and run `OPCUALoggerGUI.exe` directly

### For Linux Users:
1. Navigate to `dist/OPCUALoggerGUI_Distribution/`
2. Create a tarball:
```bash
cd dist/
tar -czf OPCUALoggerGUI_Linux.tar.gz OPCUALoggerGUI_Distribution/
```
3. Distribute the tarball to end users
4. Users can extract and run `./OPCUALoggerGUI`

## Cross-Platform Building

If you want to build Windows executables from Linux, you can use:

### Option 1: Docker (Recommended)
```bash
# Build a Windows cross-compilation environment
docker build -t win-builder .

# Build the Windows executable
docker run --rm -v "$(pwd)":/src win-builder
```

### Option 2: Wine
```bash
# Install Wine
sudo pacman -S wine

# Install Python in Wine
winecfg  # Configure Wine for Windows 10
wine msiexec /i python-3.11.0-amd64.exe

# Install dependencies and build
wine pip install -r requirements_build.txt
wine pyinstaller opcua_logger_gui.spec --clean --noconfirm
```

### Option 3: GitHub Actions (Automated)
Use the provided `.github/workflows/build.yml` to automatically build executables for multiple platforms.

## Troubleshooting

### Common Issues:

1. **ModuleNotFoundError**: Ensure all dependencies are listed in `requirements_build.txt`
2. **DLL not found**: On Windows, ensure Visual C++ Redistributable is installed
3. **Permission denied**: On Linux, make the executable file executable: `chmod +x OPCUALoggerGUI`
4. **Certificate generation fails**: Ensure OpenSSL is available on the target system

### Size Optimization:

The executable may be large (100-200MB) due to included dependencies. To reduce size:

1. Use UPX compression (already enabled in the spec file)
2. Remove unused modules from the spec file
3. Use `--exclude-module` flag for modules you don't need

### Testing:

Always test the executable on a clean system (without Python installed) to ensure it's truly standalone.

## Files Included in Executable

The standalone executable includes:
- Main GUI application (`opcua_logger_gui.py`)
- Core logger (`opcua_logger.py`)
- Certificate generator (`generate_cert.py`)
- JSON to CSV converter (`json_to_csv.py`)
- Default configuration (`config.yaml`)
- All required Python libraries and dependencies

## Security Considerations

1. The executable includes all dependencies, which may increase the attack surface
2. Always scan the final executable with antivirus software
3. Consider code signing for Windows distribution
4. Keep dependencies updated to patch security vulnerabilities

## Automated Building

For automated builds, consider using:
- GitHub Actions (cross-platform)
- GitLab CI/CD
- Jenkins with multiple agents

See `.github/workflows/build.yml` for an example GitHub Actions workflow.