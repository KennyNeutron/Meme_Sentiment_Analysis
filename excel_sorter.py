import pandas as pd


def rearrange_rows_by_affiliation(input_file, output_file):
    """
    Rearrange rows of an Excel file by the 'Affiliation' column.

    Args:
        input_file (str): Path to the input Excel file.
        output_file (str): Path to save the rearranged Excel file.
    """
    try:
        # Load the Excel file
        df = pd.read_excel(input_file)

        # Ensure the 'Affiliation' column exists
        if "Political Affiliation" not in df.columns:
            raise ValueError("The 'Affiliation' column is missing in the Excel file.")

        # Sort the DataFrame by the 'Affiliation' column
        sorted_df = df.sort_values(by="PoliticalAffiliation")

        # Save the rearranged DataFrame to a new Excel file
        sorted_df.to_excel(output_file, index=False)
        print(f"Rearranged file saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
input_file_path = "Results/Affiliation_and_Ideology.xlsx"  # Replace with your file path
output_file_path = "Results/Affiliation_and_Ideology_sorted.xlsx"  # Replace with your desired output path
rearrange_rows_by_affiliation(input_file_path, output_file_path)
