# EV Blog Automation Suite

An automated system for generating and publishing blog posts about electric vehicles to WordPress using AI, Google Sheets integration, and image processing.

![EV Blog Automation Suite](https://img.shields.io/badge/EV%20Blog-Automation%20Suite-blue)
![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Web Interface**: User-friendly interface for configuring and running the blog automation process
- **Google Sheets Integration**: Pull blog post data from a Google Sheet
- **AI-Powered Content**: Generate high-quality blog content using Ollama and Gemma
- **Image Search**: Automatically find and download relevant images
- **WordPress Publishing**: Publish posts directly to your WordPress site
- **Customizable**: Configure the number of images and article length

## Prerequisites

- Python 3.6 or higher
- Ollama with Gemma model installed (for AI content generation)
- Google Sheet with blog post data
- WordPress site with admin credentials

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/harshafau/blog-maker.git
   cd blog-maker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the setup script**:
   ```bash
   python3 setup.py
   ```
   This will:
   - Check your Python version
   - Install required dependencies
   - Create necessary directories
   - Install ChromeDriver for image scraping
   - Check for Ollama and Gemma model (optional)

4. **Install Ollama** (if not already installed):
   - Download from [ollama.ai/download](https://ollama.ai/download)
   - Install the Gemma model:
     ```bash
     ollama pull gemma3:latest
     ```

## Usage

1. **Start the web interface**:
   ```bash
   python3 run_web_interface.py
   ```
   This will open your browser to the web interface.

2. **Enter your configuration**:
   - **Google Sheet ID**: The ID from your Google Sheets URL
   - **WordPress URL**: Your WordPress site URL
   - **WordPress Username**: Your WordPress admin username
   - **WordPress Password**: Your WordPress admin password
   - **Number of Images**: Maximum number of images per post (default: 3)
   - **Article Length**: Target word count for generated articles (default: 1000)

3. **Click "Generate Articles"** to start the process

4. **Monitor the process** in the terminal output display

## Google Sheet Format

Your Google Sheet should have the following columns:
- **topic name**: The main topic of the blog post
- **title**: The title of the blog post
- **keywords**: Keywords to include in the content
- **context**: Additional context for the AI
- **must have elements**: Required elements (e.g., table, bullet points)
- **status**: Current status of the post

The Google Sheet must be publicly accessible for reading.

## Project Structure

- `run_web_interface.py`: Web interface entry point
- `web_interface.py`: Flask web application
- `main.py`: Command-line entry point
- `config/`: Configuration files
- `modules/`: Core functionality modules
- `static/`: Web interface assets (CSS, JavaScript)
- `templates/`: HTML templates for web interface
- `logs/`: Log files
- `temp/`: Temporary files (downloaded images, etc.)

## Troubleshooting

- **Import Errors**: Run `python3 setup.py` to install missing dependencies

- **SSL Certificate Issues** (macOS): If you see SSL certificate verification errors, run:
  ```bash
  python3 fix_ssl.py
  ```
  This will install the necessary certificates for SSL verification.

- **ChromeDriver Issues**: If image scraping doesn't work, try reinstalling ChromeDriver:
  ```bash
  python3 modules/chromedriver_installer.py
  ```

- **Chrome Version Mismatch**: If you see "This version of ChromeDriver only supports Chrome version X" errors, run:
  ```bash
  pip install webdriver-manager
  python3 modules/chromedriver_installer.py
  ```
  This will download the correct ChromeDriver version for your Chrome browser.

- **Ollama Connection Issues**: Make sure Ollama is running with `ollama serve`

- **Google Sheet Access**: Ensure your Google Sheet is publicly accessible

- **WordPress Connection**: Verify your WordPress credentials and URL
  - Make sure your WordPress URL includes the protocol (http:// or https://)
  - Check that your username and password are correct

- **Image Scraping Errors**: If you see "ChromeDriver not found" errors, the automatic installation may have failed. Try installing ChromeDriver manually from [chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads) and place it in the `modules/webdriver/` directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Ollama for providing the AI model infrastructure
- Google Sheets API for data management
- WordPress API for publishing integration