from flask_login import UserMixin
from extensions import openai_db


class UserDetails(UserMixin):
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
                    student_name = user_data['student_name'],
                    user_styling = user_data['user_styling'],
                    tokens = user_data['tokens'],
                    accumulating_tokens = user_data['accumulating_tokens'],
                    lock = user_data['lock'],
                )
        return user
    except Exception as e:
        print(f"get_user_from_db Error: {e}")

    return None
