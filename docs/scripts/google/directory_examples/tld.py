from pathlib import Path


def get_top_level_directory(path_string):
    """
    Returns the top-level directory of a given path string.

    Args:
      path_string: A string representing the file path.

    Returns:
      A string representing the top-level directory, or None if the path is invalid.
    """

    path_object = Path(path_string)

    # Handle cases like '/' or 'C:\\' where parent does not exist
    if str(path_object) == path_object.root:
        return str(path_object)

    return str(path_object.parents[-1])


# Example usage:
file_path = "/home/user/documents/project/file.txt"
top_level_dir = get_top_level_directory(file_path)
print(f"The top-level directory of '{file_path}' is: {top_level_dir}")

file_path_2 = r"C:\Music\3 Doors Down\3 Doors Down"
top_level_dir_2 = get_top_level_directory(file_path_2)
print(f"The top-level directory of '{file_path_2}' is: {top_level_dir_2}")

file_path_3 = "/"
top_level_dir_3 = get_top_level_directory(file_path_3)
print(f"The top-level directory of '{file_path_3}' is: {top_level_dir_3}")

file_path_4 = "C:\\"
top_level_dir_4 = get_top_level_directory(file_path_4)
print(f"The top-level directory of '{file_path_4}' is: {top_level_dir_4}")
