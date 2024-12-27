import easyocr
from googletrans import Translator


def extract_text_with_easyocr(image_path):
    # Initialize EasyOCR reader with CPU (gpu=False)
    reader = easyocr.Reader(
        ["en", "tl"], gpu=False
    )  # Include Tagalog ('tl') for OCR recognition
    result = reader.readtext(image_path)

    # Extracting text from the result
    extracted_text = " ".join([item[1] for item in result])
    return extracted_text


def translate_text(text, target_language="en"):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text


# Example usage
image_path = "your_image.jpg"  # Replace with your image path
extracted_text = extract_text_with_easyocr(image_path)
print(f"Extracted Text: {extracted_text}")  # Corrected the string formatting

# Translate extracted text if it's in Tagalog (Filipino)
translated_text = translate_text(extracted_text, "en")  # Translate to English
print(f"Translated Text: {translated_text}")  # Corrected the string formatting
