import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

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
    <p>The shared ID provided below can be used to retrieve the content
    on the <strong>ZMC Student Assistant</strong> website.
    </p><p>Our commitment is to make learning enjoyable. Utilize the
    shared content to your advantage.</p>

    <p><span>{code}</span></p>
    <p>Thank you for choosing <strong>ZMC Student Assistant!</strong></p>
    <h4 style="color: #1E90FF;">Best regards,</h4>
    <h4 style="color: #1E90FF;">ZMC Student Assistant Team</h4>
    """
    body2 = f"""
    <p style="color:#1E90FF; font-weight:bold;">Dear Student,</p>
    <p>Welcome to ZMC Student Assistant! We are thrilled to have
    you on board, and we appreciate your decision to create an
    account with us. </p>

    <p>Please use the following verification code to
    complete the registration process:</p>

    <p><span>{code}</span></p>

    <p>If you did not request this code or are not the intended
    recipient, please disregard this message. Your account
    security is important to us, and this code should only be
    shared by the account holder.</p>

    <p>Thank you for choosing ZMC Student Assistant. We look
    forward to providing you with an exceptional experience.</p>

    <h4 style="color: #1E90FF;">Best regards,</h4>

    <h4 style="color: #1E90FF;">ZMC Student Assistant Team</h4>
    """
    body3 = f"""
    <p style="color:#1E90FF; font-weight:bold;">Dear Student,</p>
    <p>We have successfully received your password reset request at ZMC
    Student Assistant.</p>

    <p>Please use the following code to complete the password
    reset process:</p>

    <p><span>{code}</span></p>

    <p>If you did not initiate this password reset or are not the
    intended recipient, please disregard this message. Your
    account security is paramount, and this code should only be
    shared by the account holder.</p>

    <p>Thank you for trusting ZMC Student Assistant. We're here to
    assist you and ensure a seamless experience.</p>

    <h4 style="color: #1E90FF;">Best regards,</h4>

    <h4 style="color: #1E90FF;">ZMC Student Assistant Team</h4>

    """
    if not value:
        return body
    elif value == 1:
        return body2
    elif value == 2:
        return body3
