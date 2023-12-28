from flask import Blueprint, Flask, request, render_template, session, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import asyncio
from flask.sessions import SecureCookieSessionInterface

""" Import app, openai_db, openai_client and development blueprint """
from extensions import app, openai_db, login_manager
from development_assisting_route import development_blueprint

""" import openai functions """
from openai_functions import assistant_creator, wait_on_run
from openai_functions import submit_message, get_response
from openai_functions import create_thread_and_run, extract_openai_message

""" Import models and their functions """
from models_functions import get_user_from_db

""" Import general functions """
from general_functions import openai_threads_messages_save, text_generator
from general_functions import num_tokens_from_messages, clean_content
from general_functions import save_thread_number, create_thread_array
from general_functions import shift_threads, get_thread_data, get_user_styling_preference
from general_functions import replace_backslash_latex, reverse_replace_backslash_latex

""" Import token functions """
from token_functions import token_updating_func, calculate_old_thread_tokens
from token_functions import get_remaining_user_tokens

""" import email functions """
from email_functions import send_shared_id_email


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


# Start tracing
tracemalloc.start()

#MATH_ASSISTANT_ID = '';
#mathematical expression using LaTeX syntax

# Register the 'development_blueprint' with the app without the prefix
app.register_blueprint(development_blueprint, url_prefix='')


@login_manager.user_loader
def load_user(email):
    return get_user_from_db(email)


@app.route('/update_user_styling', methods=["POST"])
@login_required
def update_user_styling():
    print("called styling")
    try:
        styling_request = request.json
        if styling_request:
            print("got request")
            user_styling = styling_request.get("user_styling")
            if user_styling:
                print("extracted value")
                # Connect to the database
                collection = openai_db["user_account"]
                email = current_user.email
                doc = collection.find_one({"email": email})

                if doc:
                    print("doc found")
                    result = collection.update_one({"_id": doc["_id"]}, {"$set": {"user_styling": user_styling}})
                    if result.modified_count > 0:
                        print("update success")
                        return jsonify({"success": True})
        
        return jsonify({"success": False})
    
    except Exception as e:
        print(f"update_user_styling Error: {e}")
        return jsonify({"success": False})


@app.route('/', endpoint="index_endpoint", methods=["GET"])
@login_required
async def index():
    # Save user tokens to the session. Used by the requests which do not make api calls
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

    return render_template(
            "index.html", threads=obj["threads"], tokens_count=obj["tokens_count"],
            decide=decide, obj=obj["obj"], user_styling=obj["user_styling"],
            thread_id=session["thread_id"], reg_true=reg_true)


async def index_content_generator(decide=0):
    user_styling = await get_user_styling_preference(current_user.email)
    print(f"\n\ncurrent_user = {current_user.email}\n\n")
    threads = []
    tokens_count = 0
    obj_data = {}

    if not threads:
        print("not threads")
        session["assistant_id"] = ""
        session["thread_id"] = ""

    """if session.get("user_tokens", 0) == 0:
        # connect to the database
        collection = openai_db["user_account"]
        result = collection.find_one({"email": current_user.email})
        if result:
            session["user_tokens"] = result["tokens"]"""

    tokens_count = int(session["user_tokens"])
    # Apply thousand separator, comma
    tokens_count = f"{tokens_count:,}"

    if not decide:
        obj_data = await thread_decider_func("most_recent_thread")
        print(f"\n\nobj = {str(obj_data)}")
        threads = create_thread_array()

    obj = {
        "threads": threads,
        "tokens_count": tokens_count,
        "obj": obj_data,
        "user_styling": user_styling,
        }
    return obj


""" Log in and sign up routes and functions start """

@app.route("/log_reg_template", endpoint="log_reg_endpoint", methods=["GET", "POST"])
def log_reg_template():
    return render_template("access.html", message="")


@app.route("/login_template", methods=["GET"])
def login_template():
    return render_template("login.html")


@app.route("/register_template", methods=["GET"])
def register_template():
    return render_template("register.html")


@app.route("/reset_password_template", methods=["GET"])
def reset_password_template():
    return render_template("recover.html")


# Registration route
@app.route('/register', endpoint="register_endpoint", methods=['POST'])
def process_data():
    #session.clear()
    if current_user.is_authenticated:
        # User is already logged in, redirect to another page
        return redirect(url_for('/'))

    # Handle form data
    signup_data = {
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "first_name": request.form.get('first-name'),
            "second_name": request.form.get('second-name'),
    }

    """ Check if the email already exists in the database """
    # Connect to the database
    collection = openai_db["user_account"]
    existing_user = collection.find_one({"email": signup_data["email"]})

    if existing_user:
        message = "The email address you provided is already in use."
        return render_template("access.html", message=message)


    # Save registration data to the session
    session['reg_details'] = signup_data

    # Call verification endpoint
    return redirect(url_for('verify_get_endpoint'))


# Verification route
@app.route('/verify_get', endpoint='verify_get_endpoint', methods=['GET'])
def verify_get():
    if current_user.is_authenticated:
        # User is already logged in, redirect to the index page
        return redirect(url_for('index.html'))

    # Generate verification key
    session['valid_key'] = generate_key()

    # Setup time the verification process has started
    session['start_time'] = time.time()

    """ Send verification code """
    #send_verification_code(rec_email, ver_key) # Email sending function
    print(f"\n\nverification key = {session['valid_key']}\n\n")

    # Render verify_details.html file
    return render_template('verify-details.html', key_code=1)


@app.route("/verify_post", methods=["POST"])
def verify_post():
    # Check if the form was submitted within the specified time
    elapsed_time = time.time() - int(session.get('start_time'))

    if elapsed_time > 320:
        message = "Verification key expired, try registration again"
        return render_template('access.html', message=message)

    # Retrieve the verification key
    ver_key = request.form.get('verification_code')
    print(f"\n\nver_key = {ver_key}\n\n")

    # Convert ver_key to an integer
    try:
        verification_code = int(ver_key)
    except Exception as e:
        message = "The verification key must only contain numbers"
        return render_template('access.html', message=message)

    # Confirm the key integrity
    if verification_code == session.get('valid_key'):
        # Call the registration proceed function
        result = registration_proceed()

        if result and result != "email_already_in_use":
            # Add the registration activation variable in the session.
            #   To be used by the '/' route to respond with a reg success message.
            session["reg_success"] = True

            # Do the redirection
            return redirect(url_for('index_endpoint'))

        elif result and result == "email_already_in_use":
            message = "That email address is already in use"
            return render_template("access.html", message=message)

        # An error occured
        message = "Couldn't finalize the registration, try again latter."
        return render_template("access.html", message=message)

    # Keys don't match
    message = "Could not verify, The entered key was not correct."
    return render_template('access.html', message=message)



# Function for completing the registration process
def registration_proceed():
    print("registration proceed called")
    reg_details = session.get('reg_details')

    """ Save the registration details in the database """
    # Connect to database
    collection = openai_db["user_account"]

    # Ensure email addresses are stored in lowercase for consistency.
    email = reg_details["email"].lower()

    # Hash password
    hashed_password = hash_password(reg_details["password"])

    # capitalise user names
    first_name_raw = reg_details["first_name"]
    first_name = first_name_raw.capitalize()

    second_name_raw = reg_details["second_name"]
    second_name = second_name_raw.capitalize()

    # Construct user full name
    student_name = first_name + " " + second_name

    # Create an object to store the user details which will be saved in the database
    obj = {
            "email": email,
            "password": hashed_password,
            "student_name": student_name,
            "tokens": 100000,
            "accumulating_tokens": 0,
            "lock": False,
            "user_styling": {"font_size": 15, "font_family": "Gruppo",
                             "text_color": "#29ADB2", "background_color": "#040D12"}
        }

    # Confirm there is no user already registered with that email address
    result = collection.find_one({"email": email})
    if result:
        return "email_already_in_use"
    
    # Save these details into the database
    result = collection.insert_one(obj)

    if result and result.inserted_id:
        # Create user instance
        user = get_user_from_db(obj["email"])

        # Login user
        login_user(user, remember=False)

        # Return the obtained object
        return True

    return None


# Login route
@app.route('/login', endpoint="login_endpoint", methods=['POST'])
def login():
    if current_user.is_authenticated:
        # User is already logged in, redirect to the index page
        return redirect(url_for('index_endpoint'))

    # Get the username and password from the form data
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    remember_me = request.form.get('remember_me', False)
    print(email)
    print(password)

    if not email or not password:
        message = "Please provide your logging details."
        return render_template("access.html", message=message)

    # Convert email into lowercase letters
    email = email.lower()

    # Query the user details from your database
    user = get_user_from_db(email)
    if not user:
        message = "Student with that email address doesn't exist"
        return render_template("access.html", message=message)

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        # Login the user using Flask-Login
        login_user(user, remember_me)
        return redirect(url_for('index_endpoint'))

    # If the credentials are incorrect, show the error message
    message = "Please verify your email or password; login failed."
    return render_template('access.html', message=message)


@app.route("/logout", endpoint="logout_endpoint", methods=["GET"])
@login_required
def logout():
    session.clear()
    logout_user()
    message = "Bye, see you back soon"
    return render_template("access.html", message=message)


@app.route("/reset_password_process", methods=["POST"])
async def reset_password_process():
    email = request.form.get("email", None)
    request_method = request.form.get("request_method")
    confirm_code = request.form.get("reset_code")

    if email and request_method and request_method == "get_reset_code":
        # Check if the user exists in the database
        collection = openai_db["user_account"]
        result = collection.find_one({"email": email})

        if not result:
            message = "That email address doesn't exist in our database"
            return render_template("access.html", message=message)

        reset_code = generate_key()
        print(f"reset_code = {reset_code}")

        # Save user email in the session
        session["email"] = email

        # Save reset code in the session
        collection = openai_db["key_integrity_check"]

        obj = {
            "email": email,
            "reset_code": reset_code,
            "verified": False
            }

        result = collection.insert_one(obj)
        if result and result.inserted_id > 0:
            # Send reset code to the client
            #result2 = send_verification_email(email, reset_code)
            #if result2:
            return render_template('verify-details.html', key_code=2)

        # An error Occured
        message = "Sorry, An error ocurred while sending the reset code."
        return render_template("access.html", message=message)

    if request_method and request_method == "confirm_reset_code":
        # Check if the provided reset code match with the one in the database.
        obj = await confirm_reset_code()

        if obj["success"]:
            return render_template("/change_password.html")
        else:
            return render_template("/access.html", message=obj["error"])


async def confirm_reset_code():
    # Variable to keep track of any arising error.
    error = ""

    try:
        # Get the reset code saved earlier in the database
        collection = openai_db["key_integrity_check"]
        reset_data = collection.find_one({"email": session["email"]})
        if reset_data:
            if int(confirm_code) == reset_data["reset_code"] :
                obj = {
                    "verified": True
                    }
                result = collection.update_one({"email": session["email"]}, {"$set": obj})
                if result and result.modified_count > 0:
                    return {"success": True}
                    return render_template("/change_password.html")
                else:
                    error = "Reset code verified status update failed."
            else:
                error = "The provided reset code is not correct."
        else:
            error = "Reset code expired, please begin the password reset process again."

    except Exception as e:
        error = e
    finally:
        return {"success": False, "error": error}

    

# Recovery route
@app.route('/reset_password_data', methods=['POST'])
def reset_password_data():
    # Get the username and password from the form data
    email = request.form.get('email', None)
    new_password = request.form.get("password")

    if not email or not new_password:
        message = "Please provide email as well as the new password; reset failed."
        return render_template("access.html", message=message)

    # Query the user details from your database
    user = get_user_from_db(email)

    # Check reset code verification status before proceeding
    collection = openai_db["key_integrity_check"]
    reset_data = collection.find_one({"email": email})
    verified_status = reset_data["verified"]

    if verified_status and user and user.email == email:
        # Delete the reset code information from the database
        collection.delete_one({"email": email})

        # Hash the new password
        hashed_password = hash_password(new_password)
        print(f"new_password: {new_password}")

        # Update the user's password
        collection2 = openai_db["user_account"]
        obj = {"password": hashed_password}
        result = collection2.update_one({"email": email}, {"$set": obj})
        if result and result.modified_count > 0:
            return render_template("/access.html", message="Sign in with your new password.")



# Function for generating verification key
def generate_key():
    """
    Generates a key for account registration details verification
    """
    # Generate a random verification key
    key_array = [random.randint(1, 9) for _ in range(4)]

    # Convert the key_array to a single integer
    str_key = ''.join(map(str,key_array))
    key = int(str_key)
    return key


# Function for hashing password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            salt)
    return hashed_password


""" Log in and sign up routes and functions end """


""" Assistant functions start """


@app.route('/zmc_assistant_data', methods=['POST'])
@login_required
async def zmc_assistant_data():
    try:
        prompt = ''

        file_type = request.headers.get('File-Type')
        thread_status = request.form.get('thread_status')
        thread_num = request.form.get('thread_num')
        prompt = request.form.get('prompt')
        thread_choice = request.form.get('thread_choice')
        info_request = request.form.get('program_info', None)
        print(f"thread_choice = {thread_choice}")

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
            print("making new thread, thread status is new")
            # Call new_thread_request_func()
            obj = await new_thread_request_func(prompt, thread_status)
            if obj["success"]:
                return jsonify({"success": True,
                                "response_text": obj["response_text"],
                                "tokens_count": obj["tokens_count"],
                                "thread_id": session["thread_id"]})

        # Check if it is a thread change call
        if thread_num != "0":
            print("thread num is not 0, so old thread invoked")
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
                    print(f"IMAGE TEXT = {str(prompt)}")
                else:
                    prompt = text_generator(image_file)
                    print(f"IMAGE TEXT = {str(prompt)}")

        result = await flask_main(prompt, thread_status)
        # Get updated token count from the session. Already there is a function that has updated it.

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
        print("making new thread, thread status is new")
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
    Error = None
    try:
        # Connect to the database
        collection = openai_db["program_intro"]
        result = collection.find({},{"_id": 0})
        if result:
            for obj in result:
                #print(f"string = {str(obj.get('program_intro'))}")
                raw_program_info = r"{}".format(obj.get("program_intro"))
                print(raw_program_info)
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
    # check if it is a request to start a new thread
    prompt_token = await num_tokens_from_messages(prompt)
    prompt_token += 98 # Tokens for the Instructions sent to the assistant.

    # Save this value to the session for later retrieval
    session["instruction_prompt_tokens"] = prompt_token

    result = await flask_main(prompt, thread_status)
    # Get the user updated tokens from the database, already saved in the session
    tokens = session.get("user_tokens", 0)
    tokens = f"{int(tokens):,}"

    obj = {
        "success": True,
        "response_text": result,
        "tokens_count": tokens,
        }

    return obj


async def old_thread_request_func(thread_num):
    thread_data = shift_threads(thread_num)
    # Try retrieving token data feom the session
    tokens = int(session.get("user_tokens", 0))
    if not tokens:
        # Get tokens data from the database
        tokens = get_remaining_user_tokens()
        session["user_tokens"] = tokens
    tokens = f"{tokens:,}"
    print(f"\n\n{tokens}\n\n")

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
    try:
        # Connect to MongoDB
        collection = openai_db['program_intro']

        print("called")

        # Retrieve all documents from MongoDB
        document = collection.find_one({}, {"_id": 0})

        # Return JSON data to the client
        return jsonify(document)
    except Exception as e:
        print(f"program_info_func Error = {e}")
        return jsonify({"success": False, "Error": e})


""" flask main function start """

async def flask_main(prompt, thread_status):
    print(f"thread status = {thread_status}")
    return_value = ""
    check = 0
    openai_data = None

    prompt_token = await num_tokens_from_messages(prompt)
    prompt_token += 98 # Tokens for the Instructions sent to the assistant.

    # Save this value to the session for later retrieval
    session["instruction_prompt_tokens"] = prompt_token

    print(f"\n\n prompt tokens = {prompt_token}\n\n")

    if thread_status == "active" and "assistant_id" in session and session["assistant_id"]:
        print("Using session data, thread status is active")
        # Call thread_continuation_request_func()
        openai_data = await thread_continuation_request_func(prompt)
    else:
        print("flask main creating new thread")
        # Call flask_main_new_thread_request_func()
        openai_data = await flask_main_new_thread_request_func(prompt)

    # Save data to the database
    openai_threads_messages_save(openai_data)

    #print(f"\n\nreturning: {return_value}\n\n")
    return construct_return_html()

async def thread_continuation_request_func(prompt):
    # Update thread timer
    session["thread_continuation_timer"] = False # Signals thread continuation
    print(f"thread_continuation_request_func prompt = {prompt}")

    print("Using session assistant and thread")
    assistant_id = session["assistant_id"]
    thread_id = session["thread_id"]
    check = 1
    thread, run = await create_thread_and_run(assistant_id, prompt, thread_id)
    run = await wait_on_run(run, thread_id, check)
    return_value = await extract_openai_message(await get_response(thread_id, check))
    return_value = await clean_content(return_value)

    # Replace the backslashes with "&bksl;"
    return_value_clean = await replace_backslash_latex(return_value)
    # Get the number of tokens consumed by the message from this call
    message_tokens = session.get("currently_used_tokens", 0)
    print(f"\n\nreturn_value = {return_value_clean}")

    # Define an odject to save in the database
    prompt =f"""<h3 style="margin-top: 20px; color: #F4CE14;">User</h3><p style="color: #7ED7C1;">{prompt}</p>"""
    return_value = f"""<h3 style="margin-top: 20px; color: orange;">Assistant</h3>{return_value_clean}"""
    openai_data = {
            "assistant_id": assistant_id,
            "thread_id": thread_id,
            "timestamp": int(time.time()),
            "prompt": prompt,
            "message": return_value,
            "tokens_consumed": message_tokens,
        }
    return openai_data

async def flask_main_new_thread_request_func(prompt):
    # Update thread timer
    session["thread_continuation_timer"] = True # Signals new thread created
    check = 0

    assistant = await assistant_creator()
    #MATH_ASSISTANT_ID = assistant.id
    session["assistant_id"] = assistant.id
    thread, run = await create_thread_and_run(assistant.id, prompt)

    session["thread_id"] = thread.id
    run = await wait_on_run(run, thread, check)
    return_value = await extract_openai_message(await get_response(thread, check))
    return_value = await clean_content(return_value)

    # Replace the backslashes with "&bksl;"
    return_value_clean = await replace_backslash_latex(return_value)

    # Get the number of tokens consumed by the message from this call
    tokens_consumed = session.get("currently_used_tokens", 0)

    print(f"\n\nreturn_value = {return_value_clean}")

    prompt =f"""<h3 style="margin-top: 20px; color: #F4CE14;">User</h3><p style="color: #7ED7C1;">{prompt}</p>"""
    return_value = f"""<h3 style="margin-top: 20px; color: orange;
">Assistant</h3>{return_value_clean}"""
    openai_data = {
            "assistant_id": assistant.id,
            "thread_id": thread.id,
            "timestamp": int(time.time()),
            "prompt": prompt,
            "message": return_value,
            "tokens_consumed": tokens_consumed,
            }
    return openai_data

def construct_return_html():
    try:
        string = ''

        # Connect to the database
        collection = openai_db["openai_threads"]

        # Fetch all user threads
        thread_id = session.get('thread_id')

        threads = collection.find({"thread_id": thread_id})

        if threads:
            for thread in threads:
                string += thread['prompt'] + thread['message']
            #print(f"\n\nstring = {string}")
            return string
        return "<p>problem getting solution</p>"
    except Exception as e:
        print(f"construct_return_html Error: {e}")
        return f"""<p style='color: #ff0000;>{e}</p>"""

""" flask main function end """


""" content sharing routes and functions """

# Route for enabling content sharing
@login_required
@app.route('/enable_content_sharing', methods=['POST'])
async def enable_content_sharing():
    """
    This is the driver route.
    It calls all the functions involved in enabling content sharing.
    Retrieves the data from the user's thread and saves it on the
    database where it will be accessible to all students.
    It is also responsible for sending emails to the tagged students.
    """

    content_title = request.form.get('content_title', None)
    description = request.form.get('description', None)
    tagged_emails = request.form.get('tagged_emails', None)
    thread_id = request.form.get('thread_id', None)
    #thread_id = "thread_pajTeEykhHCWAz6VTLK0OQSy"
    print(f"\n\n\nthread id = {thread_id}\n\n")

    if content_title and len(content_title) > 20:
        message = "Consider a smaller title as the provided one is too large."
        return jsonify({"success": False, "message": message})
    if description and len(description) > 200:
        message = "Consider a smaller description asthe providedone is too large."
        return jsonify({"success": False, "message": message})

    # Get the thread conversation
    conversation = await unlock_content_for_sharing(thread_id)
    print(f"\n\nconversation = {conversation}\n\n")

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
            message = "Shared content set successfully but, a problem occured while sending some emails"
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
    print("\n\n Get shared content function called")
    """
    Receives the requests related to retrieval of the shared content.
    Shared content will be extracted and sent to the student.
    """

    try:
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
            { "$sample": { "size": desired_count } }
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


async def unlock_content_for_sharing(thread_id):
    """
    The content the students wants to share will be extracted here.
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
                print(f"""\nprompt = {doc["prompt"]}\n""")
                content = doc["prompt"] + doc["message"]
                thread_messages = thread_messages + content
            print(f"\n\nShared Content = {thread_messages}\n\n")
            return thread_messages
        return "thread_not_found"

    except Exception as e:
        print(f"unlock_content_for_sharing Error = {e}")
        return "error"


def construct_share_content_intro(content_title, description):
    """
    Generates the introductory part of the shared content.
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
    """

    if tagged_emails:
        # Extract all emails
        extracted_emails = extract_emails(tagged_emails)

        # Initiate a variable to keep track of the sent emails
        count = 0

        for email in extracted_emails:
            result = await send_shared_id_email(email, shared_id)
            if result:
                count += 1

        if count >= len(extracted_emails):
            return True
        return False
    return "no_tagged_emails"


def extract_emails(tagged_emails):
    """
    Extracts all email addresses from the given text
    """

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, tagged_emails)
    return emails


async def save_shared_content(content_title, shared_content, emails):
    """
    Shared content is added to the database here.
    It will be available to all students.
    """
    try:
        # Connect to the database
        collection = openai_db["shared_content"]

        # Get the current timestamp
        timestamp = int(time.time())

        # Add timestamp to the content title for uniqueness
        content_title = content_title + "©"+ str(timestamp)

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
    This string will mostly be used as the share id
    """

    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(12))
    return random_string


""" content sharing routes and functions """


if __name__ == '__main__':
    app.run(debug=True, port=5020)
