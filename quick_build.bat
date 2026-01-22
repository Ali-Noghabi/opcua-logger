@echo off
REM Quick build script for Windows - One executable with all dependencies

echo ========================================
echo OPC UA Logger GUI - Quick Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Install PyInstaller if not already installed
echo Installing/Updating PyInstaller...
pip install pyinstaller --upgrade
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Building standalone executable...
echo This may take a few minutes...
echo.

REM Build the executable with all dependencies
pyinstaller --onefile --windowed --name "OPCUALoggerGUI" --icon=opcua_icon.ico --version-file=version_info.txt --add-data "config.yaml;." --add-data "generate_cert.py;." --add-data "json_to_csv.py;." --add-data "opcua_logger.py;." opcua_logger_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.

REM Create distribution package
echo Creating distribution package...
if not exist "dist\OPCUALoggerGUI_Distribution" mkdir "dist\OPCUALoggerGUI_Distribution"

copy "dist\OPCUALoggerGUI.exe" "dist\OPCUALoggerGUI_Distribution\" >nul
copy "README_GUI.md" "dist\OPCUALoggerGUI_Distribution\" >nul 2>&1
copy "sample_tags.csv" "dist\OPCUALoggerGUI_Distribution\" >nul 2>&1
copy "config.yaml" "dist\OPCUALoggerGUI_Distribution\" >nul 2>&1

echo.
echo Your standalone executable is ready!
echo Location: dist\OPCUALoggerGUI_Distribution\OPCUALoggerGUI.exe
echo.
echo You can now:
echo 1. Test the executable by running: dist\OPCUALoggerGUI_Distribution\OPCUALoggerGUI.exe
echo 2. Distribute the entire OPCUALoggerGUI_Distribution folder
echo 3. Create a ZIP file of the OPCUALoggerGUI_Distribution folder for distribution
echo.

REM Ask if user wants to test the executable
set /p test="Do you want to test the executable now? (y/n): "
if /i "%test%"=="y" (
    echo.
    echo Starting OPC UA Logger GUI...
    start "" "dist\OPCUALoggerGUI_Distribution\OPCUALoggerGUI.exe"
    echo GUI started! Check if it opens correctly.
)

echo.
echo Build process completed!
pause