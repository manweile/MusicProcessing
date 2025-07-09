import argparse
import os
import platform
import shutil
import sys


def parse_text(file_path):
    """
    @brief Removes empty line and progress lines from a normalize output text file.

    @param file_path (str): The path to the text file.
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

    temp_filepath = file_path + ".tmp"

    with open(file_path, 'r') as infile, open(temp_filepath, 'w') as outfile:
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

    # Replace the original file with the temporary file, keeping temp
    os.remove(file_path)
    # os.rename(temp_filepath, file_path)
    shutil.copy(temp_filepath, file_path)


def main(args):
    try:
        if args.subcommand == "parse-text":
            file_path = getattr(args, "file")
            parse_text(file_path)

    except NotImplementedError:
        raise NotImplementedError(f"Command {args.subcommand} does not exist")
    except Exception as e:
        raise Exception(f"Exception {e} executing subcommand {args.subcommand}")


if __name__ == "__main__":
    '''
    @brief Top level script environment entry point

    @details Parses and validates input arguments.
    '''

    os_name = platform.system()
    if os_name == "Windows":
        if sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    elif os_name == "Linux":
        if sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description='Output Processing')
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    parse_text_parser = subparsers.add_parser("parse-text", help="Parses the text in a normalize walk output file")
    parse_text_parser.add_argument("file", type=str, help="mandatory full path to output file")
    parse_text_parser.set_defaults(func=parse_text)

    args = parser.parse_args()
    main(args)

# parse_text("/home/gerald/MusicProcessing/src/generated_files/results_files/normalize-walk.txt")