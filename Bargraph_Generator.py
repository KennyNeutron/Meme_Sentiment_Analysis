import pandas as pd
import matplotlib.pyplot as plt


def generate_sentiment_bargraph(excel_file_path, output_image_path):
    """
    Generates a bar graph of sentiment counts (Positive, Neutral, Negative) from an Excel file.

    Args:
        excel_file_path (str): Path to the Excel file containing sentiment analysis results.
        output_image_path (str): Path to save the generated bar graph image.
    """
    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(excel_file_path)

        # Ensure the "Overall Sentiment" column exists
        if "Overall Sentiment" not in df.columns:
            raise ValueError(
                "The column 'Overall Sentiment' is missing in the Excel file."
            )

        # Count occurrences of each sentiment
        sentiment_counts = df["Overall Sentiment"].value_counts()

        # Create the bar graph
        plt.figure(figsize=(8, 6))
        bars = sentiment_counts.plot(
            kind="bar", color=["gray", "green", "red"], alpha=0.7
        )
        plt.title("Sentiment Analysis Distribution", fontsize=14)
        plt.xlabel("Sentiment", fontsize=12)
        plt.ylabel("Count", fontsize=12)
        plt.xticks(rotation=0)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Add a text box with sentiment counts on the right side of the graph
        sentiment_text = "\n".join(
            [f"{sentiment} = {count}" for sentiment, count in sentiment_counts.items()]
        )
        plt.text(
            1.05,
            0.5,
            sentiment_text,
            fontsize=12,
            color="black",
            transform=plt.gca().transAxes,
            verticalalignment="center",
            horizontalalignment="left",
            bbox=dict(
                boxstyle="round,pad=0.3",
                edgecolor="black",
                facecolor="white",
                alpha=0.8,
            ),
        )

        # Save the graph as an image
        plt.savefig(output_image_path, bbox_inches="tight")
        print(f"Bar graph saved at: {output_image_path}")

        # Show the graph (optional)
        plt.show()

    except Exception as e:
        print(f"Error generating bar graph: {e}")


if __name__ == "__main__":
    # Example usage
    excel_file = input("Enter the path to the Excel file: ").strip()
    output_image = input("Enter the path to save the bar graph image: ").strip()
    generate_sentiment_bargraph(excel_file, output_image)
