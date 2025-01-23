from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import warnings

# Suppress PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

# Load the fine-tuned model and tokenizer
model_path = "./fine_tuned_model_for_PoliticalIdeology"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Test data (replace this with your actual test dataset)
test_texts = [
    "Example text 1 related to Conservatism",
    "Example text 2 related to Socialism",
    # Add more test samples here...
]
test_labels = [
    0,
    1,
]  # Replace with the ground truth labels corresponding to the test_texts

# Perform predictions
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
inputs = tokenizer(test_texts, return_tensors="pt", padding=True, truncation=True).to(
    device
)
outputs = model(**inputs)
predictions = outputs.logits.argmax(dim=-1).cpu().numpy()

# Calculate metrics
accuracy = accuracy_score(test_labels, predictions)
precision, recall, f1, _ = precision_recall_fscore_support(
    test_labels, predictions, average="weighted", zero_division=1
)

# Print the results as numerical values
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
