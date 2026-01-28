#!/bin/bash
# Build script for creating standalone executable (Linux)

echo "Building OPC UA Logger GUI standalone executable..."

# Check if PyInstaller is installed
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the executable
echo "Building executable..."
python3 -m PyInstaller opcua_logger_gui.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OPCUALoggerGUI" ]; then
    echo "Build successful! Executable created at: dist/OPCUALoggerGUI"
    
    # Create a distribution directory
    mkdir -p "dist/OPCUALoggerGUI_Distribution"
    
    # Copy essential files
    cp "dist/OPCUALoggerGUI" "dist/OPCUALoggerGUI_Distribution/"
    cp "README.md" "dist/OPCUALoggerGUI_Distribution/"
    cp "sample_tags.csv" "dist/OPCUALoggerGUI_Distribution/"
    
    # Create a simple config file if it doesn't exist
    if [ ! -f "dist/OPCUALoggerGUI_Distribution/config.yaml" ]; then
        cp "config.yaml" "dist/OPCUALoggerGUI_Distribution/"
    fi
    
    # Make executable
    chmod +x "dist/OPCUALoggerGUI_Distribution/OPCUALoggerGUI"
    
    echo "Distribution package created at: dist/OPCUALoggerGUI_Distribution/"
    echo "You can now run: ./dist/OPCUALoggerGUI_Distribution/OPCUALoggerGUI"
    
    # Create tarball for distribution
    cd dist
    tar -czf OPCUALoggerGUI_Linux.tar.gz OPCUALoggerGUI_Distribution/
    echo "Created tarball: OPCUALoggerGUI_Linux.tar.gz"
else
    echo "Build failed! Please check the error messages above."
    exit 1
fi