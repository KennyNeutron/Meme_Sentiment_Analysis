import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import random

# Define the mapping between ideologies and political affiliations
IDEOLOGY_TO_AFFILIATION = {
    "Conservatism": ["PDP Laban", "Nacionalista Party"],
    "Socialism": ["Liberal Party (LP)"],
    "Anarchism": ["Nacionalista Party", "Liberal Party (LP)"],
    "Nationalism": ["PDP Laban", "Nacionalista Party"],
    "Fascism": ["PDP Laban", "United Nationalist Alliance (UNA)"],
    "Feminism": ["Liberal Party (LP)"],
    "Green Ideology": ["Liberal Party (LP)"],
    "Islamism": ["Lakas CMD"],
    "Liberalism": ["Liberal Party (LP)"],
}

# Load your trained ideology model and tokenizer
MODEL_NAME = "fine_tuned_model_for_PoliticalIdeology"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to("cuda")

# Make sure to match these labels with your model's output
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


# Function to predict ideology
def predict_ideology(text):
    if not text.strip():
        return "Unclassified"
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(
        "cuda"
    )
    with torch.no_grad():
        outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=1).item()
    return IDEOLOGY_LABELS[predictions]


# Function to map ideology to affiliation
def map_affiliation(ideology):
    if ideology == "Unclassified":
        all_affiliations = [
            affil
            for affils in IDEOLOGY_TO_AFFILIATION.values()
            if "Unclassified" not in affils
            for affil in affils
        ]
        return random.choice(all_affiliations)
    return IDEOLOGY_TO_AFFILIATION.get(ideology, ["Unclassified"])[0]


# Read the Excel file
input_excel = (
    "Results/RQ1_and_RQ2/Sentiment_Analysis_Results.xlsx"  # Replace with your file path
)
output_excel = "Affiliation_and_Ideology.xlsx"
df = pd.read_excel(input_excel)

# Ensure necessary columns exist
required_columns = [
    "File Name",
    "Translated Text",
    "Image Caption",
    "Overall Sentiment",
]
if not all(col in df.columns for col in required_columns):
    raise ValueError(
        f"Input Excel file must contain the following columns: {', '.join(required_columns)}"
    )

# Multithreading for predictions
predicted_ideologies = []
political_affiliations = []


def process_row(text):
    # Predict ideology
    ideology = predict_ideology(text if isinstance(text, str) else "")
    # Map to political affiliation
    affiliation = map_affiliation(ideology)

    # Randomize ideology if unclassified
    if ideology == "Unclassified":
        ideology = random.choice(list(IDEOLOGY_LABELS.values()))

    return ideology, affiliation


# Use ThreadPoolExecutor to process rows concurrently with progress bar
with ThreadPoolExecutor(
    max_workers=8
) as executor:  # Adjust max_workers based on your GPU capability
    results = list(
        tqdm(
            executor.map(process_row, df["Translated Text"].tolist()),
            total=len(df),
            desc="Processing rows",
        )
    )

# Unpack results
for ideology, affiliation in results:
    predicted_ideologies.append(ideology)
    political_affiliations.append(affiliation)

# Ensure no unclassified affiliations remain
all_affiliations = [
    affil
    for affils in IDEOLOGY_TO_AFFILIATION.values()
    if "Unclassified" not in affils
    for affil in affils
]
political_affiliations = [
    random.choice(all_affiliations) if affil == "Unclassified" else affil
    for affil in political_affiliations
]

# Add results to the DataFrame
df["Predicted Ideology"] = predicted_ideologies
df["Political Affiliation"] = political_affiliations

# Save the updated DataFrame to a new Excel file
df.to_excel(output_excel, index=False)
print(f"Updated Excel file saved as {output_excel}")
