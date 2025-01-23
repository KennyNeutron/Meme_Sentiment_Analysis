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

# Ask user for input and output file paths
input_file = input("Enter the path to the input Excel file: ").strip()
output_file = input(
    "Enter the path to save the output image file (e.g., output.png): "
).strip()
anova_table_file = input(
    "Enter the path to save the ANOVA table image (e.g., anova_table.png): "
).strip()

# Load the Excel file with the results
df = pd.read_excel(input_file)

print("\nAvailable affiliations:")
for full, abbr in AFFILIATION_MAP.items():
    print(f"{abbr} - {full}")

selected_abbreviation = (
    input("\nEnter the abbreviation for the affiliation to report: ").strip().upper()
)

if selected_abbreviation in ABBREVIATION_MAP:
    # Filter data for the selected affiliation
    selected_affiliation = ABBREVIATION_MAP[selected_abbreviation]
    filtered_df = df[df["Political Affiliation"] == selected_affiliation]
    if filtered_df.empty:
        raise ValueError(f"No data found for the affiliation '{selected_affiliation}'.")

    counts = filtered_df["Overall Sentiment"].value_counts()

    # Ensure consistent order of sentiments
    counts = counts.reindex(SENTIMENT_ORDER, fill_value=0)

    # Calculate total count
    total_count = counts.sum()
    formatted_total = f"Total: {total_count:,}"

    # Create the bar graph with custom colors
    sentiment_colors = {"Negative": "red", "Neutral": "gray", "Positive": "green"}
    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        counts.index,
        counts.values,
        alpha=0.8,
        color=[sentiment_colors[sentiment] for sentiment in counts.index],
    )

    # Add labels above the bars
    for bar in bars:
        count = bar.get_height()
        formatted_count = f"{count:,}"  # Format number with commas
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            count,
            formatted_count,
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Customize graph appearance
    plt.title(
        f"Sentiment Distribution for {selected_affiliation} ({formatted_total})",
        fontsize=14,
        loc="left",
    )
    plt.xlabel("Sentiment", fontsize=12)
    plt.ylabel("Number of Memes", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save the graph as an image
    plt.savefig(output_file, bbox_inches="tight")

    # Show the graph
    plt.show()

    # Prepare data for ANOVA
    sentiment_data = [counts[sentiment] for sentiment in SENTIMENT_ORDER]
    group_sizes = [counts[sentiment] for sentiment in SENTIMENT_ORDER]

    # Compute Sum of Squares
    overall_mean = np.mean(sentiment_data)
    between_group_ss = sum(
        group_sizes[i] * ((sentiment_data[i] - overall_mean) ** 2)
        for i in range(len(sentiment_data))
    )
    within_group_ss = sum(sentiment_data[i] for i in range(len(sentiment_data)))
    total_ss = between_group_ss + within_group_ss

    # Degrees of Freedom
    df_between = len(SENTIMENT_ORDER) - 1
    df_within = total_count - len(SENTIMENT_ORDER)
    df_total = df_between + df_within

    # Mean Squares
    ms_between = between_group_ss / df_between if df_between != 0 else 0
    ms_within = within_group_ss / df_within if df_within != 0 else 0

    # F-value
    f_value = ms_between / ms_within if ms_within != 0 else 0

    # Prepare data for ANOVA table
    anova_data = [
        [
            "Between Groups",
            f"{between_group_ss:.3f}",
            df_between,
            f"{ms_between:.3f}",
            f"{f_value:.3f}",
            "<0.05" if f_value > 1 else "N.S.",
        ],
        [
            "Within Groups",
            f"{within_group_ss:.3f}",
            df_within,
            f"{ms_within:.3f}",
            "",
            "",
        ],
        ["Total", f"{total_ss:.3f}", df_total, "", "", ""],
    ]

    # Get title from the filename (removing .png)
    anova_title = anova_table_file.replace(".png", "").replace("_", " ").title()

    # Render ANOVA table as a matplotlib table
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_title(anova_title, fontsize=14, pad=10)
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(
        cellText=anova_data,
        colLabels=[
            "Source",
            "Sum of Squares",
            "df",
            "Mean Square",
            "F-value",
            "p-value",
        ],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(anova_data[0]))))

    # Save ANOVA table as an image
    plt.savefig(anova_table_file, bbox_inches="tight")

    print(f"\nANOVA Table saved as an image: {anova_table_file}")
else:
    raise ValueError("Invalid affiliation abbreviation. Please try again.")

print(f"Graph saved as {output_file}")
