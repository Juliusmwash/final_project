from flask_login import UserMixin
from extensions import openai_db


class UserDetails(UserMixin):
    """
    Represents user details for authentication and tracking purposes.

    Args:
    - email (str): User's email address.
    - password (str): User's password.
    - student_name (str): User's name.
    - user_styling (str): User's styling information.
    - tokens (int): User's available tokens.
    - accumulating_tokens (int): User's accumulating tokens.
    - lock (object): Lock object for synchronization.

    Attributes:
    - email (str): User's email address.
    - password (str): User's password.
    - student_name (str): User's name.
    - user_styling (str): User's styling information.
    - tokens (int): User's available tokens.
    - accumulating_tokens (int): User's accumulating tokens.
    - lock (object): Lock object for synchronization.

    Methods:
    - get_id(): Returns the email as the identifier for Flask-Login.
    """
    def __init__(self,
                 email, password, student_name, user_styling, tokens,
                 accumulating_tokens, lock):
        self.email = email
        self.password = password
        self.student_name = student_name
        self.user_styling = user_styling
        self.tokens = tokens
        self.accumulating_tokens = accumulating_tokens
        self.lock = lock

    def get_id(self):
        return str(self.email)  # Return the email as the identifier


def get_user_from_db(email=None):
    """
    Retrieves user details from the database based on the email.

    Args:
    - email (str, optional): User's email address. Defaults to None.

    Returns:
    - UserDetails or None: User details if found, None otherwise.
    """
    try:
        user = None
        user_data = {}
        collection = openai_db['user_account']
        if email:
            user_data = collection.find_one({"email": email})
        if user_data:
            user = UserDetails(
                    email=user_data['email'],
                    password=user_data['password'],
                    student_name=user_data['student_name'],
                    user_styling=user_data['user_styling'],
                    tokens=user_data['tokens'],
                    accumulating_tokens=user_data['accumulating_tokens'],
                    lock=user_data['lock'],
                )
        return user
    except Exception as e:
        print(f"get_user_from_db Error: {e}")

    return None
