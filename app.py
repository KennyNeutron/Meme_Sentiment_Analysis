import os
from flask import Flask, request, render_template, jsonify, send_from_directory
import easyocr
from googletrans import Translator
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import torch

app = Flask(__name__)

# Create an "uploads" directory if not exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize models
analyzer = SentimentIntensityAnalyzer()
reader = easyocr.Reader(["en", "tl"], gpu=True)
translator = Translator()
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to("cuda")


def extract_text(image_path):
    """Extract text from an image using EasyOCR"""
    result = reader.readtext(image_path)
    return " ".join([item[1] for item in result]) if result else ""


def translate_text(text):
    """Translate text to English"""
    if not text.strip():
        return ""
    try:
        return translator.translate(text, dest="en").text
    except Exception:
        return text  # Return original if translation fails


def generate_caption(image_path):
    """Generate a caption using BLIP"""
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt").to("cuda")
    with torch.no_grad():
        out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)


def analyze_sentiment(text):
    """Analyze sentiment using VADER"""
    scores = analyzer.polarity_scores(text)
    compound_score = scores["compound"]
    sentiment = (
        "Positive"
        if compound_score >= 0.05
        else "Negative" if compound_score <= -0.05 else "Neutral"
    )
    return {"sentiment": sentiment, "score": compound_score}


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

        # Process Image
        extracted_text = extract_text(image_path)
        translated_text = translate_text(extracted_text)
        image_caption = generate_caption(image_path)

        # Sentiment Analysis
        text_sentiment = analyze_sentiment(translated_text)
        caption_sentiment = analyze_sentiment(image_caption)

        # Overall Sentiment Calculation
        overall_score = text_sentiment["score"] + caption_sentiment["score"]
        overall_sentiment = (
            "Positive"
            if overall_score >= 0.05
            else "Negative" if overall_score <= -0.05 else "Neutral"
        )

        # Return results along with image path
        return jsonify(
            {
                "image_url": f"/uploads/{image.filename}",
                "extracted_text": extracted_text,
                "translated_text": translated_text,
                "image_caption": image_caption,
                "text_sentiment": text_sentiment["sentiment"],
                "caption_sentiment": caption_sentiment["sentiment"],
                "overall_sentiment": overall_sentiment,
            }
        )

    return render_template("index.html")


# Serve uploaded images
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
