import os
import time
import logging
import requests
import subprocess
from PIL import Image
from io import BytesIO
from config.config import (
    DEFAULT_IMAGE_PATH,
    IMAGE_DOWNLOAD_PATH
)
import sys
# Add the parent directory of the current file to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .GoogleImageScraper import GoogleImageScraper

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

    def search_google_images(self, search_query, num_images=5):
        """Search images using Google Image Scraper"""
        if not self.webdriver_path:
            self.logger.warning("ChromeDriver not available, skipping Google Images search")
            return []

        # Create a directory for the search results
        search_dir = os.path.join(self.temp_dir, search_query)
        os.makedirs(search_dir, exist_ok=True)

        # Use a more reliable approach with webdriver-manager
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
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
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

            # Download the images
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
                        clean_query = ''.join(c if c.isalnum() else '' for c in search_query)
                        filename = f"{clean_query}{i}.{ext}"
                        filepath = os.path.join(search_dir, filename)

                        # Save the image
                        with open(filepath, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        self.logger.info(f"Saved image to {filepath}")
                except Exception as e:
                    self.logger.warning(f"Error downloading image {i}: {str(e)}")
                    continue

            # Get the saved image paths
            if not os.path.exists(search_dir):
                return []

            # Accept all image files
            return [os.path.join(search_dir, f)
                   for f in os.listdir(search_dir)
                   if os.path.isfile(os.path.join(search_dir, f))]

        except Exception as e:
            self.logger.error(f"Error in Google image search: {str(e)}")
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