import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


"""
ZMC STUDENT ASSISTANT - EMAIL_FUNCTIONS MODULE

Module: email_functions

Developer: Julius Mwangi
Contact:
    - Email: juliusmwasstech@gmail.com

---

Disclaimer:
This project is a solo endeavor, with Julius Mwangi leading
all development efforts. Any inquiries, concerns, or collaboration
requests related to email functionality should be directed to the
provided contact email.

---

About

Welcome to the core of the ZMC Student Assistant - the `email_functions`
module. This module houses all the functions essential for sending emails
to our clients, expertly crafted by Julius Mwangi.

Developer Information

- Name: Julius Mwangi
- Contact:
  - Email: [juliusmwasstech@gmail.com]
            (mailto:juliusmwasstech@gmail.com)

Acknowledgments

Special thanks to the incredible ALX TEAM for their unwavering support
and guidance. Their influence has been instrumental in shaping my
journey as a software engineer, particularly in developing robust email
functionality.

---

Note to Developers:
Feel free to explore, contribute, or connect. Your expertise and feedback,
especially concerning email-related features, are highly valued and
appreciated!

Happy coding!
"""


# Load environment variables from config file
dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')
load_dotenv(dotenv_path)


# Function for sending shared ID to the user through email
async def send_code_by_email(rec_email, code, value=0):
    """
    Sends an email with a code or value to the specified recipient email
    address.

    Args:
    - rec_email (str): Recipient's email address.
    - code (str): Code or value to be sent in the email.
    - value (int, optional): Type of email content (
        0: Shared Content Id,
        1: Verify Your Account,
        2: Password Reset Code
    ).

    Returns:
    - bool: True if the email is sent successfully, False otherwise.

    This function sends an email using the Gmail SMTP server with the
    specified code or value to the recipient's email address.
    """
    print("\n\nSENDING EMAIL\n\n")
    # Get the email password from the environment variable
    password = os.getenv('EMAIL_PASSWORD')
    generated_body = build_email_body(code, value)

    # Sender email
    sender_email = "zambezimarketcenter@gmail.com"

    # Create an instance of MIMEMultipart
    message = MIMEMultipart()

    # Set the subject
    if not value:
        message['Subject'] = 'Shared Content Id'
    elif value == 1:
        message['Subject'] = 'Verify Your Account'
    elif value == 2:
        message['Subject'] = 'Password Reset Code'

    # Set the sender and recipient
    message['From'] = sender_email
    message['To'] = rec_email

    # Create an HTML message content
    html_content = """
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                /*background-color: #f0f0f0;*/
                background-color: black;
            }}
            h4 {{
                color: #333;
            }}
            span {{
                font-size: 18px;
                font-weight: bold;
                color: green;
            }}
            p {{
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        {}
    </body>
    </html>
    """.format(generated_body)  # Insert the generated body

    # Attach the HTML content as MIMEText
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)

    # Connect to the SMTP server and send the email
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Use TLS for secure connection
            server.login(sender_email, password)
            server.sendmail(sender_email, rec_email, message.as_string())
            print("email sent")
        return True
    except Exception as e:
        print(f"send_code_by_email Error = {e}")
        return False


# Function to determine the mail body based on the value passed to it
def build_email_body(code, value=0):
    """
    Builds the email body based on the provided code and value.

    Args:
    - code (str): Code or value to be included in the email body.
    - value (int, optional): Type of email content (
        0: Shared Content Id,
        1: Verify Your Account,
        2: Password Reset Code
    ).

    Returns:
    - str: The formatted email body.

    This function generates the email body based on the provided code and
    value, following the specified email content format.
    """

    body = f"""
    <p style="color:#1E90FF; font-weight:bold;">Dear Student,</p>
    <p>A new shared content has been created, and you have been tagged.
    <p>Use the shared ID provided below to retrieve the content
    on the <strong>ZMC Student Assistant</strong> website.
    </p><p>Our commitment is to make learning enjoyable.</p>

    <p><span>{code}</span></p>
    <p>Need further assistance? Feel free to reach us at
    zambezimarketcenter@gmail.com</p>
    <h4 style="color: #1E90FF;">Best regards,</h4>
    <h4 style="color: #1E90FF;">ZMC Student Assistant Team</h4>
    """
    body2 = f"""
    <p style="color:#1E90FF; font-weight:bold;">Dear Student,</p>
    <p>Welcome to ZMC Student Assistant, We are thrilled to have
    you on board</p>

    <p>Please use the following verification code to
    complete the registration process:</p>

    <p><span>{code}</span></p>

    <p>If you did not request this code or are not the intended
    recipient, please disregard this message.</p>

    <p>Need further assistance? Reach us at
    zambezimarketcenter@gmail.com</p>

    <h4 style="color: #1E90FF;">Best regards,</h4>

    <h4 style="color: #1E90FF;">ZMC Student Assistant Team</h4>
    """
    body3 = f"""
    <p style="color:#1E90FF; font-weight:bold;">Dear Student,</p>
    <p>We have received your password reset request at ZMC
    Student Assistant.</p>

    <p>Please use the following reset code to complete the
    password reset process:</p>

    <p><span>{code}</span></p>

    <p>If you did not initiate this password reset or are not the
    intended recipient, please disregard this message.</p>

    <p>Need further assistance? Reach us at
    zambezimarketcenter@gmail.com</p>

    <h4 style="color: #1E90FF;">Best regards,</h4>

    <h4 style="color: #1E90FF;">ZMC Student Assistant Team</h4>

    """
    if not value:
        return body
    elif value == 1:
        return body2
    elif value == 2:
        return body3
