import os
import shutil
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from googletrans import Translator
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from torch.cuda.amp import autocast
import easyocr

# Load the fine-tuned NLP model for ideology classification
model_path = "./fine_tuned_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Reverse label mapping
REVERSE_LABEL_MAP = {
    0: "Conservatism",
    1: "Socialism",
    2: "Anarchism",
    3: "Nationalism",
    4: "Fascism",
    5: "Feminism",
    6: "Green Ideology",
    7: "Islamism",
}

# Initialize the translator and OCR reader
translator = Translator()
reader = easyocr.Reader(["en", "tl"], gpu=True)

# Pretrained BLIP model initialization
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model_blip = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to("cuda")

# Define the ideologies
IDEOLOGIES = list(REVERSE_LABEL_MAP.values())


def extract_text(image_path):
    """Extract text from an image using EasyOCR."""
    result = reader.readtext(image_path)
    extracted_text = " ".join([item[1] for item in result])
    return extracted_text


def translate_text(text):
    """Translate text to English."""
    if not text.strip():
        return ""
    try:
        translated = translator.translate(text, dest="en")
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def generate_caption(image_path):
    """Generate a caption for the image using BLIP."""
    try:
        image = Image.open(image_path)
        inputs = processor(images=image, return_tensors="pt").to("cuda")
        with autocast("cuda"):
            out = model_blip.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        print(f"Caption generation error: {e}")
        return ""


def classify_image(text, caption):
    """Classify image based on text and caption using the fine-tuned NLP model."""
    combined_content = f"{text} {caption}"
    try:
        inputs = tokenizer(
            combined_content, return_tensors="pt", padding=True, truncation=True
        )
        outputs = model(**inputs)
        predicted_label = outputs.logits.argmax(dim=-1).item()
        return REVERSE_LABEL_MAP.get(predicted_label, "Unclassified")
    except Exception as e:
        print(f"Classification error: {e}")
        return "Unclassified"


def process_folder(folder_path):
    """Process images in the specified folder and classify them into subfolders."""
    # Create subfolders for ideologies
    for ideology in IDEOLOGIES:
        os.makedirs(os.path.join(folder_path, ideology), exist_ok=True)

    # List all image files in the folder
    image_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    for image_file in image_files:
        print(f"Processing: {os.path.basename(image_file)}")
        try:
            extracted_text = extract_text(image_file)
            translated_text = translate_text(extracted_text)
            caption = generate_caption(image_file)

            classification = classify_image(translated_text, caption)

            if classification != "Unclassified":
                destination_folder = os.path.join(folder_path, classification)
                shutil.move(image_file, destination_folder)
                print(f"Moved to {classification}: {os.path.basename(image_file)}")
            else:
                print(f"Could not classify: {os.path.basename(image_file)}")
        except Exception as e:
            print(f"Error processing {os.path.basename(image_file)}: {e}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path containing images: ").strip()
    if os.path.isdir(folder_path):
        process_folder(folder_path)
    else:
        print(f"The folder '{folder_path}' does not exist.")
