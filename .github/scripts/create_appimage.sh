#!/bin/bash

# Script to create AppImage after PyInstaller build

set -e

# Create AppDir structure
mkdir -p OPCUALoggerGUI.AppDir/usr/bin
mkdir -p OPCUALoggerGUI.AppDir/usr/share/applications
mkdir -p OPCUALoggerGUI.AppDir/usr/share/icons

# Copy executable
cp dist/OPCUALoggerGUI OPCUALoggerGUI.AppDir/usr/bin/

# Copy data files
cp config.yaml OPCUALoggerGUI.AppDir/usr/share/
cp sample_tags.csv OPCUALoggerGUI.AppDir/usr/share/

# Create desktop file
cat > OPCUALoggerGUI.AppDir/usr/share/applications/OPCUALoggerGUI.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=OPC UA Logger GUI
Exec=usr/bin/OPCUALoggerGUI
Icon=usr/share/icons/OPCUALoggerGUI.png
Categories=Development;Engineering;
EOF

# Create AppRun script
cat > OPCUALoggerGUI.AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${HERE}/usr/lib64:${LD_LIBRARY_PATH}"
export PATH="${HERE}/usr/bin:${PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share"
exec "${HERE}/usr/bin/OPCUALoggerGUI" "${@}"
EOF
chmod +x OPCUALoggerGUI.AppDir/AppRun

# Download appimagetool if not exists
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppImage
./appimagetool-x86_64.AppImage OPCUALoggerGUI.AppDir

# Move AppImage to dist directory
if [ -f "OPCUALoggerGUI-x86_64.AppImage" ]; then
    mv OPCUALoggerGUI-x86_64.AppImage dist/
    echo "AppImage moved to dist/ directory"
fi

echo "AppImage created successfully"