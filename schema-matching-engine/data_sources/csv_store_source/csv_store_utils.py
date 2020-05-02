import os


def get_folders_within_folder(folder_path: str):
    return [item for item in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, item))]
