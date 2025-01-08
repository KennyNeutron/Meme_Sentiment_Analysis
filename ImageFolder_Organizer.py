import os
import shutil


def divide_images_into_batches(folder_path, num_batches):
    """
    Divides images in the given folder into multiple batches.

    Args:
        folder_path (str): Path to the folder containing images.
        num_batches (int): Number of batches to divide the images into.
    """
    try:
        # Get a list of all image files in the folder
        image_files = [
            f
            for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp"))
        ]

        # Sort the image files to ensure consistent ordering
        image_files.sort()

        # Calculate the number of images per batch
        total_images = len(image_files)
        images_per_batch = total_images // num_batches
        remainder = total_images % num_batches

        print(f"Total images: {total_images}")
        print(f"Images per batch: {images_per_batch}, Remainder: {remainder}")

        # Create the batches
        start_index = 0
        for batch_num in range(1, num_batches + 1):
            batch_folder = os.path.join(folder_path, f"Batch{batch_num}")
            os.makedirs(batch_folder, exist_ok=True)

            # Determine the range of images for this batch
            end_index = (
                start_index + images_per_batch + (1 if batch_num <= remainder else 0)
            )
            batch_files = image_files[start_index:end_index]

            # Move images to the batch folder
            for file_name in batch_files:
                source_path = os.path.join(folder_path, file_name)
                destination_path = os.path.join(batch_folder, file_name)
                shutil.move(source_path, destination_path)

            print(f"Batch{batch_num} created with {len(batch_files)} images.")
            start_index = end_index

        print("All batches created successfully.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    folder_path = input("Enter the path to the folder containing images: ").strip()
    num_batches = int(input("Enter the number of batches: ").strip())
    divide_images_into_batches(folder_path, num_batches)
