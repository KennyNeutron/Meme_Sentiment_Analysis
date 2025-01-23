from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load the fine-tuned model
model_path = "./fine_tuned_model_for_PoliticalIdeology"
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
    8: "Liberalism",
}

# Ask user for input text
text = input("Enter a text to classify: ").strip()
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
outputs = model(**inputs)

# Get predicted label and corresponding ideology
predicted_label = outputs.logits.argmax(dim=-1).item()
ideology = REVERSE_LABEL_MAP.get(predicted_label, "Unknown")

print(f"Text: {text}")
print(f"Predicted Label: {predicted_label}")
print(f"Political Ideology: {ideology}")
