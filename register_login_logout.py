import time
import pymongo
import bcrypt

from flask import Blueprint, request, render_template, session
from flask import redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user
from flask_login import current_user, login_required
import asyncio

"""
Import app, openai_db, openai_client and development blueprint
Import models and their functions
Import general functions
Import email functions
"""

from extensions import app, openai_db, login_manager
from models_functions import get_user_from_db
from general_functions import generate_key, hash_password
from email_functions import send_code_by_email
from development_assisting_route import refuse_further_registrations


"""
ZMC STUDENT ASSISTANT - USER AUTHENTICATION MODULE

Module: register_login_logout.py

Developer: Julius Mwangi
Contact:
    - Email: juliusmwasstech@gmail.com

---

Disclaimer:
This project is a solo endeavor, with Julius Mwangi leading all
development efforts. For inquiries, concerns, or collaboration requests
related to user authentication, please direct them to the provided
contact email.

---

About

Welcome to the authentication hub of the ZMC Student Assistant - the
`register_login_logout.py` module. This module takes charge of seamless
user experiences, handling registration, login, logout, and password
recovery logics with finesse, expertly crafted by Julius Mwangi.

Developer Information

- Name: Julius Mwangi
- Contact:
  - Email: [juliusmwasstech@gmail.com]
            (mailto:juliusmwasstech@gmail.com)

Acknowledgments

Special thanks to the incredible ALX TEAM for their unwavering support
and guidance. Their influence has been instrumental in shaping my journey
as a software engineer, particularly in developing robust user
authentication functionalities.

---

Note to Developers:
Feel free to explore, contribute, or connect. Your insights and feedback,
especially regarding user authentication flows, are highly valued and
appreciated!

Happy coding!
"""


# Create a Blueprint for register, login, logout related routes
reg_log_blueprint = Blueprint('reg_log_blueprint', __name__)


@app.route("/log_reg_template", endpoint="log_reg_endpoint",
           methods=["GET", "POST"])
def log_reg_template():
    """
    Renders the log_reg_template page with the provided message.

    Returns:
    - Rendered HTML page with the log_reg_template.
    """
    return render_template("access.html", message="")


@app.route("/login_template", methods=["GET"])
def login_template():
    """
    Renders the login_template page.

    Returns:
    - Rendered HTML page with the login_template.
    """
    return render_template("login.html")


@app.route("/register_template", methods=["GET"])
def register_template():
    """
    Renders the register_template page.

    Returns:
    - Rendered HTML page with the register_template.
    """
    # Check the number of the registered users for the development sake
    result = refuse_further_registrations()

    if result:
        message = ("We're currently in development and not accepting new "
                   + "accounts at this time. Apologies for any "
                   + "inconvenience."
                   )
        return render_template("access.html", message=message)

    return render_template("register.html")


@app.route("/reset_password_template", methods=["GET"])
def reset_password_template():
    """
    Renders the reset_password_template page.

    Returns:
    - Rendered HTML page with the reset_password_template.
    """
    return render_template("recover.html")


# Registration route
@app.route('/register', endpoint="register_endpoint", methods=['POST'])
def process_data():
    """
    Processes registration data submitted via the registration form.

    Returns:
    - If the user is already authenticated, redirects to another page.
    - If the email already exists in the database, renders an error message.
    - If successful, saves registration data to the session and redirects
    to the verification endpoint.
    """
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
async def verify_get():
    """
    Handles the GET request for the verification route.

    Returns:
    - If the user is already authenticated, redirects to the index page.
    - Generates a verification key, sends it via email, and renders the
    verification details page.
    """
    if current_user.is_authenticated:
        # User is already logged in, redirect to the index page
        return redirect(url_for('index.html'))

    # Generate verification key
    ver_key = generate_key()
    session['valid_key'] = ver_key

    # Setup time the verification process has started
    session['start_time'] = time.time()

    """ Send verification code """
    email = session.get('reg_details')["email"]
    await send_code_by_email(email, ver_key, 1)
    print(f"\n\nverification key = {session['valid_key']}\n\n")

    # Render verify_details.html file
    return render_template('verify-details.html', key_code=1)


@app.route("/verify_post", methods=["POST"])
def verify_post():
    """
    Handles the POST request for the verification route.

    Returns:
    - If the elapsed time exceeds 320 seconds, renders an error message
    for an expired key.
    - Retrieves and validates the verification key, then proceeds with
    registration.
    """
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
            #   To be used by the '/' route to respond with a reg success
            #   message.
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
    """
    Completes the user registration process.

    Returns:
    - "email_already_in_use" if the email address is already registered.
    - True if the registration is successful.
    - None if an error occurs during the registration process.
    """
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

    # Create an object to store the user details which will be saved
    #   in the database
    obj = {
            "email": email,
            "password": hashed_password,
            "student_name": student_name,
            "tokens": 100000,
            "accumulating_tokens": 0,
            "lock": False,
            "user_styling": {"font_size": 15, "font_family": "Gruppo",
                             "text_color": "#29ADB2",
                             "background_color": "#040D12"}
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
    """
    Handles user login.

    Returns:
    - Redirects to the index page if the login is successful.
    - Renders the access.html template with an error message otherwise.
    """
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
        message = "Student with that email address doesn't exist."
        return render_template("access.html", message=message)

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        # Login the user using Flask-Login
        login_user(user, remember=remember_me)
        return redirect(url_for('index_endpoint'))

    # If the credentials are incorrect, show the error message
    message = "Incorrect password."
    return render_template('access.html', message=message)


@app.route("/logout", endpoint="logout_endpoint", methods=["GET"])
@login_required
def logout():
    """
    Handles user logout.

    Returns:
    - Renders the access.html template with a success message.
    """
    session.clear()
    logout_user()
    message = "Success bye, see you back soon"
    return render_template("access.html", message=message)


@app.route("/reset_password_process", methods=["POST"])
async def reset_password_process():
    """
    Handles the reset password process.

    Returns:
    - Renders the verify_reset_code.html template with a reset code.
    """
    print("reset password called")
    email = request.form.get("email", None)

    if email:
        email = email.lower()
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
        if result and result.inserted_id:
            print(f"inserted_id = {result.inserted_id}")
            # Send reset code to the client
            await send_code_by_email(email, reset_code, 2)
            return render_template('verify_reset_code.html', key_code=2)

        # An error Occured
        message = "Sorry, An error ocurred while sending the reset code."
        return render_template("access.html", message=message)


@app.route("/verify_password_reset", methods=["POST"])
async def verify_password_reset():
    """
    Verifies the provided password reset code.

    Returns:
    - Renders the change_password.html template upon success.
    - Renders the access.html template with an error message upon failure.
    """
    reset_code = request.form.get("reset_code", None)
    # Check if the provided reset code match with the one in the database.
    if reset_code:
        try:
            reset_code = int(reset_code)
        except Exception as e:
            message = "Only numbers allowed as the reset code"
            return render_template("access.html", message=message)

    obj = await confirm_reset_code(reset_code)
    print(f"obj = {str(obj)}")

    if obj["success"]:
        print("success true")
        return render_template("change_password.html")
    else:
        print("success false")
        return render_template("access.html", message=obj["error"])


async def confirm_reset_code(reset_code):
    """
    Confirms the provided password reset code.

    Args:
    - reset_code (int): The reset code provided by the user.

    Returns:
    - dict: {"success": True} upon successful verification.
            {"success": False, "error": error_message} upon failure.
    """
    print("confirm reset code called")
    # Variable to keep track of any arising error.
    error = ""
    success = False

    try:
        # Get the reset code saved earlier in the database
        collection = openai_db["key_integrity_check"]
        email = session["email"]
        reset_data = collection.find_one(
                {"email": email}, sort=[("_id", pymongo.DESCENDING)])

        if reset_data:
            print(f"reset code db = {reset_data['reset_code']}")
            if reset_code == reset_data["reset_code"]:
                obj = {
                    "verified": True
                    }
                result = collection.update_one(
                        {"email": session["email"]}, {"$set": obj})
                if result and result.modified_count > 0:
                    print("Reset code process success")
                    success = True
                else:
                    error = "Reset code verified status update failed."
            else:
                error = "The provided reset code is not correct."
        else:
            error = ("Reset code expired, please begin the password "
                     + "reset process again."
                     )

    except Exception as e:
        error = e
    finally:
        if success:
            return {"success": True}
        return {"success": False, "error": error}


# Recovery route
@app.route('/finalise_password_change', methods=['POST'])
def reset_password_data():
    """
    Finalizes the password change process.

    Returns:
    - str: HTML content with a success or error message.
    """
    # Get the username and password from the form data
    new_password = request.form.get("new_password")

    if not new_password:
        message = "Please provide a reset password; reset failed."
        return render_template("access.html", message=message)

    # Query the user details from your database
    email = session["email"]
    user = get_user_from_db(email)

    # Check reset code verification status before proceeding
    collection = openai_db["key_integrity_check"]
    reset_data = collection.find_one({"email": email})
    verified_status = reset_data["verified"]

    if verified_status and user and user.email == email:
        # Delete the reset code information from the database
        collection.delete_many({"email": email})

        # Hash the new password
        hashed_password = hash_password(new_password)
        print(f"new_password: {new_password}")

        # Update the user's password
        collection2 = openai_db["user_account"]
        obj = {"password": hashed_password}
        result = collection2.update_one({"email": email}, {"$set": obj})
        if result and result.modified_count > 0:
            message = "Success Sign in with your new password."
            return render_template("/access.html", message=message)
