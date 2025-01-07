import os


def rename_images_to_jpg(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Get all files in the folder
    files = os.listdir(folder_path)
    image_count = 0

    for index, file_name in enumerate(files):
        file_path = os.path.join(folder_path, file_name)

        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue

        # Create new file name
        new_name = f"image_{index + 1}.jpg"
        new_path = os.path.join(folder_path, new_name)

        # Rename the file
        os.rename(file_path, new_path)
        image_count += 1

    print(f"Renamed {image_count} images in the folder '{folder_path}' to .jpg format.")


# Example usage:
folder_path = "images/images_DataSet_Final"  # Replace with the path to your folder
rename_images_to_jpg(folder_path)
