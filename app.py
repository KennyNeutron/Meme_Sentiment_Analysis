import os
from flask import Flask, request, render_template, jsonify, send_from_directory
import easyocr
from googletrans import Translator
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch
import random

app = Flask(__name__)

# Create an "uploads" directory if not exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize sentiment analysis models
analyzer = SentimentIntensityAnalyzer()
reader = easyocr.Reader(["en", "tl"], gpu=True)
translator = Translator()
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to("cuda")

# Political Ideology & Affiliation Integration
IDEOLOGY_TO_AFFILIATION = {
    "Conservatism": ["PDP-Laban", "Nacionalista Party"],
    "Socialism": ["Liberal Party", "Aksyon Demokratiko"],
    "Anarchism": ["Bagumbayan-VNP", "PRP"],
    "Nationalism": ["PDP-Laban", "Nacionalista Party", "National People's Coalition"],
    "Fascism": ["United Nationalist Alliance", "PDP-Laban"],
    "Feminism": ["Liberal Party"],
    "Green Ideology": ["Aksyon Demokratiko", "Bagumbayan-VNP"],
    "Islamism": ["Lakas-CMD"],
    "Liberalism": ["Liberal Party", "Aksyon Demokratiko", "PFP"],
}

# Load Political Ideology Model
MODEL_NAME = "fine_tuned_model_for_PoliticalIdeology"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
ideology_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(
    "cuda"
)

IDEOLOGY_LABELS = {
    0: "Conservatism",
    1: "Socialism",
    2: "Anarchism",
    3: "Nationalism",
    4: "Fascism",
    5: "Feminism",
    6: "Green Ideology",
    7: "Islamism",
    8: "Liberalism",
}


# Functions for Sentiment Analysis
def extract_text(image_path):
    result = reader.readtext(image_path)
    return " ".join([item[1] for item in result]) if result else ""


def translate_text(text):
    if not text.strip():
        return ""
    try:
        return translator.translate(text, dest="en").text
    except Exception:
        return text


def generate_caption(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt").to("cuda")
    with torch.no_grad():
        out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)


def analyze_sentiment(text):
    scores = analyzer.polarity_scores(text)
    compound_score = scores["compound"]
    sentiment = (
        "Positive"
        if compound_score >= 0.05
        else "Negative" if compound_score <= -0.05 else "Neutral"
    )
    return {"sentiment": sentiment, "score": compound_score}


# Functions for Ideology and Affiliation
def predict_ideology(text):
    if not text.strip():
        return "Unclassified"
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(
        "cuda"
    )
    with torch.no_grad():
        outputs = ideology_model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=1).item()
    return IDEOLOGY_LABELS.get(predictions, "Unclassified")


def map_affiliation(ideology):
    if ideology == "Unclassified":
        all_affiliations = [
            affil for affils in IDEOLOGY_TO_AFFILIATION.values() for affil in affils
        ]
        return random.choice(all_affiliations)
    return random.choice(IDEOLOGY_TO_AFFILIATION.get(ideology, ["Unclassified"]))


# Main Route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "image" not in request.files:
            return jsonify({"error": "No file uploaded"})

        image = request.files["image"]
        if image.filename == "":
            return jsonify({"error": "No selected file"})

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
        image.save(image_path)

        # Sentiment Analysis
        extracted_text = extract_text(image_path)
        translated_text = translate_text(extracted_text)
        image_caption = generate_caption(image_path)
        text_sentiment = analyze_sentiment(translated_text)
        caption_sentiment = analyze_sentiment(image_caption)

        # Overall Sentiment Calculation
        overall_score = text_sentiment["score"] + caption_sentiment["score"]
        overall_sentiment = (
            "Positive"
            if overall_score >= 0.05
            else "Negative" if overall_score <= -0.05 else "Neutral"
        )

        # Political Ideology & Affiliation Prediction
        ideology = predict_ideology(translated_text + " " + image_caption)
        affiliation = map_affiliation(ideology)

        # Response
        return jsonify(
            {
                "image_url": f"/uploads/{image.filename}",
                "extracted_text": extracted_text,
                "translated_text": translated_text,
                "image_caption": image_caption,
                "text_sentiment": text_sentiment["sentiment"],
                "caption_sentiment": caption_sentiment["sentiment"],
                "overall_sentiment": overall_sentiment,
                "predicted_ideology": ideology,
                "political_affiliation": affiliation,
            }
        )

    return render_template("index.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
