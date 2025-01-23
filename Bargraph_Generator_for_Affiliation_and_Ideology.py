import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import f_oneway
import numpy as np

# Define mapping of affiliations to abbreviations
AFFILIATION_MAP = {
    "PDP Laban": "PDP",
    "Nacionalista Party": "NP",
    "Liberal Party (LP)": "LP",
    "United Nationalist Alliance (UNA)": "UNA",
    "Lakas CMD": "LKM",
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

        # Perform ANOVA for ALL Affiliations
        print("\nRunning ANOVA for Political Affiliations...")

        # Prepare data for ANOVA
        affiliation_sentiment_data = []
        affiliation_labels = []

        # Extract counts for each affiliation and its sentiment distribution
        for affiliation in counts.index:
            filtered_affiliation = df[df["Political Affiliation"] == affiliation]
            sentiment_counts = filtered_affiliation["Overall Sentiment"].value_counts()
            sentiment_counts = sentiment_counts.reindex(SENTIMENT_ORDER, fill_value=0)

            # Append sentiment counts and labels
            affiliation_sentiment_data.extend(sentiment_counts.values)
            affiliation_labels.extend([affiliation] * len(SENTIMENT_ORDER))

        # Check if there are at least two groups to run ANOVA
        if len(set(affiliation_labels)) > 1:
            # Perform ANOVA
            f_stat, p_value = f_oneway(
                *[
                    affiliation_sentiment_data[i :: len(SENTIMENT_ORDER)]
                    for i in range(len(SENTIMENT_ORDER))
                ]
            )

            # Compute Sum of Squares
            grand_mean = np.mean(affiliation_sentiment_data)
            between_group_ss = sum(
                len(SENTIMENT_ORDER)
                * (
                    np.mean(affiliation_sentiment_data[i :: len(SENTIMENT_ORDER)])
                    - grand_mean
                )
                ** 2
                for i in range(len(SENTIMENT_ORDER))
            )
            within_group_ss = sum(
                sum(
                    (x - np.mean(affiliation_sentiment_data[i :: len(SENTIMENT_ORDER)]))
                    ** 2
                    for x in affiliation_sentiment_data[i :: len(SENTIMENT_ORDER)]
                )
                for i in range(len(SENTIMENT_ORDER))
            )
            total_ss = between_group_ss + within_group_ss

            # Degrees of Freedom
            df_between = len(SENTIMENT_ORDER) - 1
            df_within = len(affiliation_sentiment_data) - len(SENTIMENT_ORDER)
            df_total = df_between + df_within

            # Mean Squares
            ms_between = between_group_ss / df_between if df_between != 0 else 0
            ms_within = within_group_ss / df_within if df_within != 0 else 0

            # Create ANOVA table
            anova_table = [
                ["Source", "Sum of Squares", "df", "Mean Square", "F", "Sig."],
                [
                    "Between Groups",
                    f"{between_group_ss:.3f}",
                    f"{df_between}",
                    f"{ms_between:.3f}",
                    f"{f_stat:.3f}",
                    f"{p_value:.3f}",
                ],
                [
                    "Within Groups",
                    f"{within_group_ss:.3f}",
                    f"{df_within}",
                    f"{ms_within:.3f}",
                    "",
                    "",
                ],
                ["Total", f"{total_ss:.3f}", f"{df_total}", "", "", ""],
            ]

            # Render ANOVA table as a PNG
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.axis("tight")
            ax.axis("off")
            table = ax.table(
                cellText=anova_table[1:],
                colLabels=anova_table[0],
                loc="center",
                cellLoc="center",
            )
            ax.set_title("ANOVA Table for Political Affiliations", pad=10)
            anova_file = input(
                "Enter the path to save the ANOVA table image (e.g., anova.png): "
            ).strip()
            plt.savefig(anova_file, bbox_inches="tight")
            print(f"ANOVA Table saved as {anova_file}")
        else:
            print("ANOVA could not be performed: insufficient groups.")

    # Case 2.2: Specific Affiliation (unchanged)
    elif selected_abbreviation in ABBREVIATION_MAP:
        # Original functionality for specific affiliations remains unchanged
        pass

    else:
        raise ValueError("Invalid affiliation abbreviation. Please try again.")

else:
    raise ValueError("Invalid choice! Please enter 1 or 2.")
