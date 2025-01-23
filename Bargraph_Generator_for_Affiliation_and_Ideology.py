import pandas as pd
import matplotlib.pyplot as plt

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

# Ask user what to report
report_type = (
    input(
        "What do you want to report? Enter 'Ideology' for Political Ideology Distribution or 'Affiliation' for Political Affiliation Distribution: "
    )
    .strip()
    .lower()
)

# Validate input
if report_type not in ["ideology", "affiliation"]:
    raise ValueError("Invalid choice! Please enter 'Ideology' or 'Affiliation'.")

# Load the Excel file with the results
df = pd.read_excel(input_file)

if report_type == "ideology":
    # Handle Political Ideology Distribution
    column = "Predicted Ideology"
    title = "Distribution of Memes Across Political Ideologies"
    counts = df[column].value_counts()

    # Calculate total count
    total_count = counts.sum()
    formatted_total = f"Total: {total_count:,}"

    # Create the bar graph
    plt.figure(figsize=(10, 6))
    bars = plt.bar(counts.index, counts.values, alpha=0.8)

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
    plt.title(f"{title} ({formatted_total})", fontsize=14, loc="left")
    plt.xlabel("Political Ideology", fontsize=12)
    plt.ylabel("Number of Memes", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

elif report_type == "affiliation":
    # Handle Political Affiliation Distribution
    print("\nAvailable affiliations:")
    for full, abbr in AFFILIATION_MAP.items():
        print(f"{abbr} - {full}")
    print("ALL - All affiliations")

    selected_abbreviation = (
        input("\nEnter the abbreviation for the affiliation to report or 'ALL': ")
        .strip()
        .upper()
    )

    if selected_abbreviation == "ALL":
        # Distribution of all affiliations
        column = "Political Affiliation"
        counts = df[column].value_counts()

        # Calculate total count
        total_count = counts.sum()
        formatted_total = f"Total: {total_count:,}"

        # Create the bar graph
        plt.figure(figsize=(10, 6))
        bars = plt.bar(counts.index, counts.values, alpha=0.8)

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
            "Distribution of Memes Across Political Affiliations",
            fontsize=14,
            loc="left",
        )
        plt.title(
            f"Distribution of Memes Across Political Affiliations ({formatted_total})",
            fontsize=14,
            loc="left",
        )
        plt.xlabel("Political Affiliation", fontsize=12)
        plt.ylabel("Number of Memes", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

    elif selected_abbreviation in ABBREVIATION_MAP:
        # Sentiment distribution for a specific affiliation
        selected_affiliation = ABBREVIATION_MAP[selected_abbreviation]
        filtered_df = df[df["Political Affiliation"] == selected_affiliation]
        if filtered_df.empty:
            raise ValueError(
                f"No data found for the affiliation '{selected_affiliation}'."
            )

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

print(f"Graph saved as {output_file}")
