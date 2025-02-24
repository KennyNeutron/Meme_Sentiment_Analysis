import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import numpy as np

# Define mapping of affiliations to abbreviations
AFFILIATION_MAP = {
    "PDP-Laban": "PDP",
    "Lakas-CMD": "LKM",
    "Liberal Party": "LP",
    "Nacionalista Party": "NP",
    "National People's Coalition": "NPC",
    "United Nationalist Alliance": "UNA",
    "Aksyon Demokratiko": "AD",
    "PFP": "PFP",
    "Bagumbayan-VNP": "BVNP",
    "PRP": "PRP",
}

# Reverse mapping for easier lookup
ABBREVIATION_MAP = {abbr: full for full, abbr in AFFILIATION_MAP.items()}

# Predefined sentiment order for consistency
SENTIMENT_ORDER = ["Negative", "Neutral", "Positive"]

# Step 1: Ask for the input Excel file
input_file = input("Enter the path to the input Excel file: ").strip()
df = pd.read_excel(input_file)

# Step 2: Ask if analyzing ideology or affiliation
analysis_choice = input(
    "\nWhat would you like to analyze? (1 for Political Ideology, 2 for Political Affiliation): "
).strip()

# Case 1: Ideology Analysis
if analysis_choice == "1":
    print("\nAnalyzing Political Ideology...")
    counts = df["Predicted Ideology"].value_counts()

    # Plot bar graph
    plt.figure(figsize=(10, 6))
    bars = plt.bar(counts.index, counts.values, color="blue", alpha=0.8)
    for bar in bars:
        count = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            count,
            f"{count:,}",
            ha="center",
            va="bottom",
        )
    plt.title("Political Ideology Distribution")
    plt.xlabel("Ideology")
    plt.ylabel("Number of Memes")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    output_file = input(
        "Enter the path to save the ideology bar graph (e.g., output.png): "
    ).strip()
    plt.savefig(output_file, bbox_inches="tight")
    print(f"Ideology bar graph saved as {output_file}")

# Case 2: Affiliation Analysis
elif analysis_choice == "2":
    print("\nAnalyzing Political Affiliation...")
    print("\nAvailable affiliations:")
    for full, abbr in AFFILIATION_MAP.items():
        print(f"{abbr} - {full}")
    print("ALL - Analyze all affiliations")

    selected_abbreviation = (
        input(
            "\nEnter the abbreviation for the affiliation to report (or ALL for all affiliations): "
        )
        .strip()
        .upper()
    )

    # Case 2.1: All Affiliations
    if selected_abbreviation == "ALL":
        counts = df["Political Affiliation"].value_counts()

        # Plot bar graph
        plt.figure(figsize=(10, 6))
        bars = plt.bar(counts.index, counts.values, color="purple", alpha=0.8)
        for bar in bars:
            count = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                count,
                f"{count:,}",
                ha="center",
                va="bottom",
            )
        plt.title("Political Affiliation Distribution")
        plt.xlabel("Affiliation")
        plt.ylabel("Number of Memes")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        output_file = input(
            "Enter the path to save the affiliation bar graph (e.g., output.png): "
        ).strip()
        plt.savefig(output_file, bbox_inches="tight")
        print(f"Affiliation bar graph saved as {output_file}")

    # Case 2.2: Specific Affiliation
    elif selected_abbreviation in ABBREVIATION_MAP:
        selected_affiliation = ABBREVIATION_MAP[selected_abbreviation]
        filtered_df = df[df["Political Affiliation"] == selected_affiliation]
        if filtered_df.empty:
            raise ValueError(
                f"No data found for the affiliation '{selected_affiliation}'."
            )

        # Sentiment Distribution
        counts = filtered_df["Overall Sentiment"].value_counts()
        counts = counts.reindex(SENTIMENT_ORDER, fill_value=0)

        # Plot sentiment distribution
        plt.figure(figsize=(10, 6))
        bars = plt.bar(
            counts.index, counts.values, color=["red", "gray", "green"], alpha=0.8
        )
        for bar in bars:
            count = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                count,
                f"{count:,}",
                ha="center",
                va="bottom",
            )
        plt.title(f"Sentiment Distribution for {selected_affiliation}")
        plt.xlabel("Sentiment")
        plt.ylabel("Count")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        output_file = input(
            "Enter the path to save the sentiment distribution graph (e.g., output.png): "
        ).strip()
        plt.savefig(output_file, bbox_inches="tight")
        print(f"Sentiment distribution graph saved as {output_file}")

        # Perform ANOVA (Unchanged)
        # ... (Rest of the ANOVA and Tukey HSD code remains the same)
        # Perform Tukey HSD if possible
        if all(
            counts[sentiment] > 1 for sentiment in SENTIMENT_ORDER
        ):  # Ensure each group has more than one sample
            tukey_data = []
            tukey_groups = []

            # Prepare data for Tukey HSD
            for sentiment in SENTIMENT_ORDER:
                sentiment_count = counts[sentiment]
                tukey_data.extend([sentiment_count] * sentiment_count)
                tukey_groups.extend([sentiment] * sentiment_count)

            tukey = pairwise_tukeyhsd(
                endog=np.array(
                    tukey_data, dtype=np.float64
                ),  # Numeric data for Tukey HSD
                groups=np.array(tukey_groups),  # Sentiment labels
                alpha=0.05,
            )

            # Convert Tukey HSD results into a table
            tukey_results = pd.DataFrame(
                data=tukey._results_table.data[1:],  # Skip header row
                columns=tukey._results_table.data[0],  # Use header row
            )

            # Render Tukey HSD table as a PNG
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.axis("tight")
            ax.axis("off")
            table = ax.table(
                cellText=tukey_results.values,
                colLabels=tukey_results.columns,
                loc="center",
                cellLoc="center",
            )
            ax.set_title(f"Tukey HSD Results for {selected_affiliation}", pad=10)
            tukey_file = input(
                "Enter the path to save the Tukey HSD table image (e.g., tukey.png): "
            ).strip()
            plt.savefig(tukey_file, bbox_inches="tight")
            print(f"Tukey HSD Table saved as {tukey_file}")
        else:
            print("Tukey HSD could not be performed due to insufficient data.")

    else:
        raise ValueError("Invalid affiliation abbreviation. Please try again.")

else:
    raise ValueError("Invalid choice! Please enter 1 or 2.")
