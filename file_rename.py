import os


def rename_files_in_folder(folder_path, new_name="image", start_index=1):
    try:
        files = sorted(
            [
                f
                for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
            ]
        )

        for index, file_name in enumerate(files, start=start_index):
            file_extension = os.path.splitext(file_name)[1]
            new_file_name = f"{new_name}_{index:05d}{file_extension}"
            old_file_path = os.path.join(folder_path, file_name)
            new_file_path = os.path.join(folder_path, new_file_name)

            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {file_name} -> {new_file_name}")

        print("All files renamed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


drive_path = "D:/KennyNeutron_TheCoder/Projects"  # change this to the path of the project based on the user's computer
folder_path = f"{drive_path}/Meme_Sentiment_Analysis/images/images_DataSet_Final"

rename_files_in_folder(folder_path)
