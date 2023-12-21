from flask import Flask
from flask_login import LoginManager
from flask.sessions import SecureCookieSessionInterface
from openai import OpenAI
import os
from pymongo import MongoClient

# Create app
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'project_testing'
app.session_interface = SecureCookieSessionInterface()

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
