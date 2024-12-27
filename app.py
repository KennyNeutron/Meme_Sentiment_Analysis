import os
import easyocr
from googletrans import Translator
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


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


def generate_caption(image_path):
    # Load BLIP model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )

    # Open the image
    image = Image.open(image_path)

    # Preprocess the image and generate the caption
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)

    # Decode and return the caption
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption


# Function to analyze sentiment using VADER and return the actual sentiment
def analyze_sentiment(text):
    # Get the sentiment scores
    sentiment = analyzer.polarity_scores(text)
    compound_score = sentiment["compound"]

    # Determine sentiment based on compound score
    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    return (
        sentiment_label,
        sentiment["neg"],
        sentiment["neu"],
        sentiment["pos"],
        compound_score,
    )


# Function to process all images in a folder
def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        # Check if the file is an image (you can extend this list if needed)
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)

            print(f"Processing Image: {filename}")

            # Extract text using EasyOCR
            extracted_text = extract_text_with_easyocr(image_path)
            print(f"Extracted Text: {extracted_text}")

            # Translate extracted text if it's in Tagalog (Filipino)
            translated_text = translate_text(
                extracted_text, "en"
            )  # Translate to English
            print(f"Translated Text: {translated_text}")

            # Analyze sentiment of the translated text
            (
                sentiment_translated,
                neg_translated,
                neu_translated,
                pos_translated,
                score_translated,
            ) = analyze_sentiment(translated_text)
            print(
                f"Sentiment of Translated Text: {sentiment_translated} (neg={neg_translated}, neu={neu_translated}, pos={pos_translated}, Score: {score_translated})"
            )

            # Generate a caption describing the image using BLIP
            image_caption = generate_caption(image_path)
            print(
                f"Image Caption: {image_caption}"
            )  # Print the generated description of the image

            # Analyze sentiment of the image caption
            sentiment_caption, neg_caption, neu_caption, pos_caption, score_caption = (
                analyze_sentiment(image_caption)
            )
            print(
                f"Sentiment of Image Caption: {sentiment_caption} (neg={neg_caption}, neu={neu_caption}, pos={pos_caption}, Score: {score_caption})"
            )

            # Calculate overall sentiment based on both scores (translated text + image caption)
            overall_score = score_translated + score_caption
            if overall_score >= 0.05:
                overall_sentiment = "Positive"
            elif overall_score <= -0.05:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"

            print(f"Overall Sentiment: {overall_sentiment} (Score: {overall_score})")

            # Print separator (now 100 "#")
            print("\n" + "#" * 100 + "\n")


# Main function to handle user input
if __name__ == "__main__":
    choice = (
        input(
            "Do you want to process a specific image or a folder? (Enter 'image' or 'folder'): "
        )
        .strip()
        .lower()
    )

    if choice == "folder":
        folder_path = input("Enter the folder path: ").strip()
        if os.path.isdir(folder_path):
            process_folder(folder_path)
        else:
            print(f"The folder '{folder_path}' does not exist.")

    elif choice == "image":
        image_path = input("Enter the image file path: ").strip()
        if os.path.isfile(image_path):
            # Process the specific image
            print(f"Processing Image: {image_path}")

            # Extract text using EasyOCR
            extracted_text = extract_text_with_easyocr(image_path)
            print(f"Extracted Text: {extracted_text}")

            # Translate extracted text if it's in Tagalog (Filipino)
            translated_text = translate_text(
                extracted_text, "en"
            )  # Translate to English
            print(f"Translated Text: {translated_text}")

            # Analyze sentiment of the translated text
            (
                sentiment_translated,
                neg_translated,
                neu_translated,
                pos_translated,
                score_translated,
            ) = analyze_sentiment(translated_text)
            print(
                f"Sentiment of Translated Text: {sentiment_translated} (neg={neg_translated}, neu={neu_translated}, pos={pos_translated}, Score: {score_translated})"
            )

            # Generate a caption describing the image using BLIP
            image_caption = generate_caption(image_path)
            print(
                f"Image Caption: {image_caption}"
            )  # Print the generated description of the image

            # Analyze sentiment of the image caption
            sentiment_caption, neg_caption, neu_caption, pos_caption, score_caption = (
                analyze_sentiment(image_caption)
            )
            print(
                f"Sentiment of Image Caption: {sentiment_caption} (neg={neg_caption}, neu={neu_caption}, pos={pos_caption}, Score: {score_caption})"
            )

            # Calculate overall sentiment based on both scores (translated text + image caption)
            overall_score = score_translated + score_caption
            if overall_score >= 0.05:
                overall_sentiment = "Positive"
            elif overall_score <= -0.05:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"

            print(f"Overall Sentiment: {overall_sentiment} (Score: {overall_score})")

        else:
            print(f"The file '{image_path}' does not exist.")

    else:
        print("Invalid choice! Please enter 'image' or 'folder'.")
