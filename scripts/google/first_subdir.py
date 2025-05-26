from pathlib import Path

def get_first_subdirectory(path_str):
    path = Path(path_str)
    if not path.is_dir():
        return None  # or raise an exception

    # NB results are not inherently sorted!!
    # iterdir uses os.listdir, which does no sorting on it's own accord but uses the OS sort order instead
    subdirectories = []
    iter_object = path.iterdir()
    for item in iter_object:
        if item.is_dir():
            subdirectories.append(item)

    # subdirectories = [x for x in path.iterdir() if x.is_dir()]
    return subdirectories[0] if subdirectories else None

# Example usage:
directory_path = r"C:\Music" # Current directory
first_subdir = get_first_subdirectory(directory_path)

if first_subdir:
    print(f"The first subdirectory in '{directory_path}' is: {first_subdir}")
else:
    print(f"No subdirectories found in '{directory_path}'.")