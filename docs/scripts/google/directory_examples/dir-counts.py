import os


def count_directories_by_level(start_path):
    """
    Recursively counts directories by their level (depth) from the start_path.

    Args:
        start_path (str): The root directory from which to start counting.

    Returns:
        dict: A dictionary where keys are integer levels (depths) and values
        are the counts of directories at that level.
    """
    directory_counts = {}
    # Get the initial depth of the start_path
    initial_depth = len(start_path.split(os.sep))

    for root, dirs, files in os.walk(start_path):
        # Calculate the current directory's depth relative to the start_path
        current_depth = len(root.split(os.sep)) - initial_depth

        # Increment the count for the current level if there are subdirectories
        if dirs:
            directory_counts[current_depth] = directory_counts.get(current_depth, 0) + len(dirs)

    return directory_counts

# Example usage:
# Create a dummy directory structure for testing
# os.makedirs("test_dir/level1a/level2a", exist_ok=True)
# os.makedirs("test_dir/level1b", exist_ok=True)
# with open("test_dir/file.txt", "w") as f:
#     f.write("test")


results = count_directories_by_level("/home/gerald/Music")
print(results)
# Expected output might be something like {0: 2, 1: 1} depending on the structure
