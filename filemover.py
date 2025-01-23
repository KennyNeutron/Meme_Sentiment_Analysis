import os
import shutil


def move_files(source_excel, source_png, destination_folder):
    """
    Moves an Excel file and a PNG file to a specified folder.

    Parameters:
        source_excel (str): Path to the Excel file.
        source_png (str): Path to the PNG file.
        destination_folder (str): Path to the destination folder.
    """
    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    try:
        # Move the Excel file
        if os.path.exists(source_excel):
            shutil.move(source_excel, destination_folder)
            print(f"Moved Excel file to {destination_folder}")
        else:
            print(f"Excel file not found: {source_excel}")

        # Move the PNG file
        if os.path.exists(source_png):
            shutil.move(source_png, destination_folder)
            print(f"Moved PNG file to {destination_folder}")
        else:
            print(f"PNG file not found: {source_png}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage

