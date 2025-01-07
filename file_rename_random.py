import os
import random
import string


def generate_random_name(length=10):
    """Generate a random string of given length, ensuring the first character is a letter."""
    if length < 1:
        raise ValueError("Length must be at least 1")
    first_char = random.choice(
        string.ascii_letters
    )  # Ensure the first character is a letter
    remaining_chars = "".join(
        random.choices(string.ascii_letters + string.digits, k=length - 1)
    )
    return first_char + remaining_chars


def rename_files_with_random_names(folder_path, name_length=20):
    file_num = 0
    try:
        files = sorted(
            [
                f
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
            ]
        )

        for file_name in files:
            file_extension = os.path.splitext(file_name)[1]
            new_file_name = f"{generate_random_name(name_length)}{file_extension}"
            old_file_path = os.path.join(folder_path, file_name)
            new_file_path = os.path.join(folder_path, new_file_name)

            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {file_name} -> {new_file_name}")
            file_num += 1

        print(f"All {file_num:,} files renamed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
drive_path = "D:/KennyNeutron_TheCoder/Projects"  # Adjust this to your project path
folder_path = f"{drive_path}/Meme_Sentiment_Analysis/images_DataSet_Final"

rename_files_with_random_names(folder_path)
