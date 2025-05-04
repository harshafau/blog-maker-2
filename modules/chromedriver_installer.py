#!/usr/bin/env python3
"""
ChromeDriver Installer

This script automatically downloads and installs the appropriate ChromeDriver version
for the current operating system and Chrome version.
"""

import os
import sys
import platform
import subprocess
import logging
import requests
import zipfile
import tarfile
import shutil
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_chrome_version():
    """Get the installed Chrome version"""
    system = platform.system()
    try:
        if system == "Windows":
            # Windows
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            version, _ = winreg.QueryValueEx(key, 'version')
            return version
        elif system == "Darwin":
            # macOS
            process = subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = process.communicate()
            version = output.decode('utf-8').strip().split(' ')[-1]
            return version
        elif system == "Linux":
            # Linux
            process = subprocess.Popen(['google-chrome', '--version'], 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = process.communicate()
            version = output.decode('utf-8').strip().split(' ')[-1]
            return version
    except Exception as e:
        logger.warning(f"Could not determine Chrome version: {e}")
    
    # If we can't determine the version, use the latest
    return None

def get_chromedriver_url(chrome_version=None):
    """Get the appropriate ChromeDriver download URL for the current system and Chrome version"""
    system = platform.system()
    machine = platform.machine().lower()
    
    # Determine platform
    if system == "Windows":
        platform_name = "win32"
    elif system == "Darwin":  # macOS
        if "arm" in machine or "aarch64" in machine:
            platform_name = "mac_arm64"
        else:
            platform_name = "mac64"
    elif system == "Linux":
        if "arm" in machine or "aarch64" in machine:
            platform_name = "linux64_arm"
        else:
            platform_name = "linux64"
    else:
        logger.error(f"Unsupported operating system: {system}")
        return None
    
    # If Chrome version is provided, get the matching ChromeDriver version
    if chrome_version:
        major_version = chrome_version.split('.')[0]
        try:
            # For newer Chrome versions (>=115), use the new URL format
            if int(major_version) >= 115:
                # Get the latest ChromeDriver version for this Chrome major version
                url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
                response = requests.get(url)
                if response.status_code == 200:
                    chromedriver_version = response.text.strip()
                    download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform_name}.zip"
                    return download_url
            else:
                # For older Chrome versions
                url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
                response = requests.get(url)
                if response.status_code == 200:
                    chromedriver_version = response.text.strip()
                    download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform_name}.zip"
                    return download_url
        except Exception as e:
            logger.warning(f"Error determining ChromeDriver version for Chrome {chrome_version}: {e}")
    
    # If we couldn't determine the version or there was an error, use the latest stable version
    try:
        url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        response = requests.get(url)
        if response.status_code == 200:
            latest_version = response.text.strip()
            download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_{platform_name}.zip"
            return download_url
    except Exception as e:
        logger.error(f"Error getting latest ChromeDriver version: {e}")
    
    return None

def download_and_install_chromedriver(target_dir=None):
    """Download and install ChromeDriver"""
    if target_dir is None:
        # Use the default location in the modules/webdriver directory
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webdriver')
    
    # Create the target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Get Chrome version
    chrome_version = get_chrome_version()
    if chrome_version:
        logger.info(f"Detected Chrome version: {chrome_version}")
    else:
        logger.warning("Could not detect Chrome version, will use latest ChromeDriver")
    
    # Get ChromeDriver download URL
    download_url = get_chromedriver_url(chrome_version)
    if not download_url:
        logger.error("Could not determine ChromeDriver download URL")
        return False
    
    logger.info(f"Downloading ChromeDriver from: {download_url}")
    
    # Download ChromeDriver
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code != 200:
            logger.error(f"Failed to download ChromeDriver: HTTP {response.status_code}")
            return False
        
        # Save the zip file
        zip_path = os.path.join(target_dir, "chromedriver.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        # Remove the zip file
        os.remove(zip_path)
        
        # Make the ChromeDriver executable
        chromedriver_path = os.path.join(target_dir, "chromedriver")
        if platform.system() != "Windows":
            os.chmod(chromedriver_path, 0o755)
        
        logger.info(f"ChromeDriver installed successfully at: {chromedriver_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error installing ChromeDriver: {e}")
        return False

if __name__ == "__main__":
    # If run directly, install ChromeDriver
    success = download_and_install_chromedriver()
    sys.exit(0 if success else 1)
