#!/usr/bin/env python3
"""
Launcher script for OPC UA Logger GUI
"""

import sys
import os
import subprocess

def main():
    """Launch the OPC UA Logger GUI."""
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        # Import and run GUI
        from opcua_logger_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error importing GUI modules: {e}")
        print("Please install required packages:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()