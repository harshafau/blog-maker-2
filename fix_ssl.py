#!/usr/bin/env python3
"""
Fix SSL Certificate Verification on macOS

This script installs the certificates required for SSL verification on macOS.
"""

import os
import sys
import subprocess
import platform

def main():
    """Main function to fix SSL certificates"""
    if platform.system() != "Darwin":
        print("This script is only for macOS. Exiting.")
        return
    
    print("Fixing SSL certificate verification for macOS...")
    
    # Get Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Find the correct path to the certificate installation script
    cert_command = f"/Applications/Python {python_version}/Install Certificates.command"
    
    if not os.path.exists(cert_command):
        # Try alternative locations
        alt_locations = [
            f"/Library/Frameworks/Python.framework/Versions/{python_version}/Resources/Python.app/Contents/MacOS/Install Certificates.command",
            f"/Library/Frameworks/Python.framework/Versions/{sys.version_info.major}.{sys.version_info.minor}/bin/Install Certificates.command"
        ]
        
        for loc in alt_locations:
            if os.path.exists(loc):
                cert_command = loc
                break
        else:
            # If not found, try to use certifi directly
            try:
                import certifi
                import ssl
                print(f"Using certifi path: {certifi.where()}")
                ssl._create_default_https_context = ssl._create_unverified_context
                print("SSL certificate verification temporarily disabled.")
                return
            except ImportError:
                print("Could not find the certificate installation script.")
                print("Please install the 'certifi' package: pip install certifi")
                return
    
    # Run the certificate installation script
    try:
        print(f"Running: {cert_command}")
        subprocess.run(["/bin/bash", cert_command], check=True)
        print("SSL certificates installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing certificates: {e}")
        print("You may need to run this script with sudo.")

if __name__ == "__main__":
    main()
