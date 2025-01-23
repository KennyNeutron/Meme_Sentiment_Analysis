import time
import random
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from openpyxl import Workbook
from selenium.webdriver.chrome.options import Options

# Path to ChromeDriver executable
PATH = "C:\\Users\\PERSONAL\\Code\\freelance\\webscrape\\chromedriver.exe"

# Initialize the Service object for ChromeDriver
service = Service(PATH)

# Configure Selenium Chrome options
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--no-sandbox")  # Disable sandboxing

# Initialize the WebDriver
wd = webdriver.Chrome(service=service, options=options)

# URL result of the Google search for images
url = "https://www.google.com/search?sca_esv=360d606574466e04&sxsrf=ADLYWILa_9OWqCQbJkk0Vz46FSETa4Nizg:1733480521337&q=2016+philippine+election+memes&udm=2&fbs=AEQNm0Aa4sjWe7Rqy32pFwRj0UkWd8nbOJfsBGGB5IQQO6L3JzWreY9LW7LdGrLDAFqYDH3DF_waBUhtl7i7Xh3ndQb6ZWKSDV_r2AU5neHqHvRjnXwaKB762_BeXUbl07EHnDIyWy0TSpTslXqKHyEAIy5VFlgLyXeHzV3mB8kLfGbMBDDv1ON2u2gY8dbzqcIc5HSBR-zWzuh4mhTlsZ-emVTCWrWqPA&sa=X&ved=2ahUKEwi95cuV9pKKAxWks1YBHQ0UFTgQtKgLegQIFRAB&biw=1280&bih=632&dpr=1.5#vhid=BM9J-s7gWFjajM&vssid=mosaic"

# Open the URL
wd.get(url)

# Wait for images to load
time.sleep(3)

# Initialize set to store unique image URLs
image_urls = set()
max_images = 700  # Target number of images
skips = 0  # Number of skipped images
delay = 2  # Delay between clicks to avoid overloading

# Initialize Excel workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "Unique Image URLs"
ws.append(["Image URL"])

# Loop to collect unique image URLs
while len(image_urls) < max_images:
    thumbnails = wd.find_elements(By.CLASS_NAME, "YQ4gaf")
    print(f"Found {len(thumbnails)} thumbnails")
    
    for img in thumbnails[len(image_urls) + skips:max_images]:
        try:
            img.click()  # Click to open the full image
            time.sleep(delay)  # Wait for image to load
        except Exception as e:
            print(f"Error: {e}")
            continue

        # Try to find the image elements
        try:
            image_element = wd.find_element(By.CLASS_NAME, "sFlh5c") or \
                            wd.find_element(By.CLASS_NAME, "FyHeAf") or \
                            wd.find_element(By.CLASS_NAME, "iPVvYb")
        except Exception as e:
            print(f"Error finding image element: {e}")
            continue

        # Collect the image URL
        image_url = image_element.get_attribute('src')

        if image_url and 'http' in image_url:  # Ensure it's a valid URL
            if image_url not in image_urls:
                image_urls.add(image_url)  # Add unique image URL to set
                print(f"Found {len(image_urls)} unique images")
            else:
                skips += 1  # Skip if duplicate URL

        # Break if we've reached the target number of unique images
        if len(image_urls) >= max_images:
            break

    # Scroll down to load more images
    wd.execute_script("window.scrollBy(0,1000);")
    time.sleep(random.uniform(1, 3))  # Random delay for smoother scraping

# Save unique image URLs to Excel file
for url in image_urls:
    ws.append([url])

wb.save("unique_image_urls.xlsx")  # Save the workbook

# Close the WebDriver
wd.quit()
