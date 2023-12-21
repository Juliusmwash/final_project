#!/usr/bin/env python3
"""
find_statement.py

This script is designed to search for a specified statement in a given
    file and print the lines containing
that statement along with their line numbers. It takes two command-line
    arguments: the file path and the search statement.

Usage:
    python3 find_statement.py <file_path> <search_statement>

Example:
    python3 find_statement.py sample.txt search_text

Note: This script assumes the file is readable and the specified statement
    is to be found in each line.
"""
import sys


def find_user_details(file_path, search_statement):
    """
    Finds and prints lines containing the specified statement in a file
        along with their line numbers.

    Parameters:
        file_path (str): The path to the file to be searched.
        search_statement (str): The statement to search for in the file.

    Returns:
        None: Prints lines containing the search statement along with
            their line numbers.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
    """
    try:
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                if search_statement in line:
                    print(f"{line}line number = {line_number}")
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 find_statement.py <file_path> " +
              "<search_statement>")
        sys.exit(1)

    file_path = sys.argv[1]
    search_statement = sys.argv[2]

    find_user_details(file_path, search_statement)
