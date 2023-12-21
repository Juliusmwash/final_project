#!/usr/bin/env python3

"""
find_and_replace.py

This script is designed to search for a specified statement in a given file
    and replace it with another statement.
It takes three command-line arguments: the file path, the search statement,
    and the replacement statement.
The script reads the file, searches for the specified statement, and replaces
    it with the provided replacement.
It then updates the file with the modified content.

Usage:
    python3 find_and_replace.py <file_path> <search_statement>
        <replace_statement>

Example:
    python3 find_and_replace.py sample.txt old_text new_text

Note: This implementation replaces only the first occurrence of the search
    statement on each line.
"""

import sys


def find_and_replace(file_path, search_statement, replace_statement):
    """
    Finds and replaces the specified statement in a file.

    Parameters:
        file_path (str): The path to the file to be processed.
        search_statement (str): The statement to be searched and replaced.
        replace_statement (str): The statement to replace the found search
            statement.

    Returns:
        None: Modifies the file in place, replacing the specified statement.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        found = False

        for line_number, line in enumerate(lines, start=1):
            if search_statement in line:
                found = True
                lines[line_number - 1] = line.replace(
                        search_statement, replace_statement)
                print(f"Found at line {line_number}: {line.strip()} - " +
                      f"Replaced with: {replace_statement}")

        if not found:
            print(f"Search statement '{search_statement}'" +
                  "not found in the file.")

        with open(file_path, 'w') as file:
            file.writelines(lines)

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 find_and_replace.py <file_path> \
                <search_statement> <replace_statement>")
        sys.exit(1)

    file_path = sys.argv[1]
    search_statement = sys.argv[2]
    replace_statement = sys.argv[3]

    find_and_replace(file_path, search_statement, replace_statement)
