import os
import easyocr
from googletrans import Translator
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

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


# Function to calculate confidence level (as percentage)
def calculate_confidence(overall_score):
    # Calculate the confidence percentage and ensure it is capped between 50% and 100%
    confidence = (
        abs(overall_score) * 100
    )  # Absolute value of the overall sentiment score

    # If the confidence level is below 50%, set it to 50% (minimum threshold)
    if confidence < 50:
        confidence = 50

    return round(confidence, 2)  # Round to 2 decimal places


# Function to process all images in a folder and save results to Excel
def process_folder(folder_path):
    # Prepare a list to collect data for the Excel file
    results = []

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is an image (you can extend this list if needed)
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)

            print(f"Processing Image: {filename}")

            # Extract text using EasyOCR
            extracted_text = extract_text_with_easyocr(image_path)

            # Translate extracted text if it's in Tagalog (Filipino)
            translated_text = translate_text(
                extracted_text, "en"
            )  # Translate to English

            # Analyze sentiment of the translated text
            (
                sentiment_translated,
                neg_translated,
                neu_translated,
                pos_translated,
                score_translated,
            ) = analyze_sentiment(translated_text)

            # Generate a caption describing the image using BLIP
            image_caption = generate_caption(image_path)

            # Analyze sentiment of the image caption
            sentiment_caption, neg_caption, neu_caption, pos_caption, score_caption = (
                analyze_sentiment(image_caption)
            )

            # Calculate overall sentiment based on both scores (translated text + image caption)
            overall_score = score_translated + score_caption
            if overall_score >= 0.05:
                overall_sentiment = "Positive"
            elif overall_score <= -0.05:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"

            # Calculate confidence level as percentage
            confidence_level = calculate_confidence(overall_score)

            # Add data to the results list
            results.append(
                {
                    "File Name": filename,
                    "Extracted Text": extracted_text,
                    "Translated Text": translated_text,
                    "Text Sentiment": sentiment_translated,
                    "Image Caption": image_caption,
                    "Caption Sentiment": sentiment_caption,
                    "Overall Sentiment": overall_sentiment,
                    "Confidence": f"{confidence_level}%",  # Add % sign to confidence
                }
            )

            # Print separator (100 "#")
            print("\n" + "#" * 100 + "\n")

    # Save results to an Excel file
    if results:
        output_folder = os.path.join(os.path.dirname(folder_path), "results")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Convert the results to a DataFrame
        df = pd.DataFrame(results)

        # Create an Excel workbook and add the data
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Sentiment Analysis Results"

        # Add the column headers
        sheet.append(df.columns.tolist())

        # Fill the Excel sheet with the rows from the DataFrame
        for row in dataframe_to_rows(df, index=False, header=False):
            sheet.append(row)

        # Autofit columns based on content
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column name
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = max_length + 2
            sheet.column_dimensions[column].width = adjusted_width

        # Save the Excel workbook
        output_file = os.path.join(output_folder, "sentiment_analysis_results.xlsx")
        workbook.save(output_file)
        print(f"Results saved to {output_file}")
    else:
        print("No images found to process.")


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

            # Calculate confidence level as percentage
            confidence_level = calculate_confidence(overall_score)
            print(f"Confidence Level: {confidence_level}%")

        else:
            print(f"The file '{image_path}' does not exist.")

    else:
        print("Invalid choice! Please enter 'image' or 'folder'.")
