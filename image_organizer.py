import os
import easyocr
import shutil
from PIL import Image
import re  # Add this import for regular expressions
import time

# Initialize EasyOCR reader
reader = easyocr.Reader(["en", "tl"], gpu=False)


def extract_text(image_path):
    """Extract text from an image using EasyOCR"""
    result = reader.readtext(image_path)
    # If result is not empty, return the text
    return " ".join([item[1] for item in result])


def is_understandable_text(extracted_text):
    """Check if the extracted text is understandable based on length and content"""
    # Trim the text and remove any extra spaces
    extracted_text = extracted_text.strip()

    # If the text is too short or contains mostly digits, we consider it "without text"
    if len(extracted_text) < 10 or re.match(r"^[\d\W_]+$", extracted_text):
        return False

    # Further checks: ensure there's at least one word that is not a number or symbol
    word_count = len(re.findall(r"\b\w+\b", extracted_text))  # Count words
    if word_count > 1:
        return True
    else:
        return False


def organize_images(folder_path):
    """Organize images in the folder based on whether they contain understandable text"""
    # Create directories for with and without text if they don't exist
    with_text_dir = os.path.join(folder_path, "with text")
    without_text_dir = os.path.join(folder_path, "without text")

    if not os.path.exists(with_text_dir):
        os.makedirs(with_text_dir)
    if not os.path.exists(without_text_dir):
        os.makedirs(without_text_dir)

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if the file is an image
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                # Try to open the image and extract text
                image = Image.open(file_path)
                extracted_text = extract_text(file_path)

                # Ensure the image is closed after processing
                image.close()

                # Check if the extracted text is understandable
                if is_understandable_text(extracted_text):
                    # Move the image to "with text" folder
                    shutil.move(
                        file_path, os.path.join(with_text_dir, filename)
                    )  # Move the file
                else:
                    # Move the image to "without text" folder
                    shutil.move(
                        file_path, os.path.join(without_text_dir, filename)
                    )  # Move the file

                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                time.sleep(1)  # Wait before retrying in case the file is locked

    print("Image organization completed.")


if __name__ == "__main__":
    folder_path = input("Enter the folder path to organize images: ").strip()

    if os.path.isdir(folder_path):
        organize_images(folder_path)
    else:
        print(f"The folder '{folder_path}' does not exist.")
