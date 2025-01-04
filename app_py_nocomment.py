import os
import easyocr
from googletrans import Translator
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import matplotlib.pyplot as plt

analyzer = SentimentIntensityAnalyzer()


def extract_text_with_easyocr(image_path):
    reader = easyocr.Reader(["en", "tl"], gpu=False)
    result = reader.readtext(image_path)
    extracted_text = " ".join([item[1] for item in result])
    return extracted_text


def translate_text(text, target_language="en"):
    if not text.strip():
        return ""
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        print(f"Error during translation: {e}")
        return text


def generate_caption(image_path):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption


def analyze_sentiment(text):
    sentiment = analyzer.polarity_scores(text)
    compound_score = sentiment["compound"]
    return compound_score


def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)


def plot_sentiment(sentiments):
    plt.hist(sentiments, bins=20, edgecolor="black")
    plt.title("Sentiment Analysis")
    plt.xlabel("Sentiment Score")
    plt.ylabel("Frequency")
    plt.show()


def main():
    image_path = "path_to_image.jpg"
    text = extract_text_with_easyocr(image_path)
    translated_text = translate_text(text)
    caption = generate_caption(image_path)
    sentiment_score = analyze_sentiment(translated_text)
    data = {
        "Extracted Text": [text],
        "Translated Text": [translated_text],
        "Caption": [caption],
        "Sentiment Score": [sentiment_score],
    }
    save_to_excel(data, "output.xlsx")
    plot_sentiment([sentiment_score])


if __name__ == "__main__":
    main()
