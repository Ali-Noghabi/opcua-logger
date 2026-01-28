@echo off
REM Build script for creating standalone executable (Windows)

echo Building OPC UA Logger GUI standalone executable...

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo Building executable...
pyinstaller opcua_logger_gui.spec --clean --noconfirm

REM Check if build was successful
if exist "dist\OPCUALoggerGUI.exe" (
    echo Build successful! Executable created at: dist\OPCUALoggerGUI.exe
    
    REM Create a distribution directory
    if not exist "dist\OPCUALoggerGUI_Distribution" mkdir "dist\OPCUALoggerGUI_Distribution"
    
    REM Copy essential files
    copy "dist\OPCUALoggerGUI.exe" "dist\OPCUALoggerGUI_Distribution\"
    copy "README.md" "dist\OPCUALoggerGUI_Distribution\"
    copy "sample_tags.csv" "dist\OPCUALoggerGUI_Distribution\"
    
    REM Create a simple config file if it doesn't exist
    if not exist "dist\OPCUALoggerGUI_Distribution\config.yaml" (
        copy "config.yaml" "dist\OPCUALoggerGUI_Distribution\"
    )
    
    echo Distribution package created at: dist\OPCUALoggerGUI_Distribution\
    echo You can now run: dist\OPCUALoggerGUI_Distribution\OPCUALoggerGUI.exe
) else (
    echo Build failed! Please check the error messages above.
    pause
    exit /b 1
)

pause