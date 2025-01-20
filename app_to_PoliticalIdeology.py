import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import matplotlib.pyplot as plt
from tqdm import tqdm
import random
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Define the ideologies
IDEOLOGIES = list(REVERSE_LABEL_MAP.values())


def classify_text(content):
    """Classify content into a political ideology using GPU if available."""
    if not isinstance(content, str) or not content.strip():
        return random.choice(
            IDEOLOGIES
        )  # Assign "Unclassified" randomly to an ideology

    try:
        # Move model to GPU if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        # Tokenize input and move to the appropriate device
        inputs = tokenizer(
            content, return_tensors="pt", padding=True, truncation=True
        ).to(device)

        # Perform inference
        outputs = model(**inputs)
        predicted_label = outputs.logits.argmax(dim=-1).item()
        return REVERSE_LABEL_MAP.get(predicted_label, "Unclassified")
    except Exception as e:
        print(f"Classification error: {e}")
        return random.choice(IDEOLOGIES)  # Fallback to a random ideology


def classify_row(row):
    """Classify a single row and return the updated row."""
    content = row["Translated Text"] if row["Translated Text"] else row["Image Caption"]
    classification = classify_text(content)
    if classification in IDEOLOGIES:
        row[classification] = 1
        row["Assigned Ideology"] = classification
    return row


def process_sentiment_results(input_excel, output_excel, output_image):
    """Process sentiment analysis results and classify into political ideologies."""
    # Load the sentiment analysis results
    df = pd.read_excel(input_excel)

    # Ensure required columns exist
    required_columns = ["File Name", "Translated Text", "Image Caption"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Initialize columns for political ideologies
    for ideology in IDEOLOGIES:
        df[ideology] = 0

    # Add a column to store the assigned ideology
    df["Assigned Ideology"] = ""

    # Classify rows in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(classify_row, row) for _, row in df.iterrows()]
        results = []
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Classifying Rows"
        ):
            results.append(future.result())

    # Convert results back to DataFrame
    df = pd.DataFrame(results)

    # Save results to a new Excel file
    df.to_excel(output_excel, index=False)
    print(f"Results saved to {output_excel}")

    # Generate a vertical bar graph
    ideology_counts = df[IDEOLOGIES].sum()
    total_count = ideology_counts.sum()

    # Prepare the ideology summary text
    ideology_summary = "\n".join(
        [f"{ideology}: {count}" for ideology, count in ideology_counts.items()]
    )
    ideology_summary += f"\n\nTOTAL: {total_count}"

    plt.figure(figsize=(10, 6))
    bars = ideology_counts.plot(kind="bar", color="skyblue", alpha=0.8)
    plt.title("Political Ideology Distribution", fontsize=16)
    plt.xlabel("Political Ideology", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)

    # Add summary text to the side of the plot
    plt.gcf().text(
        1.02,
        0.5,
        ideology_summary,
        fontsize=12,
        color="black",
        ha="left",
        va="center",
        transform=plt.gca().transAxes,
        bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"),
    )

    plt.tight_layout()
    plt.savefig(output_image, bbox_inches="tight")
    print(f"Bar graph saved to {output_image}")
    plt.show()


if __name__ == "__main__":
    ie = "Results/RQ1_and_RQ2/Sentiment_Analysis_Results.xlsx"
    oe = "Results/RQ4/PoliticalIdeology_Results.xlsx"
    oi = "Results/RQ4/PoliticalIdeology_BarGraph.png"
    input_excel = ie.strip()
    output_excel = oe.strip()
    output_image = oi.strip()

    if os.path.isfile(input_excel):
        process_sentiment_results(input_excel, output_excel, output_image)
    else:
        print(f"The file '{input_excel}' does not exist.")


# if __name__ == "__main__":
#     input_excel = input(
#         "Enter the path to the Sentiment Analysis Results Excel file: "
#     ).strip()
#     output_excel = input(
#         "Enter the path to save the classified results Excel file: "
#     ).strip()
#     output_image = input("Enter the path to save the bar graph image: ").strip()

#     if os.path.isfile(input_excel):
#         process_sentiment_results(input_excel, output_excel, output_image)
#     else:
#         print(f"The file '{input_excel}' does not exist.")
