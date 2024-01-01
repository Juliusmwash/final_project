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
from flask_login import current_user


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

            cleaned_content = first_content.replace(
                    '\n', '').replace('\\n', '')
            return cleaned_content

    # Return the original content if substrings are not found
    return input_content


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
