import os
import uuid
import json
import time
import re
import pymongo
from pymongo import MongoClient
import logging
import sys
import random
import string
import tracemalloc
import bcrypt
import asyncio

from flask import Blueprint, Flask, request, render_template, session
from flask import redirect, url_for, jsonify, Response
from flask_login import LoginManager, UserMixin, login_user
from flask_login import login_required, logout_user, current_user
from flask.sessions import SecureCookieSessionInterface
from weasyprint import HTML, CSS

"""
Import app, openai_db, openai_client and blueprints
import openai functions
Import models and their functions
Import general functions
Import token functions
Import email functions
"""
from extensions import app, openai_db, login_manager
from development_assisting_route import development_blueprint
from register_login_logout import reg_log_blueprint
from openai_functions import assistant_creator, wait_on_run
from openai_functions import submit_message, get_response
from openai_functions import create_thread_and_run, extract_openai_message
from models_functions import get_user_from_db
from general_functions import openai_threads_messages_save, text_generator
from general_functions import num_tokens_from_messages, clean_content
from general_functions import save_thread_number, create_thread_array
from general_functions import shift_threads, get_thread_data
from general_functions import get_user_styling_preference
from general_functions import replace_backslash_latex, check_lock_status
from general_functions import reverse_replace_backslash_latex
from general_functions import generate_key, hash_password
from general_functions import generate_pdf_styler_obj, code_to_pdf
from general_functions import validate_pdf_request_data
from token_functions import token_updating_func, calculate_old_thread_tokens
from token_functions import get_remaining_user_tokens
from email_functions import send_code_by_email


"""
ZMC STUDENT ASSISTANT - APP MODULE

Module: app.py

Developer: Julius Mwangi
Contact:
    - Email: juliusmwasstech@gmail.com

---

Disclaimer:
This project is a solo endeavor, and all development efforts
are led by Julius Mwangi. Any inquiries, concerns, or
collaboration requests should be directed to the provided
contact email.

---

About

Welcome to the heart of the ZMC Student Assistant! This
module, `app`, serves as the core component, encapsulating
the brilliance and dedication of Julius Mwangi.

Developer Information

- Name: Julius Mwangi
- Contact:
  - Email: [juliusmwasstech@gmail.com]
            (mailto:juliusmwasstech@gmail.com)

Acknowledgments

Special thanks to the incredible ALX TEAM for their unwavering
support and guidance. Their influence has been instrumental in
shaping my journey as a software engineer, and I express my
deepest gratitude.

---

Note to Developers:
Feel free to explore, contribute, or connect. Your feedback
is valuable and appreciated!

Happy coding!
"""


# Start tracing
tracemalloc.start()

# MATH_ASSISTANT_ID = '';
# mathematical expression using LaTeX syntax

# Register the 'development_blueprint' with the app without the prefix
app.register_blueprint(development_blueprint, url_prefix='')

# Register the 'development_blueprint' with the app without the prefix
app.register_blueprint(reg_log_blueprint, url_prefix='')


@login_manager.user_loader
def load_user(email):
    """
    Callback function registered with @login_manager.user_loader.

    Loads a user object from the database based on the provided email.

    Parameters:
    - email (str): The email address of the user to load.

    Returns:
    - User: The user object retrieved from the database.

    """

    return get_user_from_db(email)


@app.route('/update_user_styling', methods=["POST"])
@login_required
def update_user_styling():
    """
    Update user styling information.

    This route allows authenticated users to update their styling
    preferences.

    Method: POST

    Parameters (JSON):
    - user_styling (dict): Dictionary containing user styling preferences.

    Returns (JSON):
    - {"success": True} if the update is successful,
    {"success": False} otherwise.

    Note:
    - Requires authentication through the use of the @login_required
    decorator.
    - The user_styling parameter should be a dictionary with styling
    preferences.
    - The user's styling information is stored in the "user_account"
    collection in the database.

    """
    # print("called styling")
    try:
        styling_request = request.json
        if styling_request:
            # print("got request")
            user_styling = styling_request.get("user_styling")
            if user_styling:
                # print("extracted value")
                # Connect to the database
                collection = openai_db["user_account"]
                email = current_user.email
                doc = collection.find_one({"email": email})

                if doc:
                    # print("doc found")
                    result = collection.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"user_styling": user_styling}})

                    if result.modified_count > 0:
                        # print("update success")
                        return jsonify({"success": True})

        return jsonify({"success": False})

    except Exception as e:
        print(f"update_user_styling Error: {e}")
        return jsonify({"success": False})


"""
if user:
            # Check the lock status of the user account
            account_lock = user.get("lock", True)

            unlocked = {"success": True, "lock": False, "Error": False}
            locked = {"success": True, "lock": True, "Error": False}

            return locked if account_lock else unlocked

        # Unable to get user data
        message = "Unable to retrieve user data from the database"
        return {"success": False, "Error": message, "e_server": False}

    except Exception as e:
        print(f"lock_status Error: {e}")
        message = "Sorry an error occured, try again latter."
        return {"success": False, "Error": message, "e_serverv": True}
"""


@app.route('/', endpoint="index_endpoint", methods=["GET"])
@login_required
async def index():
    """
    Render the index page.

    This route renders the index page, which includes user information
    and styling preferences.

    Method: GET

    Returns:
    - Rendered HTML template with user information and styling preferences.

    """
    # Check if the user's account is locked.
    obj = check_lock_status()
    # print(f"access obj = {str(obj)}")

    if not obj["access"]:
        # Get the user stylings
        user_styling = await get_user_styling_preference(
                current_user.email)

        return render_template(
                "index.html", tokens_count=obj["tokens"], obj=obj,
                user_styling=user_styling, thread_id="")

    # Save user tokens to the session. Used by the requests which do
    #   not make api calls
    session["user_tokens"] = get_remaining_user_tokens()

    # Add session data checker variables
    decide = 0
    obj = dict()
    reg_true = session.get("reg_success", False)

    # Set the reg_success variable back to false
    if reg_true:
        session["reg_success"] = False

    if "assistant_id" not in session:
        session["assistant_id"] = ""
        decide = 1
    if "sequence_id" not in session:
        session["sequence_id"] = 0
    if "thread_timer" not in session:
        session["thread_continuation_timer"] = False
    if "previous_thread_request" not in session:
        session["previous_thread_request"] = False
    if "UNIVERSAL_ERROR" not in session:
        session["UNIVERSAL_ERROR"] = False

    obj = await index_content_generator(decide)
    # print(f"user styling = {obj['user_styling']}")
    # print(f"session thread id = {session['thread_id']}")

    return render_template(
            "index.html", tokens_count=obj["tokens_count"],
            decide=decide, obj=obj["obj"], user_styling=obj["user_styling"],
            thread_id=session["thread_id"], reg_true=reg_true)


async def index_content_generator(decide=0):
    """
    Generate content for the index page.

    This function generates content for the index page, including user
    styling preferences, thread information, and token count.

    Parameters:
    - decide (int): Decision variable.

    Returns:
    - dict: Dictionary containing tokens_count, obj_data, and user_styling.

    """
    user_styling = await get_user_styling_preference(current_user.email)
    # print(f"\n\ncurrent_user = {current_user.email}\n\n")
    threads = []
    tokens_count = 0
    obj_data = {}

    if not threads:
        # print("not threads")
        session["assistant_id"] = ""
        session["thread_id"] = ""

    tokens_count = int(session["user_tokens"])
    # Apply thousand separator, comma
    tokens_count = f"{tokens_count:,}"

    check = await check_thread_availability()
    if check:
        obj_data = await thread_decider_func(
                "most_recent_thread")
        # print("session not empty")
    else:
        # print("creating a new thread")
        obj_data = await thread_decider_func("new_thread")

    # print(f"\n\nobj = {str(obj_data)}")

    obj = {
        "tokens_count": tokens_count,
        "obj": obj_data,
        "user_styling": user_styling,
        }
    return obj


async def check_thread_availability():
    """
    Check the availability of threads for the current user.

    This function checks if there are existing threads for the
    current user.

    Returns:
    - True if an existing thread is found, False otherwise.

    """
    try:
        email = current_user.email
        # print(f"check_thread_availability email = {email}")

        # Connect to the database
        collection = openai_db["thread_sequence"]

        # Check for the available threads
        thread = collection.find_one({"email": email},
                                     sort=[("_id", -1)])

        if thread:
            # Most recent thread found
            # Set the session variables
            session["thread_id"] = thread["thread_id"]
            session["assistant_id"] = thread["assistant_id"]
            # print("check_thread_availability True")
            return True
        else:
            # print("check_thread_availability problem getting thread")
            pass
        return False
    except Exception as e:
        print(f"check_thread_availability Error = {e}")
        return False


""" Assistant functions start """


@app.route('/zmc_assistant_data', methods=['POST'])
@login_required
async def zmc_assistant_data():
    """
    Handle requests related to ZMC Student Assistant data.

    This route processes various requests related to the ZMC Student Assistant,
    such as creating new threads, changing threads, handling image files,
    and interacting with the assistant.

    Method: POST

    Request Headers:
    - File-Type: Type of the file (e.g., Image)

    Form Data:
    - thread_status: Status of the thread (e.g., new)
    - thread_num: Number of the thread
    - prompt: Prompt for the assistant
    - thread_choice: Choice for thread handling
    - program_info: Information request flag (e.g., info_request)

    Returns (JSON):
    - Success response with relevant data or failure response with an
    error message.

    """
    try:
        # Check if the user's account is locked.
        obj = check_lock_status()

        if not obj["access"]:
            # Get the user stylings
            user_styling = await get_user_styling_preference(
                    current_user.email)

            return jsonify({'success': True,
                            'response_text': obj["response_text"],
                            "tokens_count": "0",
                            "thread_id": ""})

        prompt = ''

        file_type = request.headers.get('File-Type')
        thread_status = request.form.get('thread_status')
        thread_num = request.form.get('thread_num')
        prompt = request.form.get('prompt')
        thread_choice = request.form.get('thread_choice')
        info_request = request.form.get('program_info', None)
        # print(f"thread_choice = {thread_choice}")

        # Call thread_decider_func()
        if thread_choice:
            obj = await thread_decider_func(thread_choice)
            obj["thread_id"] = session["thread_id"]

            return jsonify(obj)

        if info_request == "info_request":
            # Call info_request_func()
            obj = await info_request_func()
            if obj["success"]:
                return jsonify({"success": True,
                                "response_text": obj["response_text"],
                                "tokens_count": obj["tokens_count"],
                                "thread_id": "no_sharing"})
            else:
                return jsonify({"success": False,
                                "response_text": obj["response_text"]})

        if thread_status == "new":
            # print("making new thread, thread status is new")
            # Call new_thread_request_func()
            obj = await new_thread_request_func(prompt, thread_status)
            if obj["success"]:
                return jsonify({"success": True,
                                "response_text": obj["response_text"],
                                "tokens_count": obj["tokens_count"],
                                "thread_id": session["thread_id"]})

        # Check if it is a thread change call
        if thread_num != "0":
            # print("thread num is not 0, so old thread invoked")
            # Call old_thread_request_func()
            obj = await old_thread_request_func(thread_num)
            if obj["success"]:
                return jsonify({"success": True,
                                "response_text": obj["response_text"],
                                "tokens_count": obj["tokens_count"],
                                "thread_id": session["thread_id"]})

        if file_type == "Image":
            # Get the image file from the request
            image_file = request.files['image']

            if image_file:
                if prompt:
                    prompt = prompt + text_generator(image_file)
                    # print(f"IMAGE TEXT = {str(prompt)}")
                else:
                    prompt = text_generator(image_file)
                    # print(f"IMAGE TEXT = {str(prompt)}")

        result = await flask_main(prompt, thread_status)
        # Get updated token count from the session. Already there is a
        #   function that has updated it.

        tokens = session.get("user_tokens", 0)
        if tokens:
            tokens = f"{int(tokens):,}"

        return jsonify({'success': True,
                        'response_text': result,
                        "tokens_count": tokens,
                        "thread_id": session["thread_id"]})

    except Exception as e:
        print(f"Error Thread = {e}")
        return jsonify({'success': False, 'error': str(e)})


async def thread_decider_func(thread_choice):
    if thread_choice == "new_thread":
        # print("making new thread, thread status is new")
        # Call new_thread_request_func()
        obj = await new_thread_request_func("new thread", "new")
        if obj["success"]:
            # Get threads
            threads = create_thread_array()

            return {"success": True,
                    "response_text": obj["response_text"],
                    "tokens_count": obj["tokens_count"],
                    "threads": threads, "decide": False}

    if thread_choice == "most_recent_thread":
        threads = create_thread_array()
        recent_thread = 1
        if len(threads):
            for thread in threads:
                if thread > recent_thread:
                    recent_thread = thread
            # Call old_thread_request_func()
            obj = await old_thread_request_func(recent_thread)
            if obj["success"]:
                return {"success": True,
                        "response_text": obj["response_text"],
                        "tokens_count": obj["tokens_count"],
                        "threads": threads, "decide": False}
        else:
            # Call new_thread_request_func()
            obj = await new_thread_request_func("new thread", "new")
            if obj["success"]:
                threads = create_thread_array()
                return {"success": True,
                        "response_text": obj["response_text"],
                        "tokens_count": obj["tokens_count"],
                        "threads": threads, "decide": False}


async def info_request_func():
    """
    Retrieve program information.

    This function retrieves information about the ZMC Student Assistant
    program.

    Returns:
    - dict: Success response with program information, tokens count,
    or failure response with an error message.

    """
    Error = None
    try:
        # Connect to the database
        collection = openai_db["program_intro"]
        result = collection.find({}, {"_id": 0})
        if result:
            for obj in result:
                # print(f"string = {str(obj.get('program_intro'))}")
                raw_program_info = r"{}".format(obj.get("program_intro"))
                # print(raw_program_info)
                tokens = session.get("user_tokens", 0)
                if not tokens:
                    tokens = get_remaining_user_tokens()
                    session["user_tokens"] = tokens

                tokens = f"{tokens:,}"
                obj = {
                    "success": True,
                    "response_text": raw_program_info,
                    "tokens_count": tokens,
                    }

                return obj

        else:
            Error = "Problem fetching program info"
    except Exception as e:
        Error = e
    obj = {
        "success": False,
        "response_text": Error,
        }
    return obj


async def new_thread_request_func(prompt, thread_status):
    """
    Handle a request to start a new thread.

    This function processes a request to start a new thread by providing a
    prompt to the assistant.

    Parameters:
    - prompt (str): Prompt for the assistant.
    - thread_status (str): Status of the thread (e.g., new).

    Returns:
    - dict: Success response with the assistant's response, tokens count,
    or failure response with an error message.

    """
    # check if it is a request to start a new thread
    prompt_token = await num_tokens_from_messages(prompt)
    prompt_token += 98  # Tokens for the Instructions sent to the assistant.

    # Save this value to the session for later retrieval
    session["instruction_prompt_tokens"] = prompt_token

    result = await flask_main(prompt, thread_status)
    # Get the user updated tokens from the database, already saved in
    #   the session
    tokens = session.get("user_tokens", 0)
    tokens = f"{int(tokens):,}"

    obj = {
        "success": True,
        "response_text": result,
        "tokens_count": tokens,
        }

    return obj


async def old_thread_request_func(thread_num):
    """
    Handle a request to switch to an old thread.

    This function processes a request to switch to an old thread based on
    the provided thread number.

    Parameters:
    - thread_num (str): Number of the thread.

    Returns:
    - dict: Success response with the assistant's response, tokens count,
    or failure response with an error message.

    """
    thread_data = shift_threads(thread_num)
    # Try retrieving token data feom the session
    tokens = int(session.get("user_tokens", 0))
    if not tokens:
        # Get tokens data from the database
        tokens = get_remaining_user_tokens()
        session["user_tokens"] = tokens
    tokens = f"{tokens:,}"
    # print(f"\n\n{tokens}\n\n")

    # Signal a previous thread has being requested for
    session["previous_thread_request"] = True

    # Call the function below to set the session variable with
    # the appropriate data so that the functions responsible
    # for token calculations can understand how to carry on
    # with their operations
    calculate_old_thread_tokens(session["thread_id"])

    obj = {
        "success": True,
        "response_text": thread_data,
        "tokens_count": tokens
        }

    return obj

""" Assistant functions end """


@app.route('/get_program_info', methods=['GET'])
@login_required
async def program_info_func():
    """
    Get program information.

    This route retrieves program information from MongoDB.

    Method: GET

    Returns (JSON):
    - Program information document.

    """
    try:
        # Check if the user's account is locked.
        obj = check_lock_status()

        if not obj["access"]:
            # Return lock message
            return jsonify({"program_intro": obj["response_text"]})

        # Connect to MongoDB
        collection = openai_db['program_intro']

        # Retrieve all documents from MongoDB
        document = collection.find_one({}, {"_id": 0})

        # Return JSON data to the client
        return jsonify(document)
    except Exception as e:
        print(f"program_info_func Error = {e}")
        return jsonify({"success": False, "Error": e})


""" flask main function start """


async def flask_main(prompt, thread_status):
    """
    Main function to interact with the Flask app and OpenAI.

    This function handles the main interaction with the Flask app and
    OpenAI based on the provided prompt and thread status.

    Parameters:
    - prompt (str): Prompt for the assistant.
    - thread_status (str): Status of the thread (e.g., active).

    Returns:
    - str: Constructed HTML for the response.

    """
    # print(f"thread status = {thread_status}")
    return_value = ""
    check = 0
    openai_data = None

    prompt_token = await num_tokens_from_messages(prompt)
    prompt_token += 98  # Tokens for the Instructions sent to the assistant.

    # Save this value to the session for later retrieval
    session["instruction_prompt_tokens"] = prompt_token

    # print(f"\n\n prompt tokens = {prompt_token}\n\n")

    if thread_status == "active" and "assistant_id" in session and session[
            "assistant_id"]:
        # print("Using session data, thread status is active")
        # Call thread_continuation_request_func()
        openai_data = await thread_continuation_request_func(prompt)
    else:
        # print("flask main creating new thread")
        # Call flask_main_new_thread_request_func()
        openai_data = await flask_main_new_thread_request_func(prompt)

    # Save data to the database
    openai_threads_messages_save(openai_data)

    # print(f"\n\nreturning: {return_value}\n\n")
    return construct_return_html()


async def thread_continuation_request_func(prompt):
    """
    Handle a request for thread continuation.

    This function processes a request for thread continuation based on
    the provided prompt.

    Parameters:
    - prompt (str): Prompt for thread continuation.

    Returns:
    - dict: Constructed data for saving in the database.

    """
    # Update thread timer
    session["thread_continuation_timer"] = False  # Signals thread continuation
    # print(f"thread_continuation_request_func prompt = {prompt}")

    # print("Using session assistant and thread")
    assistant_id = session["assistant_id"]
    thread_id = session["thread_id"]
    check = 1
    thread, run = await create_thread_and_run(assistant_id, prompt, thread_id)
    run = await wait_on_run(run, thread_id, check)
    return_value = await extract_openai_message(
            await get_response(thread_id, check))
    return_value = await clean_content(return_value)

    # Replace the backslashes with "&bksl;"
    return_value_clean = await replace_backslash_latex(return_value)
    # Get the number of tokens consumed by the message from this call
    message_tokens = session.get("currently_used_tokens", 0)
    # print(f"\n\nreturn_value = {return_value_clean}")

    # Define an odject to save in the database
    prompt = (
            """<h3 style="margin-top: 20px; color: #F4CE14;">"""
            + f"""{current_user.student_name}</h3>"""
            + f"""<p style="color: #7ED7C1;">{prompt}</p>"""
            )
    return_value = (
            """<h3 style="margin-top: 20px; color: orange;">"""
            + f"""Assistant</h3>{return_value_clean}"""
            )

    openai_data = {
            "email": current_user.email,
            "assistant_id": assistant_id,
            "thread_id": thread_id,
            "timestamp": int(time.time()),
            "prompt": prompt,
            "message": return_value,
            "tokens_consumed": message_tokens,
        }
    return openai_data


async def flask_main_new_thread_request_func(prompt):
    """
    Handle a request to create a new thread.

    This function processes a request to create a new thread based on the
    provided prompt.

    Parameters:
    - prompt (str): Prompt for the new thread.

    Returns:
    - dict: Constructed data for saving in the database.

    """
    # Update thread timer
    session["thread_continuation_timer"] = True  # Signals new thread created
    check = 0

    assistant = await assistant_creator()
    session["assistant_id"] = assistant.id
    thread, run = await create_thread_and_run(assistant.id, prompt)

    session["thread_id"] = thread.id
    run = await wait_on_run(run, thread, check)
    return_value = await extract_openai_message(
            await get_response(thread, check))
    return_value = await clean_content(return_value)

    # Replace the backslashes with "&bksl;"
    return_value_clean = await replace_backslash_latex(return_value)

    # Get the number of tokens consumed by the message from this call
    tokens_consumed = session.get("currently_used_tokens", 0)

    # print(f"\n\nreturn_value = {return_value_clean}")

    prompt = (
            """<h3 style="margin-top: 20px; color: #F4CE14;">"""
            + f"""{current_user.student_name}</h3>"""
            + f"""<p style="color: #7ED7C1;">{prompt}</p>"""
            )
    return_value = (
            f"""<h3 style="margin-top: 20px; color: orange;">"""
            + f"""Assistant</h3>{return_value_clean}"""
            )

    openai_data = {
            "email": current_user.email,
            "assistant_id": assistant.id,
            "thread_id": thread.id,
            "timestamp": int(time.time()),
            "prompt": prompt,
            "message": return_value,
            "tokens_consumed": tokens_consumed,
            }
    return openai_data


def construct_return_html():
    """
    Construct HTML for the response.

    This function constructs HTML by retrieving thread information from
    the database.

    Returns:
    - str: Constructed HTML.

    """
    try:
        string = ''

        # Connect to the database
        collection = openai_db["openai_threads"]

        thread_id = session.get('thread_id')
        email = current_user.email

        # Construct the query
        query = {"$and": [{"thread_id": thread_id}, {"email": email}]}

        # Execute the query
        threads = collection.find(query)
        # print(threads)

        if threads:
            for thread in threads:
                string += thread['prompt'] + thread['message']
            # print(f"\n\nstring = {string}")
            return string
        return "<p>problem getting solution</p>"
    except Exception as e:
        print(f"construct_return_html Error: {e}")
        return f"""<p style='color: #ff0000;>{e}</p>"""


""" flask main function end """
""" content sharing routes and functions """


@login_required
@app.route('/enable_content_sharing', methods=['POST'])
async def enable_content_sharing():
    """
    Route for enabling content sharing.

    This route serves as the driver for enabling content sharing.
    It orchestrates various functions to:
        - Retrieve data from the user's thread.
        - Save the data in the database, making it accessible to all students.
        - Handle the process of sending emails to tagged students.
    """

    # Check if the user's account is locked.
    obj = check_lock_status()

    if not obj["access"]:
        # Return lock message
        return jsonify({"success": False, "message": obj["response_text"]})

    content_title = request.form.get('content_title', None)
    description = request.form.get('description', None)
    tagged_emails = request.form.get('tagged_emails', None)
    thread_id = request.form.get('thread_id', None)
    # thread_id = "thread_pajTeEykhHCWAz6VTLK0OQSy"
    # print(f"\n\n\nthread id = {thread_id}\n\n")

    if content_title and len(content_title) > 20:
        message = "Consider a smaller title as the provided one is too large."
        return jsonify({"success": False, "message": message})
    if description and len(description) > 200:
        message = ("Consider a smaller description asthe provided"
                   + " one is too large."
                   )
        return jsonify({"success": False, "message": message})

    # Get the thread conversation
    conversation = await unlock_content_for_sharing(thread_id)
    # print(f"\n\nconversation = {conversation}\n\n")

    if conversation != "thread_not_found" and conversation != "error":
        # construct share content introduction
        introduction = construct_share_content_intro(
                content_title, description)

        # Concatenate them to get complete message response
        shared_content = introduction + conversation

        # Save shared content
        result = await save_shared_content(
                content_title, shared_content, tagged_emails)

        message = ""
        check = 0
        if result and result != "no_tagged_emails":
            message = "Shared content set successfully, all emails sent"
            check = 1
        elif result and result == "no_tagged_emails":
            message = "Shared content set successfully"
            check = 1
        elif result and result == "problem_sending_emails":
            message = ("Shared content set successfully but, "
                       + "a problem occured while sending some emails"
                       )
            check = 1
        if check:
            return jsonify({"success": True, "message": message})

        message = "Failed to save the shared content in the database"
        return jsonify({"success": False, "message": message})

    else:
        message = "Problem retrieving content from your account"
        return jsonify({"success": False, "message": message})


@app.route('/get_shared_content', methods=["POST"])
@login_required
async def get_shared_content():
    # print("\n\n Get shared content function called")
    """
    Handles requests for retrieving shared content.

    This route processes requests related to the retrieval of shared
    content. The shared content is extracted and sent to the student.
    """

    try:
        # Check if the user's account is locked.
        obj = check_lock_status()
        print(f"access obj = {str(obj)}")

        if not obj["access"]:
            # Return lock message
            return jsonify({"success": False,
                            "message": obj["response_text"]})

        shared_id = request.form.get('shared_id', None)

        # Connect to the database
        collection = openai_db["shared_content"]

        # Retrieve shared content
        if shared_id:
            result = collection.find_one({"shared_id": shared_id})
            if result:
                message = "shared content retrieved successfully"
                return jsonify(
                        {"success": True,
                         "shared_content": result["shared_content"],
                         "message": message, "used_shared_id": True})

            message = "Sorry, the shared content with that id was not found."
            return jsonify({"success": False, "message": message})

        # Count the number of documents in the collection
        document_count = collection.count_documents({})

        # Set the desired number of random documents to retrieve
        desired_count = min(document_count, 10)

        # Use $sample to randomly select documents
        random_documents = collection.aggregate([
            {"$sample": {"size": desired_count}}
            ])

        # Retrieve titles from the extracted documents
        list_objs = []
        for doc in random_documents:
            obj = {"shared_id": doc["shared_id"], "title": doc["title"]}
            list_objs.append(obj)

        message = "shared content retrieved successfully"
        return jsonify({"success": True, "list_objs": list_objs,
                        "used_shared_id": False, "message": message})

    except Exception as e:
        print(f"get_shared_content Error = {e}")
        return jsonify({"success": False, "message": e})


@login_required
@app.route("/generate_pdf_route", methods=["POST"])
async def generate_pdf_route():
    # print("\n\n\ngenerate_pdf_route called\n\n\n")
    try:
        # Check if the user's account is locked.
        obj = check_lock_status()

        if not obj["access"]:
            # Return lock message
            return jsonify({"message": obj["response_text"]})

        obj = {}
        pdf_path = None

        default_pdf = request.form.get("default_pdf", None)
        obj["letter_spacing"] = request.form.get("letter_spacing", None)
        obj["font_size"] = request.form.get("font_size", None)
        obj["text_color"] = request.form.get("text_color", None)
        obj["page_margins"] = request.form.get("page_margins", None)
        obj["background_color"] = request.form.get("background_color", None)
        obj["span_color"] = request.form.get("span_color", None)
        obj["font_family"] = request.form.get("font_family", None)

        print(f"object = {str(obj)}")

        # Validate user input
        result = validate_pdf_request_data(obj)

        pdf_header = ("""<h1 style="color: lime; font-size: 24px;">"""
                      + """ZMC STUDENT ASSISTANT</h1>"""
                      + """<p style="color: lime;">"""
                      + """Developer: Julius Mwangi</p>"""
                      + """<p style="color: lime;">"""
                      + """Contact: juliusmwasstech@gmail.com</p>"""
                      + """<p style="color: lime;"""
                      + """margin-bottom: 150px;">Happy learning</p>"""
                      )

        if not result or default_pdf:
            html_content = pdf_header + construct_return_html()
            obj = generate_pdf_styler_obj(html_content)
            pdf_path = await code_to_pdf(obj)
            # print(f"pdf name = {pdf_path}")
        else:
            html_content = pdf_header + construct_return_html()
            obj = generate_pdf_styler_obj(html_content, obj)
            pdf_path = await code_to_pdf(obj)
            # print(f"pdf name = {pdf_path}")

        # Return the PDF as a downloadable file
        with open(pdf_path, 'rb') as pdf_file:
            response = Response(pdf_file.read(),
                                content_type='application/pdf')
            filename = ("zmc_student_assistant"
                        + str(generate_key()) + ".pdf"
                        )
            fname = f"inline; filename={filename}"
            response.headers['Content-Disposition'] = fname

        # Delete the PDF file immediately after sending
        os.remove(pdf_path)

        return response
    except Exception as e:
        print(f"generate_pdf_route Error = {e}")
        return jsonify({"message": "error"})


async def unlock_content_for_sharing(thread_id):
    """
    Extracts shared content from the specified thread.

    Args:
    - thread_id (str): The identifier of the thread containing the
    shared content.

    Returns:
    - str: Extracted shared content.

    If the specified thread is found, this function extracts and returns
    the shared content. Otherwise, it returns "thread_not_found".
    """

    try:
        # Initialise a variable to hold thread converstion messages
        thread_messages = ""

        # Make database connection
        collection = openai_db["openai_threads"]

        # Get the current Thread of the calling user
        result = collection.find({"thread_id": thread_id})

        if result:
            for doc in result:
                # print(f"""\nprompt = {doc["prompt"]}\n""")
                content = doc["prompt"] + doc["message"]
                thread_messages = thread_messages + content
            # print(f"\n\nShared Content = {thread_messages}\n\n")
            return thread_messages
        return "thread_not_found"

    except Exception as e:
        print(f"unlock_content_for_sharing Error = {e}")
        return "error"


def construct_share_content_intro(content_title, description):
    """
    Generates the introductory part of the shared content.

    Args:
    - content_title (str): The title of the shared content.
    - description (str): Description of the shared content.

    Returns:
    - str: The constructed introductory part of the shared content.

    This function takes the title and description of the shared content
    and generates the introductory HTML code.
    """

    intro = """<h3 style="margin-top: 20px; color: #CFF800;">"""
    intro2 = f"""{content_title}</h3>"""
    intro3 = f"""<p style="color: #E7C582;">{description}</p>"""
    intro4 = """<h3 style="margin-top: 20px; color: #CFF800;">"""
    intro5 = """Shared Content Starts Here</h3>"""

    return intro + intro2 + intro3 + intro4 + intro5


async def send_those_emails(tagged_emails, shared_id):
    """
    Sends emails to the tagged students.

    Args:
    - tagged_emails (str): Space separated string of tagged student emails.
    - shared_id (str): Identifier of the shared content.

    Returns:
    - Union[bool, str]: True if all emails are sent successfully, False
    otherwise. "no_tagged_emails" if no tagged emails are provided.

    This function extracts emails from the given string, sends codes via
    email, and returns the success status.
    """

    if tagged_emails:
        # Extract all emails
        extracted_emails = extract_emails(tagged_emails)

        # Initiate a variable to keep track of the sent emails
        count = 0

        for email in extracted_emails:
            result = await send_code_by_email(email, shared_id)
            if result:
                count += 1

        if count >= len(extracted_emails):
            return True
        return False
    return "no_tagged_emails"


def extract_emails(tagged_emails):
    """
    Extracts all email addresses from the given text.

    Args:
    - tagged_emails (str): Text containing email addresses.

    Returns:
    - List[str]: List of extracted email addresses.

    This function uses a regular expression to extract and return all
    email addresses from the given text.
    """

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, tagged_emails)
    return emails


async def save_shared_content(content_title, shared_content, emails):
    """
    Saves shared content in the database and sends emails to tagged
    students.

    Args:
    - content_title (str): Title of the shared content.
    - shared_content (str): The shared content.
    - emails (str): Comma-separated string of tagged student emails.

    Returns:
        - Union[bool, str]: True if shared content is saved and emails are
        sent successfully."no_tagged_emails" if no tagged emails are provided.
        "problem_sending_emails" if there is an issue while sending emails.
        False otherwise.

    This function saves the shared content in the database, generates a
    share id, and sends emails to tagged students.
    """
    try:
        # Connect to the database
        collection = openai_db["shared_content"]

        # Get the current timestamp
        timestamp = int(time.time())

        # Add timestamp to the content title for uniqueness
        content_title = content_title + "©" + str(timestamp)

        # Generate a share id
        shared_id = generate_random_string()

        obj = {
            "title": content_title,
            "shared_content": shared_content,
            "shared_id": shared_id
            }

        # Save the shared content in the database
        result = collection.insert_one(obj)

        if result and result.inserted_id:
            # Check and send emails incase there is
            result = await send_those_emails(emails, shared_id)
            if result and result != "no_tagged_emails":
                return True
            elif result and result == "no_tagged_emails":
                return "no_tagged_emails"
            return "problem_sending_emails"

            return True
        return False
    except Exception as e:
        print(f"save_shared_content Error = {e}")
        return False


def generate_random_string():
    """
    Generates a random string.

    Returns:
    - str: Randomly generated string.

    This function generates a random string of length 12 containing letters
    (both uppercase and lowercase) and digits.
    """

    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(12))
    return random_string


""" content sharing routes and functions """


if __name__ == '__main__':
    app.run(debug=True, port=5020)
