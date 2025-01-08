import os
import re
import bs4
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uuid
import base64
import gc
import hashlib

driver = webdriver.Chrome()


def scrap_web(search_url):
    driver.get(url=search_url)

    WebDriverWait(driver, timeout=10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.eA0Zlc"))
    )

    last_height = driver.execute_script("return document.body.scrollHeight")
    retry_count = 0  # To track retry attempts for clicking the "More Results" button

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")

        # If the page height hasn't changed, try to click the "More Results" button
        if new_height == last_height:
            try:
                # Attempt the first XPath
                try:
                    more_results_button = driver.find_element(
                        By.XPATH, '//*[@id="rso"]/div/div/div[2]/div[2]/div[4]/div[2]/a'
                    )
                except:
                    # If the first XPath fails, attempt the second XPath
                    more_results_button = driver.find_element(
                        By.XPATH,
                        '//*[@id="rso"]/div/div/div[2]/div[2]/div[4]/a[1]/h3/div',
                    )

                # If the button is visible, click it
                if more_results_button.is_displayed():
                    print("Clicking 'More Results' button")
                    more_results_button.click()
                    time.sleep(3)  # Wait for the next batch of results to load
                    retry_count = 0  # Reset retry count after a successful click
                else:
                    print("No 'More Results' button found or visible.")
                    break  # No more results to load
            except Exception as e:
                retry_count += 1
                print(f"Error while finding or clicking 'More Results' button: {e}")

                if retry_count >= 3:
                    print("Failed to click 'More Results' button 3 times. Stopping.")
                    break

                print(f"Retrying... ({retry_count}/3)")
                time.sleep(2)

        last_height = new_height

    page_html = driver.page_source
    page_soup = bs4.BeautifulSoup(page_html, features="html.parser")

    containers = page_soup.find_all(
        "div",
        {
            "class": "eA0Zlc WghbWd FnEtTd mkpRId m3LIae RLdvSe qyKxnc ivg-i PZPZlf GMCzAd"
        },
    )

    containers_length = len(containers)

    print(f"Found {containers_length} containers")

    driver.execute_script("window.scroll(0,0);")
    time.sleep(5)

    return containers_length


def get_img_links(containers_length):
    for i in range(1, containers_length + 1):
        x_path = f'//*[@id="rso"]/div/div/div[1]/div/div/div[{i}]'

        try:
            element = driver.find_element(By.XPATH, x_path)
            preview_img_element = element.find_element(By.TAG_NAME, "img")
            preview_img_url = preview_img_element.get_attribute("src")

            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()

            if str(preview_img_url).startswith("data:image/jpeg"):
                img_element = driver.find_element(By.TAG_NAME, "img")
                img_url = img_element.get_attribute("src")
                save_img(img_url)

            elif str(preview_img_url).startswith("data:image/url") or str(
                preview_img_url
            ).startswith("data:image/png"):
                continue

            else:
                img_url = preview_img_url
                start_time = time.time()

                while True:
                    img_x_path = f'//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]'
                    quality_img_element = driver.find_element(By.XPATH, img_x_path)
                    quality_img_url = quality_img_element.get_attribute("src")

                    if preview_img_url != quality_img_url:
                        img_url = quality_img_url
                        break

                    if time.time() - start_time >= 3:  # Reduced to 3 seconds wait time
                        print("Got Low res image, Skipping it")
                        break

                if img_url != preview_img_url:
                    save_img(img_url)
        except Exception as e:
            print(f"Error clicking an element: {e}")
            driver.execute_script("window.history.go(-1)")


def save_img(img):
    global img_count
    save_dir = "Scraper/img/scraped_images"
    os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists

    try:
        if img_count >= num_images:
            return

        # Check if the image is base64 encoded or a URL
        if str(img).startswith("data:image"):
            header, encoded = img.split(",", 1)
            ext = header.split(";")[0].split("/")[1]
            filename = f"image_{uuid.uuid4().hex[:8]}.{ext}"
            image_data = base64.b64decode(encoded)

            image_path = os.path.join(save_dir, filename)

            # Avoid duplication by checking if the image file already exists
            is_duplicate, unique_filename = check_duplicate(image_data, image_path)
            if not is_duplicate:
                with open(unique_filename, "wb") as f:
                    f.write(image_data)
                print(
                    f"Base64 image {img_count}/{num_images} saved as : {os.path.basename(unique_filename)}"
                )
                img_count += 1
            else:
                print(f"Duplicate image skipped: {os.path.basename(image_path)}")

        else:
            response = requests.get(
                img, timeout=5
            )  # Reduced timeout to 5 seconds for faster image retrieval
            response.raise_for_status()
            if response.status_code == 200:
                filename = extract_filename(img)

                if not filename:
                    filename = f"image_{uuid.uuid4().hex[:8]}.jpg"

                image_path = os.path.join(save_dir, filename)

                # Avoid duplication by checking if the image file already exists
                is_duplicate, unique_filename = check_duplicate(
                    response.content, image_path
                )
                if not is_duplicate:
                    with open(unique_filename, "wb") as f:
                        f.write(response.content)
                    print(
                        f"Image {img_count}/{num_images} saved as : {os.path.basename(unique_filename)}"
                    )
                    img_count += 1
                else:
                    print(f"Duplicate image skipped: {filename}")
            else:
                print("Failed to retrieve image")

    except Exception as e:
        print(f"Error saving image: {e}")

    gc.collect()


def check_duplicate(image_data, image_path):
    """
    Check if an image file already exists in the target directory
    by comparing the size and hash of the image.
    If an image has the same name but a different size, it renames the new file.
    """
    if os.path.exists(image_path):
        # Check the size first
        existing_file_size = os.path.getsize(image_path)
        new_image_size = len(image_data)

        # If the sizes don't match, handle the same name but different size case
        if existing_file_size != new_image_size:
            # Append a unique identifier (e.g., a UUID or timestamp) to the filename
            file_name, ext = os.path.splitext(image_path)
            unique_filename = f"{file_name}_{uuid.uuid4().hex[:8]}{ext}"
            print(
                f"Different size detected for {os.path.basename(image_path)}. Renaming new image to {os.path.basename(unique_filename)}"
            )
            return (
                False,
                unique_filename,
            )  # Return the new filename to save the image with a unique name

        # If the sizes match, check the hash
        with open(image_path, "rb") as f:
            existing_image_data = f.read()
            existing_image_hash = hashlib.md5(existing_image_data).hexdigest()
            new_image_hash = hashlib.md5(image_data).hexdigest()
            if existing_image_hash == new_image_hash:
                print(
                    f"Duplicate image skipped: {os.path.basename(image_path)} (same hash and size)"
                )
                return True, None  # Duplicate found
    return False, image_path  # No duplicate, use the original path


def extract_filename(img):
    filename = re.findall(pattern=r"/([^/]+\.(?:jpg|jpeg|png|gif))", string=img)
    if filename:
        return sanitize_file_name(filename[0])
    return filename


def sanitize_file_name(filename):
    sanitize_file_name = re.sub(pattern=r'[<>:"/\\|?*]', repl="", string=filename)
    name, ext = os.path.splitext(sanitize_file_name)
    if len(name) > 0:
        name = name[:5]
    while name and name[-1] in ["-", "_", "."]:
        name = name[:-1]
    return name + ext


if __name__ == "__main__":
    img_count = 0

    # url = "https://www.google.com/search?q=philippine+politician+memes&sca_esv=5571eca2e3b5ace7&udm=2&biw=2560&bih=1317&sxsrf=ADLYWIInjtburOMJD2jSmMjbzB0de0guAA%3A1735979563704&ei=K_J4Z5zSKsrb1e8Py9vw-A8&ved=0ahUKEwjck-3p09uKAxXKbfUHHcstHP8Q4dUDCBE&uact=5&oq=philippine+politician+memes&gs_lp=EgNpbWciG3BoaWxpcHBpbmUgcG9saXRpY2lhbiBtZW1lczIEECMYJzIHEAAYgAQYCkjMM1DdDljqL3AGeACQAQCYAXSgAfsLqgEEMC4xNLgBA8gBAPgBAZgCDqAC5AfCAgQQABgewgIGEAAYBxgewgIIEAAYBxgKGB6YAwCIBgGSBwM1LjmgB-8Q&sclient=img"
    url = input("Enter URL: ")

    len_containers = scrap_web(url)

    # num_images = int(input("Enter Number of Images: "))
    num_images = len_containers - 6
    print(f"Scraping {num_images} images")
    get_img_links(len_containers)

    if img_count >= num_images:
        print("Completed num images successfully")
    else:
        print("No sufficient number of images")

    driver.quit()
