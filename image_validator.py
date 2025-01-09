import os
from PIL import Image


def validate_and_remove_images(folder_path):
    """
    Validates images in the given folder, removes corrupted ones,
    and reports the number of corrupted and removed images.

    Args:
        folder_path (str): Path to the folder containing images.
    """
    corrupted_count = 0
    total_images = 0

    try:
        # Get a list of all image files in the folder
        image_files = [
            f
            for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp"))
        ]

        total_images = len(image_files)

        for file_name in image_files:
            file_path = os.path.join(folder_path, file_name)
            try:
                # Attempt to open and verify the image
                with Image.open(file_path) as img:
                    img.verify()
            except (IOError, SyntaxError):
                # Remove corrupted image
                os.remove(file_path)
                corrupted_count += 1
                print(f"Removed corrupted image: {file_name}")

        print(f"Total images checked: {total_images}")
        print(f"Corrupted images removed: {corrupted_count}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    folder_path = input("Enter the path to the folder containing images: ").strip()
    validate_and_remove_images(folder_path)
