import os


def parse_text(filepath):
    """
    @brief Removes empty line and progress lines from a convert walk output text file.

    @param filepath (str): The path to the text file.
    """

    '''
    if line not empty, check what text we have:
        if line contains "Beginning", copy to output file
        if line contains "Source directory path", copy to output file
        if line contains "metadata:", copy to output file
        if line contains "key:", copy to output file
        if line contains "Converting", iterate to next line
        if line contains "Successful", copy to output file, print blank line to output
    '''

    temp_filepath = filepath + ".tmp"

    with open(filepath, 'r') as infile, open(temp_filepath, 'w') as outfile:
        for line in infile:
            # if we dont have text, blank line is not copied to output
            if line.strip():
                if "Beginning conversion on" in line:
                    outfile.write(line)
                elif "Source directory path" in line:
                    outfile.write(line)
                elif "metadata: " in line:
                    outfile.write(line)
                elif "key: " in line:
                    outfile.write(line)
                elif "Converting" in line:
                    continue
                elif "Successful conversion on" in line:
                    outfile.write(line)
                    outfile.write("\n")

    # Replace the original file with the temporary file
    os.remove(filepath)
    os.rename(temp_filepath, filepath)


parse_text("/home/gerald/MusicProcessing/src/generated_files/results_files/convert-walk-all.txt")
