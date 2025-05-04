import os
import time
import logging
import requests
import subprocess
import platform
from PIL import Image
from io import BytesIO
from config.config import (
    DEFAULT_IMAGE_PATH,
    IMAGE_DOWNLOAD_PATH
)
import sys
# Add the parent directory of the current file to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ImageHandler:
    def __init__(self, temp_dir=IMAGE_DOWNLOAD_PATH):
        self.temp_dir = temp_dir
        self.default_dir = DEFAULT_IMAGE_PATH
        self.logger = logging.getLogger(__name__)
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(DEFAULT_IMAGE_PATH, exist_ok=True)

        # Initialize Google Image Scraper
        self.webdriver_path = os.path.join(os.path.dirname(__file__), 'webdriver', 'chromedriver')

        # Check if ChromeDriver exists
        if not os.path.exists(self.webdriver_path):
            self.logger.warning("ChromeDriver not found at: %s", self.webdriver_path)

            # Try to install ChromeDriver
            if self._install_chromedriver():
                self.logger.info("ChromeDriver installed successfully")
            else:
                self.logger.error("Failed to install ChromeDriver")
                self.webdriver_path = None

    def _install_chromedriver(self):
        """Attempt to install ChromeDriver"""
        try:
            # Check if chromedriver_installer.py exists
            installer_path = os.path.join(os.path.dirname(__file__), 'chromedriver_installer.py')
            if not os.path.exists(installer_path):
                self.logger.error("ChromeDriver installer not found")
                return False

            # Run the ChromeDriver installer
            self.logger.info("Attempting to install ChromeDriver...")
            result = subprocess.run([sys.executable, installer_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)

            if result.returncode == 0:
                self.logger.info("ChromeDriver installed successfully")
                return True
            else:
                self.logger.error(f"ChromeDriver installation failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Error installing ChromeDriver: {str(e)}")
            return False

    def search_google_images_with_selenium(self, search_query, num_images=5):
        """Search images using Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager

            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Initialize the Chrome driver with webdriver-manager
            self.logger.info("Initializing Chrome driver with webdriver-manager")

            # Get the driver path but don't use it directly
            driver_path = ChromeDriverManager().install()

            # Fix for macOS - make sure we're using the correct executable
            if platform.system() == "Darwin":
                # The driver_path might point to the wrong file, so let's find the actual executable
                driver_dir = os.path.dirname(driver_path)

                # Look for the actual chromedriver executable
                if "arm64" in platform.machine().lower():
                    # For Apple Silicon (M1/M2)
                    possible_paths = [
                        os.path.join(driver_dir, "chromedriver"),
                        os.path.join(driver_dir, "chromedriver-mac-arm64", "chromedriver"),
                        # Try parent directory
                        os.path.join(os.path.dirname(driver_dir), "chromedriver")
                    ]
                else:
                    # For Intel Macs
                    possible_paths = [
                        os.path.join(driver_dir, "chromedriver"),
                        os.path.join(driver_dir, "chromedriver-mac-x64", "chromedriver"),
                        # Try parent directory
                        os.path.join(os.path.dirname(driver_dir), "chromedriver")
                    ]

                # Find the first executable that exists
                for path in possible_paths:
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        driver_path = path
                        self.logger.info(f"Found executable ChromeDriver at: {driver_path}")
                        break

            # Use the corrected driver path
            self.logger.info(f"Using ChromeDriver at: {driver_path}")
            driver = webdriver.Chrome(
                service=Service(driver_path),
                options=chrome_options
            )

            # Set up the search URL
            search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
            self.logger.info(f"Searching Google Images with URL: {search_url}")

            # Navigate to the search URL
            driver.get(search_url)

            # Wait for the page to load
            import time
            time.sleep(2)

            # Find image elements
            from selenium.webdriver.common.by import By
            img_elements = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")

            # Get image URLs
            image_urls = []
            for i, img in enumerate(img_elements):
                if i >= num_images:
                    break

                try:
                    # Get the image source
                    img.click()
                    time.sleep(1)

                    # Find the larger image
                    large_img = driver.find_elements(By.CSS_SELECTOR, "img.r48jcc")
                    if large_img:
                        src = large_img[0].get_attribute("src")
                        if src and src.startswith("http"):
                            image_urls.append(src)
                            self.logger.info(f"Found image URL: {src}")
                except Exception as e:
                    self.logger.warning(f"Error getting image {i}: {str(e)}")
                    continue

            # Close the driver
            driver.quit()

            return image_urls

        except Exception as e:
            self.logger.error(f"Error in Selenium Google image search: {str(e)}")
            return []

    def search_google_images_with_requests(self, search_query, num_images=5):
        """Search images using requests (fallback method)"""
        try:
            # Set up headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            # Create the search URL
            search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
            self.logger.info(f"Searching Google Images with requests: {search_url}")

            # Make the request
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code != 200:
                self.logger.warning(f"Failed to get search results: {response.status_code}")
                return []

            # Extract image URLs using a simple regex pattern
            import re
            pattern = r'https://[^"\']+\.(jpg|jpeg|png|webp)'
            image_urls = re.findall(pattern, response.text)

            # Deduplicate and limit
            unique_urls = []
            for url in image_urls:
                if url not in unique_urls and len(unique_urls) < num_images:
                    if url.startswith("http"):
                        unique_urls.append(url)

            self.logger.info(f"Found {len(unique_urls)} image URLs with requests method")
            return unique_urls

        except Exception as e:
            self.logger.error(f"Error in requests Google image search: {str(e)}")
            return []

    def download_images(self, image_urls, search_dir):
        """Download images from URLs"""
        downloaded_paths = []

        for i, url in enumerate(image_urls):
            try:
                # Download the image
                response = requests.get(url, stream=True, timeout=10)
                if response.status_code == 200:
                    # Generate a filename
                    ext = "jpg"  # Default extension
                    if "image/png" in response.headers.get("Content-Type", ""):
                        ext = "png"
                    elif "image/jpeg" in response.headers.get("Content-Type", ""):
                        ext = "jpeg"
                    elif "image/webp" in response.headers.get("Content-Type", ""):
                        ext = "webp"

                    # Clean the search query for filename
                    clean_query = ''.join(c if c.isalnum() else '' for c in os.path.basename(search_dir))
                    filename = f"{clean_query}{i}.{ext}"
                    filepath = os.path.join(search_dir, filename)

                    # Save the image
                    with open(filepath, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    self.logger.info(f"Saved image to {filepath}")
                    downloaded_paths.append(filepath)
            except Exception as e:
                self.logger.warning(f"Error downloading image {i}: {str(e)}")
                continue

        return downloaded_paths

    def search_google_images(self, search_query, num_images=5):
        """Search images using Google Image Scraper with fallbacks"""
        if not self.webdriver_path:
            self.logger.warning("ChromeDriver not available, trying alternative methods")

        # Create a directory for the search results
        search_dir = os.path.join(self.temp_dir, search_query)
        os.makedirs(search_dir, exist_ok=True)

        # Try Selenium method first
        image_urls = self.search_google_images_with_selenium(search_query, num_images)

        # If Selenium method fails, try requests method
        if not image_urls:
            self.logger.info("Selenium method failed, trying requests method")
            image_urls = self.search_google_images_with_requests(search_query, num_images)

        # If we have image URLs, download them
        if image_urls:
            self.logger.info(f"Found {len(image_urls)} image URLs, downloading...")
            downloaded_paths = self.download_images(image_urls, search_dir)

            if downloaded_paths:
                return downloaded_paths

        # If all methods fail, use default images
        self.logger.warning("All image search methods failed, using default images")

        # Check if default images exist
        default_images = [os.path.join(self.default_dir, f) for f in os.listdir(self.default_dir)
                         if os.path.isfile(os.path.join(self.default_dir, f)) and
                         f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

        if default_images:
            # Copy default images to the search directory
            import shutil
            for i, img_path in enumerate(default_images[:num_images]):
                try:
                    dest_path = os.path.join(search_dir, f"default{i}{os.path.splitext(img_path)[1]}")
                    shutil.copy2(img_path, dest_path)
                    self.logger.info(f"Copied default image to {dest_path}")
                except Exception as e:
                    self.logger.warning(f"Error copying default image: {str(e)}")

            # Return paths to the copied default images
            return [os.path.join(search_dir, f) for f in os.listdir(search_dir)
                   if os.path.isfile(os.path.join(search_dir, f))]

        return []

    def search_and_download_images(self, topic, keywords, num_images=5):
        """Search and download images using Google Image Scraper"""
        try:
            search_query = f"{topic} {keywords}"
            self.logger.info(f"Searching for images with query: {search_query}")

            # Search for images using Google Image Scraper
            image_paths = self.search_google_images(search_query, num_images)

            if not image_paths:
                self.logger.warning("No images found from Google Images")
                return []

            return image_paths

        except Exception as e:
            self.logger.error(f"Error in image search: {str(e)}")
            return []

    def select_featured_image(self, images):
        """Select the most suitable image as featured image"""
        if not images:
            return None

        # For now, just return the first image
        # In a more sophisticated implementation, you could analyze images
        # to select the most suitable one based on size, aspect ratio, etc.
        return images[0]

    def cleanup(self):
        """Clean up resources"""
        try:
            # Clean up temporary files
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    self.logger.error(f"Error deleting file {file_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error in cleanup: {str(e)}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()