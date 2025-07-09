import os


def parse_text(filepath):
    """
    @brief Removes empty line and progress lines from a normalize output text file.

    @param filepath (str): The path to the text file.
    """

    '''
    if line not empty, check what text we have:
        if line contains "Beginning normalization to ", copy to output file
        if line contains "Source directory path:", copy to output file
        if line contains "Getting normalizing to ", iterate to next line
        if line contains "{", copy to output file
        if line contains "input_", copy to output file
        if line contains "output_", copy to output file
        if line contains "normalization_type", copy to output file
        if line contains "target_offset", copy to output file
        if line contains "}", copy to output file
        if line contains "Normalizing to ", iterate to next line
        if line contains "Post normalization to ", copy to output file
        if line contains "FFMPEG used normalization type:", copy to output file
        if line contains "Successful normalization to ", copy to output file, print blank line to output
    '''

    temp_filepath = filepath + ".tmp"

    with open(filepath, 'r') as infile, open(temp_filepath, 'w') as outfile:
        for line in infile:
            # if we dont have text, blank line is not copied to output
            if line.strip():
                if "Beginning normalization on:" in line:
                    outfile.write(line)
                elif "Source directory path:" in line:
                    outfile.write(line)
                elif "Getting normalizing stats" in line:
                    continue
                elif "Pre normalization stats:" in line:
                    outfile.write(line)
                elif "{" in line:
                    outfile.write(line)
                elif "input_" in line:
                    outfile.write(line)
                elif "output_" in line:
                    outfile.write(line)
                elif "normalization_type" in line:
                    outfile.write(line)
                elif "target_offset" in line:
                    outfile.write(line)
                elif "}" in line:
                    outfile.write(line)
                elif "Normalizing audio" in line:
                    continue
                elif "Post normalization stats:" in line:
                    outfile.write(line)
                elif "FFMPEG used normalization type:" in line:
                    outfile.write(line)
                elif "Successful normalization on:" in line:
                    outfile.write(line)
                    outfile.write("\n")

    # Replace the original file with the temporary file
    os.remove(filepath)
    os.rename(temp_filepath, filepath)


parse_text("/home/gerald/MusicProcessing/src/generated_files/results_files/normalize-walk.txt")