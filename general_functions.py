from flask import session
from PIL import Image
import pytesseract
import tiktoken
import logging
from extensions import openai_db
from token_functions import token_updating_func
import pymongo
import random
import bcrypt
import re
from flask_login import current_user
from weasyprint import HTML, CSS


"""
ZMC STUDENT ASSISTANT - GENERAL FUNCTIONS MODULE

Module: general_functions.py

Developer: Julius Mwangi
Contact:
    - Email: juliusmwasstech@gmail.com

---

Disclaimer:
This project is a solo endeavor, with Julius Mwangi leading all
development efforts. For inquiries, concerns, or collaboration requests
related to versatile functions across the app, please direct them to the
provided contact email.

---

About

Welcome to the core of the ZMC Student Assistant - the
`general_functions.py` module. This module serves as a repository for
versatile functions that can be utilized across different components of
the app, skillfully crafted by Julius Mwangi.

Developer Information

- Name: Julius Mwangi
- Contact:
  - Email: [juliusmwasstech@gmail.com]
            (mailto:juliusmwasstech@gmail.com)

Acknowledgments

Special thanks to the incredible ALX TEAM for their unwavering support
and guidance. Their influence has been instrumental in shaping my journey
as a software engineer, contributing to the development of versatile
functions that enhance various aspects of the app.

---

Note to Developers:
Feel free to explore, contribute, or connect. Your insights and feedback,
especially regarding the usability and enhancement of these general
functions, are highly valued and appreciated!

Happy coding!
"""


def check_lock_status():
    """
    Check if the user's account is locked.

    Returns:
    - dict: A dictionary indicating the user's access status.
        If the account is locked, returns a dictionary with access
        set to False and additional information in response_text.
        If the account is not locked, returns a dictionary with
        access set to True.
    """

    return_lock_message = ""
    lock_obj = lock_status(current_user.email)

    if lock_obj.get("lock", True):
        # User has being locked out due to token depletion
        return_lock_message = (
                "<p style=&bksl;color:#FF0000 !important;&bksl;>"
                + f"""{lock_obj["message"]}</p>"""
                )

    elif lock_obj.get("error", False):
        # An error occurred before the user remaining tokens could
        # be checked; this is considered an account lock.
        return_lock_message = (
                "<p style=&bksl;color:#FF0000 !important;&bksl;>"
                + f"""{lock_obj["message"]}</p>"""
                )

    if return_lock_message:
        obj = {
            "access": False,
            "success": True,
            "response_text": return_lock_message,
            "threads": [],
            "tokens": lock_obj["tokens"]
        }
        return obj

    return {"access": True}


def lock_status(email):
    """
    Check the lock status of a user account based on the
    provided email.

    Parameters:
    - email (str): The email address associated with the
    user account.

    Returns:
        - str: "locked" if the account is locked, "unlocked" if it
        is unlocked.
        Returns an error message if there are issues retrieving the
        user from the database.
        Returns an error message if an exception occurs.
    """
    try:
        # Connect to the database
        collection = openai_db["user_account"]

        # Retrieve user from the database
        user = collection.find_one({"email": email})
        print(str(user))

        # Define an object to hold the return data
        obj = {}
        tokens = 0

        if user:
            # Define a lock message
            message = (
                    "Dear student, your tokens are depleted. Recharge"
                    + " your account to continue enjoying the "
                    + "services."
                    )

            # Check the lock status of the user account
            account_lock = user.get("lock", True)
            tokens = user.get("tokens", 0)

            unlocked = {"lock": False, "message": "", "tokens": tokens}
            locked = {"lock": True, "message": message, "tokens": tokens}

            return locked if account_lock else unlocked

        # Unable to get user data
        message = "Unable to retrieve your account data from the database"
        return {"error": True, "message": message, "tokens": tokens}

    except Exception as e:
        print(f"lock_status Error: {e}")
        message = "Sorry an error occured, try again latter."
        return {"error": True, "message": message, "tokens": tokens}


def generate_pdf_styler_obj(html_content, user_obj=None):
    # print("generate_pdf_styler_obj called")
    """
    Generates a styling object for PDF creation.

    Args:
        html_content (str): HTML content to be included in the PDF.

    Returns:
        dict: Styling object with parameters for PDF generation.

    """
    pdf_name = current_user.email + str(generate_key()) + ".pdf"

    obj = {
        "lt_spacing": "2px",
        "margin": "1cm",
        "bg_color": "#000134",
        "font_size": "20px",
        "html_content": html_content,
        "output_filename": pdf_name,
        "text_color": "brown"
    }

    if user_obj:
        obj["lt_spacing"] = str(user_obj["letter_spacing"]) + "px"
        obj["font_size"] = str(user_obj["font_size"]) + "px"
        obj["text_color"] = user_obj["text_color"]
        obj["bg_color"] = user_obj["background_color"]
        obj["span_color"] = user_obj["span_color"]
        obj["font_family"] = user_obj["font_family"]
        # print(f"general obj = {str(obj)}")

    return obj


async def code_to_pdf(obj):
    """
    Converts HTML content to a PDF file with specified styling.

    Args:
        obj (dict): Styling object containing parameters for PDF generation.

    Returns:
        str: Filename of the generated PDF.

    """
    custom_css = f"""

    * {{
        letter-spacing: {obj["lt_spacing"]};
        font-size: {obj["font_size"]};
        color: {obj["text_color"]};
        white-space: pre-wrap;
    }}
    @page {{
        size: Letter;
        margin: {obj["margin"]};
        background-color: {obj["bg_color"]};
    }}
    p {{
        color: {obj["text_color"]} !important;
    }}
    span {{
        color: {obj["span_color"]};
        font-weight: bold;
    }}
    """

    # Convert HTML to PDF using WeasyPrint with inline CSS
    HTML(string=obj["html_content"]).write_pdf(
            obj["output_filename"], stylesheets=[CSS(string=custom_css)])

    return obj["output_filename"]


def validate_pdf_request_data(obj):
    """
    Validate and sanitize PDF request data.

    This function checks and adjusts the values in the provided
    dictionary object to ensure they meet certain criteria for
    letter spacing, font size, background color, and text color.

    Parameters:
    - obj (dict): A dictionary containing PDF request data with the
    following keys:
        - "letter_spacing" (float or int): Desired letter spacing
            (0.5 to 3).
        - "font_size" (int): Desired font size (10 to 30).
        - "background_color" (str): Background color in hex format
            (e.g., "#1a2b3c").
        - "text_color" (str): Text color in hex format
            (e.g., "#1a2b3c").

    Returns:
    - dict: A validated and sanitized dictionary object.

    Note:
    - If a value is invalid, it will be adjusted to a default value.
    - If an exception occurs during the validation process, the
        function returns False.
    """
    try:
        if obj["letter_spacing"]:
            num = float(obj["letter_spacing"])
            if num < 0.5 or num > 3:
                obj["letter_spacing"] = 1

        if obj["font_size"]:
            num = float(obj["font_size"])
            if num < 10 or num > 30:
                obj["font_size"] = 10

        if obj["page_margins"]:
            num = float(obj["page_margins"])
            if num < 0.5 or num > 2:
                obj["page_margins"] = 1

        if obj["background_color"]:
            code = obj["background_color"]
            check = is_valid_hex_color(code)
            if not check:
                obj["background_color"] = "#FFF"

        if obj["text_color"]:
            code = obj["text_color"]
            check = is_valid_hex_color(code)
            if not check:
                print("\n\ntext color not found")
                obj["text_color"] = "black"

        if obj["span_color"]:
            code = obj["span_color"]
            check = is_valid_hex_color(code)
            if not check:
                obj["span_color"] = "lime"

        return obj
    except Exception as e:
        print(f"validate_pdf_request_data Error = {e}")
        return False


def is_valid_hex_color(code):
    """
    Check if a given string is a valid hex color code.

    Parameters:
    - code (str): The input string to check.

    Returns:
    - bool: True if the string is a valid hex color code, False otherwise.
    """
    # Define the regular expression pattern for a valid hex color code
    # pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    pattern = re.compile(r'''
        ^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$  # Hex format
        |                                # OR
        ^rgba?\(
            \d{1,3},\s?\d{1,3},\s?\d{1,3}  # RGB format
            (,\s?[0-1](\.\d{1,2})?)?       # Optional alpha channel
        \)$
    ''', re.VERBOSE)

    # Check if the provided code matches the pattern
    return bool(pattern.match(code))


async def get_user_styling_preference(email):
    """
    Get the styling preferences for a user.

    Args:
    - email (str): The email of the user.

    Returns:
    - dict or None: A dictionary containing user styling preferences,
    or None if not found.
    """
    try:
        # Connect to the database
        collection = openai_db["user_account"]
        result = collection.find_one({"email": email})
        if result:
            styling_obj = result["user_styling"]
            return styling_obj
        return None
    except Exception as e:
        print(f"get_user_styling_preference Error = {e}")
        return None


def openai_threads_messages_save(openai_data):
    """
    Save OpenAI thread messages.

    Args:
    - openai_data (dict): Data to be saved.

    Returns:
    - str: "success" if successful, "fail" otherwise.
    """
    try:
        collection = openai_db["openai_threads"]

        # Find the most recent document
        email = current_user.email
        result = collection.find_one(
                {"email": email}, sort=[("timestamp", pymongo.DESCENDING)])

        # Check if the thread_id already exists
        query = {"$and": [
            {"email": email},
            {"thread_id": openai_data['thread_id']}]}
        result2 = collection.find_one(query)

        if result:
            # Increment thread_num only if the thread_id is new
            if not result2:
                openai_data['thread_num'] = result['thread_num'] + 1
                # Keep thread sequence record
                save_thread_number(
                        result['thread_num'] + 1,
                        openai_data["thread_id"],
                        openai_data["assistant_id"])
            else:
                openai_data['thread_num'] = result2['thread_num']
        else:
            openai_data['thread_num'] = 1
            # Keep thread sequence record
            save_thread_number(1, openai_data["thread_id"],
                               openai_data["assistant_id"])

        # Insert the new document
        result = collection.insert_one(openai_data)

        if result.acknowledged and result.inserted_id:
            return "success"
        else:
            return "fail"

    except Exception as e:
        logging.error(f"openai_threads_create Error: {e}")
        return "fail"


# Function to save thread numbers and their associated thread id and
#   assistant id.
def save_thread_number(thread_num, thread_id, assistant_id):
    """
    Save thread numbers and their associated thread id and assistant id.

    Args:
    - thread_num (int): Thread number.
    - thread_id (str): Thread ID.
    - assistant_id (str): Assistant ID.

    Returns:
    - bool: True if successful, False otherwise.
    """
    try:
        email = current_user.email
        # Connect to the database
        collection = openai_db['thread_sequence']

        obj = {
                "email": email,
                "thread_num": thread_num,
                "thread_id": thread_id,
                "assistant_id": assistant_id
            }

        result = collection.insert_one(obj)

        if result.acknowledged and result.inserted_id:
            return True
        return False
    except Exception as e:
        print(f"save_thread_number Error: {e}")
        return False


def text_generator(image_file):
    """
    Extract text from an image using OCR.

    Args:
    - image_file (str): Path to the image file.

    Returns:
    - str: Extracted text from the image.
    """
    # Open an image file
    image = Image.open(image_file)

    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(image)
    return text


async def num_tokens_from_messages(message, model="gpt-3.5-turbo-1106"):
    """
    Return the number of tokens used by a list of messages.

    Args:
    - message (str): The input message.
    - model (str): The language model to use. Default is "gpt-3.5-turbo-1106".

    Returns:
    - int: Number of tokens used.
    """
    num_tokens = 0

    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens_per_message = 4
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    try:
        num_tokens += tokens_per_message
        num_tokens += len(encoding.encode(message))
        num_tokens += 3
        return num_tokens
    except Exception as e:
        print(f"num_tokens&from_messages Error: {e}")
        return 0


async def clean_content(input_content):
    """
    Extracts the required value from the returned message by the api.
    Once the value is obtained all newline characters are removed.
    This is because html don't depend on newline characters to render
    new lines.
    Finally, the tokens consumed by the current call is calculated here
    before sending the result to the other function for further processing.
    """
    start_index = input_content.find('value="')
    if start_index == -1:
        start_index = input_content.find("value='")

    if start_index != -1:
        start_index += len('value="')
        end_index = input_content.rfind('"),', 0, len(input_content) - 3)
        if end_index == -1:
            end_index = input_content.rfind("'),", 0, len(input_content) - 3)

        if end_index != -1:
            first_content = input_content[start_index:end_index]

            # Count number of tokens used
            token_count = await num_tokens_from_messages(first_content)
            token_count_session = session.get("instruction_prompt_tokens", 0)
            if token_count_session:
                token_count_session = int(token_count_session)

            total_tokens_count = token_count + token_count_session

            # Save the total tokens used in the session
            session["currently_used_tokens"] = total_tokens_count

            # Update user tokens
            token_updating_func(total_tokens_count)

            # cleaned_content = second_content.replace(
            # '\n', '').replace('\\n', '')

            cleaned_content = first_content.replace(
                    "\n", "<br>").replace(
                            "\\n", "<br>").replace(
                                    "\\'", "'").replace('\\"', '"')

            # Finalise content processing
            processed_content = await process_text(cleaned_content)

            # Check if the message was not correctly interprated
            pattern = r'^\s*(<br>\s*)+$'
            match = re.search(pattern, processed_content)
            if match:
                return cleaned_content
            return processed_content

    # Return the original content if substrings are not found
    return input_content


async def process_text(input_text):
    """
    Processes input text and applies formatting based on specified patterns.

    Parameters:
    - input_text (str): The input text to be processed.

    Returns:
    - str: The formatted text.
    """

    # Split input_text by '<br>' to process each part separately
    words = input_text.split('<br>')
    result = []

    for word in words:
        keep_track = False
        # Check for empty string and append '<br>' if found
        if not word:
            result.append("<br>")
        elif word[0].isupper() and ':' in word:
            # Process uppercase words with ':' pattern
            pattern = r'([A-Za-z]+ \([A-Za-z]+ [A-Za-z]+\): )|([A-Za-z]+: )'
            match = re.search(pattern, word)
            if match:
                colon_index = word.index(':')
                statement = (
                    '<span style="font-weight: bold;">'
                    + f'{word[:colon_index]}'
                    + f'</span>{word[colon_index:]}<br>'
                )
                result.append(statement)
        elif word[0].isupper() and '-' in word:
            # Process uppercase words with '-' pattern
            pattern = r'([A-Za-z]+ \([A-Za-z]+ [A-Za-z]+\) - )|([A-Za-z]+ - )'
            match = re.search(pattern, word)
            if match:
                colon_index = word.index('-')
                statement = (
                    '<span style="font-weight: bold;">'
                    + f'{word[:colon_index]}'
                    + f'</span>{word[colon_index:]}<br>'
                )
                result.append(statement)
        else:
            # Process numeric patterns
            pattern = r'(\d+\.\s)'
            match = re.search(pattern, word)
            if match:
                if ':' in word:
                    colon_index = word.index(':')
                    statement = (
                        '<span style="font-weight: bold;">'
                        + f'{word[:colon_index]}'
                        + f'</span>{word[colon_index:]}<br>'
                    )
                    result.append(statement)
                elif '-' in word:
                    colon_index = word.index('-')
                    statement = (
                        '<span style="font-weight: bold;">'
                        + f'{word[:colon_index]}'
                        + f'</span>{word[colon_index:]}<br>'
                    )
                    result.append(statement)
            else:
                keep_track = True
        if keep_track:
            result.append(word)

    # Concatenate formatted parts to create the final text
    final_text = ''.join(result)
    return final_text


# Function to create list of thread numbers
def create_thread_array():
    """
    Create a list of thread numbers associated with the current user's
    email.

    Returns:
        list: A list containing thread numbers.
              If no threads are found, returns an empty list.
              If an error occurs, returns 0.
    """
    try:
        email = current_user.email

        # create a list variable
        thread_list = []

        # Connect to the database
        collection = openai_db['thread_sequence']

        result = collection.find({"email": email})
        if result is not None:
            for obj in result:
                thread_list.append(obj["thread_num"])
            return thread_list
        return 0
    except Exception as e:
        print(f"create_thread_array() Error: {e}")
        return 0


# Function for shifting threads
def shift_threads(thread_num):
    """
    Shift the current session to a different thread based on the
    provided thread number.

    Args:
        thread_num (int): The thread number to shift to.

    Returns:
        Union[dict, bool]: If the shift is successful, returns thread
        data as a dictionary. If an error occurs or the shift fails,
        returns False.
    """
    thread_num = int(thread_num)
    try:
        email = current_user.email

        # Connect to the database
        collection = openai_db["thread_sequence"]

        result = collection.find_one(
                {"$and": [{"email": email},
                          {"thread_num": thread_num}]})

        if result is not None:
            # Update the  session data
            session["thread_id"] = result["thread_id"]
            session["assistant_id"] = result["assistant_id"]

            # Start thread data retrieval process
            result = get_thread_data(result["thread_id"])
            if result:
                return result
        return False
    except Exception as e:
        print(f"shift_threads(thread_num) Error = {e}")
        return False


# Function for getting thread data
def get_thread_data(thread_id):
    """
    Retrieve thread data based on the provided thread ID.

    Args:
        thread_id (str): The ID of the thread to retrieve data for.

    Returns:
        Union[str, bool]: If the retrieval is successful, returns the
        concatenated thread data as a string. If no data is found or an
        error occurs, returns False.
    """
    try:
        email = current_user.email

        # create a variable to hold thread data
        thread_data = ""

        # Connect to the database
        collection = openai_db["openai_threads"]

        result = collection.find(
                {"$and": [{"email": email},
                          {"thread_id": thread_id}]})

        if result:
            for obj in result:
                thread_data += obj["prompt"] + obj["message"]
            return thread_data
        return False
    except Exception as e:
        print(f"get_thread_data() Error = {e}")
        return False


async def replace_backslash_latex(latex_expression):
    """
    Replace backslashes in a LaTeX expression with the string '&bksl;'.

    Args:
        latex_expression (str): The LaTeX expression to process.

    Returns:
        str: The LaTeX expression with backslashes replaced by '&bksl;'.
    """
    return latex_expression.replace("\\", "&bksl;")


# Reverse to backslashes
async def reverse_replace_backslash_latex(modified_latex):
    """
    Reverse the replacement of backslashes in a modified LaTeX expression.

    Args:
        modified_latex (str): The modified LaTeX expression with '&bksl;'
        replacing backslashes.

    Returns:
        str: The original LaTeX expression with backslashes restored.
    """
    return modified_latex.replace("&bksl;", "\\")


# Function for generating verification key
def generate_key():
    """
    Generate a random verification key.

    Returns:
        int: Random verification key.
    """
    # Generate a random verification key
    key_array = [random.randint(1, 9) for _ in range(4)]

    # Convert the key_array to a single integer
    str_key = ''.join(map(str, key_array))
    key = int(str_key)
    return key


# Function for hashing password
def hash_password(password):
    """
    Hash the given password using bcrypt.

    Args:
        password (str): Password to be hashed.

    Returns:
        bytes: Hashed password.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            salt)
    return hashed_password
