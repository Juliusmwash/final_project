import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Function for sending shared ID to the user through email
async def send_shared_id_email(rec_email, shared_id):
    print("\n\nSENDING EMAIL\n\n")
    # Get the email password from the environment variable
    password = os.getenv('EMAIL_PASSWORD')
    generated_body = build_email_body(shared_id)

    # Sender email
    sender_email = "zambezimarketcenter@gmail.com"

    # Create an instance of MIMEMultipart
    message = MIMEMultipart()

    # Set the subject
    message['Subject'] = 'Shared Content Id'

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
                background-color: #f0f0f0;
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
    """.format(generated_body) # Insert the generated body

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
        return True
    except Exception as e:
        print(f"send_shared_id_email Error = {e}")
        return False


# Function to determine the mail body based on the value passed to it
def build_email_body(shared_id):
    body = f"""<p><strong>Dear Student,</strong></p>
    <p>A new shared content has been created, and you have been tagged.
    <p>The shared ID provided below can be used to retrieve the content
    on the <strong>ZMC Student Assistant</strong> website.
    </p><p>Our commitment is to make learning enjoyable. Utilize the
    shared content to your advantage.</p>

    <p><span>{shared_id}</span></p>
    <p>Thank you for choosing <strong>ZMC Student Assistant!</strong></p>
    <h4>Best regards,<br>The ZMC Student Assistant Team</h4>
    """
    return body
