#!/usr/bin/env python3
"""
Setup script for EV Blog Automation Suite

This script checks for required dependencies and installs them if needed.
It also downloads and installs ChromeDriver for web scraping.
"""

import os
import sys
import subprocess
import platform
import importlib.util

def check_python_version():
    """Check if Python version is 3.6 or higher"""
    required_version = (3, 6)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current Python version: {current_version[0]}.{current_version[1]}")
        return False
    return True

def check_pip():
    """Check if pip is installed"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        print("Error: pip is not installed or not working properly.")
        return False

def fix_ssl_certificates():
    """Fix SSL certificate verification on macOS"""
    if platform.system() != "Darwin":
        return True

    print("Checking SSL certificate verification for macOS...")

    try:
        # Install certifi
        subprocess.run([sys.executable, "-m", "pip", "install", "certifi"],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      text=True)

        # Try to import certifi
        try:
            import certifi
            print(f"Using certificates from: {certifi.where()}")
            return True
        except ImportError:
            print("Could not import certifi. SSL verification may fail.")
            return False
    except Exception as e:
        print(f"Error fixing SSL certificates: {e}")
        return False

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")

    # Fix SSL certificates first (for macOS)
    if platform.system() == "Darwin":
        fix_ssl_certificates()

    try:
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

        # Install certifi separately (important for SSL verification)
        subprocess.run([sys.executable, "-m", "pip", "install", "certifi"],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      text=True)

        print("All required packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed"""
    system = platform.system()

    if system == "Windows":
        ollama_cmd = "where ollama"
    else:  # Linux or macOS
        ollama_cmd = "which ollama"

    try:
        subprocess.check_call(ollama_cmd, shell=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        print("Ollama is installed.")
        return True
    except subprocess.CalledProcessError:
        print("Warning: Ollama is not installed or not in PATH.")
        print("The EV Blog Automation Suite requires Ollama for content generation.")
        print("Please install Ollama from: https://ollama.ai/download")
        return False

def check_gemma_model():
    """Check if Gemma model is available in Ollama"""
    try:
        result = subprocess.run(["ollama", "list"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

        if "gemma" in result.stdout.lower():
            print("Gemma model is available in Ollama.")
            return True
        else:
            print("Warning: Gemma model is not available in Ollama.")
            print("The EV Blog Automation Suite requires the Gemma model for content generation.")
            print("You can install it with: ollama pull gemma3:latest")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If Ollama is not installed, we already warned about it
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "temp/images", "templates", "static/css", "static/js", "modules/webdriver"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print("Created necessary directories.")
    return True

def install_chromedriver():
    """Download and install ChromeDriver"""
    print("Checking for ChromeDriver...")

    # Check if chromedriver_installer.py exists
    installer_path = os.path.join("modules", "chromedriver_installer.py")
    if not os.path.exists(installer_path):
        print("Error: ChromeDriver installer not found.")
        return False

    try:
        # Run the ChromeDriver installer
        print("Installing ChromeDriver...")
        result = subprocess.run([sys.executable, installer_path],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

        if result.returncode == 0:
            print("ChromeDriver installed successfully!")
            return True
        else:
            print(f"Warning: ChromeDriver installation failed: {result.stderr}")
            print("You may need to manually install ChromeDriver for image scraping to work.")
            print("Visit: https://chromedriver.chromium.org/downloads")
            return False
    except Exception as e:
        print(f"Error installing ChromeDriver: {e}")
        print("You may need to manually install ChromeDriver for image scraping to work.")
        return False

def main():
    """Main setup function"""
    print("Setting up EV Blog Automation Suite...")

    # Check Python version
    if not check_python_version():
        return False

    # Check pip
    if not check_pip():
        return False

    # Install requirements
    if not install_requirements():
        return False

    # Create directories
    if not create_directories():
        return False

    # Install ChromeDriver
    chromedriver_installed = install_chromedriver()
    if not chromedriver_installed:
        print("Warning: ChromeDriver installation failed. Image scraping may not work.")
        print("You can try installing it manually later.")

    # Check Ollama (optional)
    ollama_installed = check_ollama()

    # Check Gemma model (optional)
    if ollama_installed:
        check_gemma_model()

    print("\nSetup completed successfully!")
    print("\nTo run the EV Blog Automation Suite, use:")
    print("  python3 run_web_interface.py")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
