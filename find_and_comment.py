#!/usr/bin/python3
import sys

def comment_print_lines(filename, text_to_look_for):
    """
    Comment out lines starting with "print(<text_to_look_for>)" in the
    specified file.

    Args:
        filename (str): Name of the file to process.
        text_to_look_for (str): Text to identify lines to be commented.

    Returns:
        None
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        with open(filename, 'w') as file:
            for line in lines:
                if line.lstrip().startswith("print("):
                    file.write(f'# {line}')
                else:
                    file.write(line)

        print(f'Successfully commented lines starting with "print({text_to_look_for}" in {filename}.')
    except FileNotFoundError:
        print(f'Error: File "{filename}" not found.')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <filename> <text_to_look_for>")
    else:
        filename = sys.argv[1]
        text_to_look_for = sys.argv[2]
        comment_print_lines(filename, text_to_look_for)

