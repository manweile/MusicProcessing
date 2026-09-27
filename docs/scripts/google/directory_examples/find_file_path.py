import os


def find_file_directory(filename, search_path):
    """
    Finds the directory path of a file given its name and a starting search path.

    Args:
        filename (str): The name of the file to find.
        search_path (str): The root directory from which to start the search.

    Returns:
        str or None: The directory path containing the file, or None if not found.
    """
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return root  # 'root' is the current directory being walked
    return None


# Example usage:
file_to_find = "my_document.txt"
starting_directory = "/home/user/documents"  # Or os.getcwd() for current directory

found_directory = find_file_directory(file_to_find, starting_directory)

if found_directory:
    print(f"File '{file_to_find}' found in: {found_directory}")
else:
    print(f"File '{file_to_find}' not found in '{starting_directory}' or its subdirectories.")