from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset, Dataset
import pandas as pd

# Label mapping
LABEL_MAP = {
    "Conservatism": 0,
    "Socialism": 1,
    "Anarchism": 2,
    "Nationalism": 3,
    "Fascism": 4,
    "Feminism": 5,
    "Green Ideology": 6,
    "Islamism": 7,
}


# Load the dataset
def load_data(file_path):
    """Load the CSV dataset and convert it into a Hugging Face Dataset."""
    df = pd.read_csv(file_path)
    df["label"] = df["label"].map(LABEL_MAP)  # Map string labels to integers
    dataset = Dataset.from_pandas(df)
    return dataset


# Tokenize the data
def tokenize_function(example, tokenizer):
    """Tokenize the input text."""
    return tokenizer(
        example["text"], padding="max_length", truncation=True, max_length=128
    )


def train_model(dataset_path, output_dir="./fine_tuned_model"):
    """Train a transformer model for political ideology classification."""
    # Load dataset
    dataset = load_data(dataset_path)

    # Split into train and test
    dataset = dataset.train_test_split(test_size=0.2)
    train_dataset = dataset["train"]
    test_dataset = dataset["test"]

    # Load tokenizer and model
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=8)

    # Tokenize datasets
    train_dataset = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer), batched=True
    )
    test_dataset = test_dataset.map(
        lambda x: tokenize_function(x, tokenizer), batched=True
    )

    # Remove unnecessary columns
    train_dataset = train_dataset.remove_columns(["text"])
    test_dataset = test_dataset.remove_columns(["text"])

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",  # Updated from evaluation_strategy
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch",
        logging_dir="./logs",
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
    )

    # Define evaluation metrics
    def compute_metrics(eval_pred):
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support

        logits, labels = eval_pred
        predictions = logits.argmax(axis=-1)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average="weighted"
        )
        acc = accuracy_score(labels, predictions)
        return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

    # Create Trainer instance
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # Train the model
    trainer.train()

    # Save the fine-tuned model
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}")


if __name__ == "__main__":
    dataset_path = input("Enter the path to the dataset CSV file: ").strip()
    output_dir = (
        input(
            "Enter the directory to save the fine-tuned model (default: ./fine_tuned_model): "
        ).strip()
        or "./fine_tuned_model"
    )

    if not dataset_path or not dataset_path.endswith(".csv"):
        print("Invalid dataset path. Please provide a valid CSV file.")
    else:
        train_model(dataset_path, output_dir)
