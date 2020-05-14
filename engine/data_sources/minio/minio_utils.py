def correct_file_ending(file_name: str):
    if file_name.endswith(".csv"):
        return file_name
    return file_name + ".csv"
