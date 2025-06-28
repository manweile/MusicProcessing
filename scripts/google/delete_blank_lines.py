import os


def delete_empty_lines(filepath):
    """
    @brief Deletes empty lines (including lines with only whitespace) from a text file.

    @param filepath (str): The path to the text file.
    """
    temp_filepath = filepath + ".tmp"

    with open(filepath, 'r') as infile, open(temp_filepath, 'w') as outfile:
        for line in infile:
            if line.strip():  # Check if the line is not empty after stripping whitespace
                outfile.write(line)

    # Replace the original file with the temporary file
    os.remove(filepath)
    os.rename(temp_filepath, filepath)


# Example usage:
file_to_clean = "my_text_file.txt"

# Create a sample file with empty lines for demonstration
with open(file_to_clean, 'w') as f:
    f.write("This is line 1.\n")
    f.write("\n")
    f.write("This is line 2.\n")
    f.write("   \n")  # Line with only whitespace
    f.write("This is line 3.\n")

print(f"Original content of {file_to_clean}:")
with open(file_to_clean, 'r') as f:
    print(f.read())

delete_empty_lines(file_to_clean)

print(f"\nContent of {file_to_clean} after removing empty lines:")
with open(file_to_clean, 'r') as f:
    print(f.read())
