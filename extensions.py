from flask import Flask
from flask_login import LoginManager
from flask.sessions import SecureCookieSessionInterface
from openai import OpenAI
import os
from pymongo import MongoClient
from datetime import timedelta

# Create app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'project_testing'
app.session_interface = SecureCookieSessionInterface()

# Set the default session duration to 20 hours
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

# Set the duration for the "Remember Me" cookie to 7 days
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=20)


login_manager = LoginManager(app)
login_manager.login_view = "log_reg_endpoint"

# Set up the MongoDB connection
openai_uri = os.environ.get('OPENAI_ADMIN_DATABASE_URI')
client = MongoClient(openai_uri)
openai_db = client['openaiDB']


api_key = os.environ.get('MY_OPENAI_API_KEY')
openai_client = OpenAI(api_key=api_key,)

"""
login_manager = LoginManager(app)
login_manager.login_view = 'login_endpoint'
"""
