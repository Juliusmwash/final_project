from flask import Flask, request, jsonify, render_template, session
from bson.raw_bson import RawBSONDocument
from PIL import Image
import pytesseract
import asyncio
#from flask import Quart, render_template_string, session
from flask.sessions import SecureCookieSessionInterface
from openai import OpenAI
import os
import json
import time
import re
import pymongo
from pymongo import MongoClient
import logging
import sys
import tracemalloc
import tiktoken

openai_uri = os.environ.get('OPENAI_ADMIN_DATABASE_URI')
client = MongoClient(openai_uri)
openai_db = client['openaiDB']


"""
collection = openai_db['openai_test']
collection.insert_one({"test":"okay"})
result = collection.find_one({"test":"okay"})
print(f"\n\ndatabase result: {str(result)}\n\n")
"""


# Start tracing
tracemalloc.start()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'julius_testing_zambezi_mall_project'
app.session_interface = SecureCookieSessionInterface()

api_key = os.environ.get('MY_OPENAI_API_KEY')
client = OpenAI(api_key=api_key,)

MATH_ASSISTANT_ID = '';
#mathematical expression using LaTeX syntax





def configure_user_account():
    # Connect to the MongoDB database
    collection = openai_db["user_account"]

    # Define the document
    document = {
        "user": "Admin",
        "email": "admin@gmail.com",
        "school": "testing school",
        "level_of_school": "master",
        "password": "password",
        "tokens": 100000,
        "accumulating_tokens": 0,
        "lock": False,
        "user_styling": {"font_size": 14, "font_family": "sans-serif",
                         "text_color": "#29ADB2", "background_color": "#040D12"}
    }

    # Insert the document into the collection
    result = collection.insert_one(document)

    # Print the inserted document's ID
    print("Inserted document ID:", result.inserted_id)



def delete_false_prompts():
    prompt = """<h3 style=\"margin-top: 20px; color: #F4CE14;\">User</h3><p style=\"color: #7ED7C1;\">false</p>"""
    collection = openai_db["openai_threads"]
    collection.delete_many({"prompt": prompt})


def token_updating_func(current_tokens):
    """
    The final token calculations are carried out here and saved
    to the database and in the session as well.
    This function is being called by the function 'clean_content()'.
    clean_content() can be found at or close to line number 646.
    """
    try:
        accumulating_tokens = 0

        prev_thrd_rqst = session.get("previous_thread_request", 0)
        thrd_cntn_timer = session.get("thread_continuation_timer", 0)

        if prev_thrd_rqst:
            session["previous_thread_request"] = False
            accumulating_tokens = int(session.get("math_variable", 0))
        elif thrd_cntn_timer:
            session["thread_continuation_timer"] = False
            accumulating_tokens = 0

        #Connect to the database
        collection = openai_db["user_account"]
        remaining_tokens = None
        
        result = collection.find_one({"email": "admin@gmail.com"})
        if result:
            total_tokens = int(result["tokens"])
            if not prev_thrd_rqst:
                if not thrd_cntn_timer:
                    accumulating_tokens = int(result["accumulating_tokens"])
            deduct_tokens = accumulating_tokens + int(current_tokens)
            value_to_update = None

            remaining_tokens = total_tokens - deduct_tokens
            if remaining_tokens > 0:
                value_to_update = {"tokens": remaining_tokens,
                                   "accumulating_tokens": deduct_tokens,
                                   "lock": False}
            else:
                value_to_update = {"tokens": remaining_tokens,
                                   "accumulating_tokens": deduct_tokens,
                                   "lock": True}

            session["user_tokens"] = remaining_tokens

            # Update document
            result = collection.update_one({"_id": result["_id"]}, {"$set": value_to_update})
            # Check if the update was successful
            if result.acknowledged and result.modified_count > 0:
                return "update successful"
            else:
                return "update failed"
    except Exception as e:
        print(f"token_udating_func Error = {e}")
        return "Update failed"



def calculate_old_thread_tokens(thread_id):
    # Get the signals from the session
    # thread_continuation_signal = session.get("thread_continuation_timer", 0)
    # thread_previous_request = session.get("previous_thread_request", 0)
    try:
        # Connect to the database
        collection = openai_db["openai_threads"]

        # Variable to store all previous tokens used in the thread
        tokens_used = 0

        result = collection.find({"thread_id": thread_id})
        if result:
            for doc in result:
                tokens_used += int(doc["tokens_consumed"])

            session["previous_thread_request"] = True
            session["math_variable"] = tokens_used
            return "old_thread_request", tokens_used

        session["previous_thread_request"] = True
        session["UNIVERSAL_ERROR"] = True
        print("calculate_old_thread_tokens Triggered Universal Error")
        return "Error"

    except Exception as e:
        print(f"token_calculations_decider Error = {e} Universal Error Triggered")
        session["previous_thread_request"] = True
        session["UNIVERSAL_ERROR"] = True
        return "Error"

    











def get_remaining_user_tokens():
    try:
        # Connect to the database
        collection = openai_db["user_account"]
        result = collection.find_one({"email": "admin@gmail.com"})
        if result:
            tokens_remaining = int(result["tokens"])

            # Save this data for latter retrival
            session["user_tokens"] = tokens_remaining

            return tokens_remaining
        return 0
    except Exception as e:
        print(f"get_remaining_user_tokens Error = {e}")
        return 0



async def get_user_styling_preference(email):
    try:
        # Connect to the database
        collection = openai_db["user_account"]
        #email = "admin@gmail.com"

        result = collection.find_one({"email": email})
        if result:
            styling_obj = result["user_styling"]
            return styling_obj
        return None
    except Exception as e:
        print(f"get_user_styling_preference Error = {e}")
        return None


@app.route('/update_user_styling', methods=["POST"])
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
                email = "admin@gmail.com"
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



@app.route('/', methods=["GET"])
async def index():
    session.clear()
    #configure_user_account()
    #delete_false_prompts()
    # Save user tokens to the session. Used by the requests which do not make api calls
    # Add session data checker variables
    decide = 0
    obj = dict()

    session["user_tokens"] = get_remaining_user_tokens()

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

    user_styling = await get_user_styling_preference("admin@gmail.com")
    threads = create_thread_array()

    if not threads:
        print("not threads")
        session["assistant_id"] = ""
        session["thread_id"] = ""

    # Get user remaining tokens
    tokens_count = int(session["user_tokens"])
    tokens_count = f"{tokens_count:,}"

    if not decide:
        obj = await thread_decider_func("most_recent_thread")
        print(f"\n\nobj = {str(obj)}")
        threads = create_thread_array()

    return render_template("index.html", threads=threads,
                           tokens_count=tokens_count, decide=decide, obj=obj,
                           user_styling=user_styling)





""" Assistant functions start """

@app.route('/zmc_assistant_data', methods=['POST'])
async def zmc_assistant_data():

    print("called")
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
            return jsonify(obj)

        if info_request == "info_request":
            # Call info_request_func()
            obj = await info_request_func()
            if obj["success"]:
                return jsonify({"success": True,
                                "response_text": obj["response_text"],
                                "tokens_count": obj["tokens_count"]})
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
                                "tokens_count": obj["tokens_count"]})

        # Check if it is a thread change call
        if thread_num != "0":
            print("thread num is not 0, so old thread invoked")
            # Call old_thread_request_func()
            obj = await old_thread_request_func(thread_num)
            if obj["success"]:
                return jsonify({"success": True,
                                "response_text": obj["response_text"],
                                "tokens_count": obj["tokens_count"]})


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

        print("Direct here, no match upstairs")


        result = await flask_main(prompt, thread_status)
        # Get updated token count from the session. Already there is a function that has updated it.

        tokens = session.get("user_tokens", 0)
        if tokens:
            tokens = f"{int(tokens):,}"

        return jsonify({'success': True, 'response_text': result, "tokens_count": tokens})

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





# replace backslashes with &bksl;
async def replace_backslash_latex(latex_expression):
    return latex_expression.replace("\\", "&bksl;")

# Reverse to backslashes
async def reverse_replace_backslash_latex(modified_latex):
    return modified_latex.replace("&bksl;", "\\")




""" flask main function start """

#@app.route('/openai', methods=["GET", "POST"])
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
    MATH_ASSISTANT_ID = session["assistant_id"]
    thread_id = session["thread_id"]
    check = 1
    thread, run = await create_thread_and_run(MATH_ASSISTANT_ID, prompt, thread_id)
    run = await wait_on_run(run, thread_id, check)
    return_value = await pretty_print(await get_response(thread_id, check))
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
            "assistant_id": MATH_ASSISTANT_ID,
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
    MATH_ASSISTANT_ID = assistant.id
    session["assistant_id"] = MATH_ASSISTANT_ID
    thread, run = await create_thread_and_run(MATH_ASSISTANT_ID, prompt)

    session["thread_id"] = thread.id
    run = await wait_on_run(run, thread, check)
    return_value = await pretty_print(await get_response(thread, check))
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
            "assistant_id": MATH_ASSISTANT_ID,
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









def openai_threads_messages_save(openai_data):
    try:
        collection = openai_db["openai_threads"]

        # Find the most recent document
        result = collection.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])

        # Check if the thread_id already exists
        result2 = collection.find_one({"thread_id": openai_data['thread_id']})

        if result:
            # Increment thread_num only if the thread_id is new
            if not result2:
                openai_data['thread_num'] = result['thread_num'] + 1
                # Keep thread sequence record
                save_thread_number(
                        result['thread_num'] + 1,
                        openai_data["thread_id"],
                        openai_data["assistant_id"])
            else:
                openai_data['thread_num'] = result2['thread_num']
        else:
            openai_data['thread_num'] = 1
            # Keep thread sequence record
            save_thread_number(1, openai_data["thread_id"],
                               openai_data["assistant_id"])

        # Insert the new document
        result = collection.insert_one(openai_data)

        if result.acknowledged and result.inserted_id:
            return "success"
        else:
            return "fail"

    except Exception as e:
        logging.error(f"openai_threads_create Error: {e}")
        return "fail"





"""
def openai_threads_create(openai_data):
    try:
        collection = openai_db["openai_threads"]
        result = collection.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])

        result2 = collection.find_one(
                {"thread_id": openai_data['thread_id']},
                sort=[("timestamp", pymongo.DESCENDING)])
        if result:
            if not result2:
                openai_data['thread_num'] = result['thread_num'] + 1
        else:
            openai_data['thread_num'] = 1

        result = collection.insert_one(openai_data)
        if result.acknowledged and result.inserted_id:
            return "success"
        return "fail"
    except Exception as e:
        print(f"openai_threads_create Error: {e}")
        return("fail")
"""




def openai_threads_database():
    pass


def text_generator(image_file):
    # Open an image file
    image = Image.open(image_file)

    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(image)
    return text;



def show_json(obj):
    print(json.loads(obj.model_dump_json()))



#instructions="Assist students with math queries. If the question is unrelated to math, politely mention that assistance is only available for math subjects. When addressing math queries, provide a step-by-step solution using MathJax library-compatible responses for equation rendering. Ensure clarity in your explanations to help students understand the solution.",
#If the prompt is exactly "new thread" reply with '<p>Thread created, how can I assist you?</p>'




# Define function to create an assistant
async def assistant_creator():
    print("assistant here")
    assistant = client.beta.assistants.create(
        name="ZMC STUDENT ASSISTANT",
        instructions="""Ouput content in html format and use p tags only. Avoid using newline characters; use `<p>` tags instead. Even for a single line, enclose it within `<p>` tags.Assist on all queries.If equations are involved use latex syntax.If 'new thread' is issued as a prompt, reply with '<p>Thread created, how can I assist you?</p>'.""",
        model="gpt-3.5-turbo",
    )
    return assistant


async def wait_on_run(run, thread, check=0):
    #print("\n\nwait here")
    value = ''
    if check:
        #print("wait check is 1")
        value = thread
    else:
        #print("wait check is 0")
        value = thread.id

    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=value,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


async def submit_message(assistant_id, thread, user_message, check=0):
    #print("submit here")
    #print(str(thread))
    print(str(assistant_id))
    if check:
        client.beta.threads.messages.create(
                thread_id=thread, role="user", content=user_message
                )
        return client.beta.threads.runs.create(
            thread_id=thread,
            assistant_id=assistant_id,
        )


    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )




async def get_response(thread, check=0):
    #print("response here")
    value = ''
    if check:
        value = thread
    else:
        value = thread.id
    # Retrieve only the newest message in the thread
    newest_message = client.beta.threads.messages.list(
        thread_id=value,
        order="desc",  # Order the messages in descending order (newest to oldest)
        limit=1  # Limit the result to only one message
    )
    #print(f"HERE = {type(newest_message)}")
    return newest_message

    """
    #return client.beta.threads.messages.list(thread_id=thread, order="asc")
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    """





async def create_thread_and_run(MATH_ASSISTANT_ID, user_input, thread_id=''):
    #print("\n\ncreate here")
    if thread_id:
        #print("session -> create")
        run = await submit_message(MATH_ASSISTANT_ID, thread_id, user_input, 1)
        #print(f"Create run id = {run.id}\n\n")
        return "", run

    thread = client.beta.threads.create()
    #print(f"thread: {thread}\n")
    run = await submit_message(MATH_ASSISTANT_ID, thread, user_input)
    #print(f"Create run id = {run.id}\n\n")
    return thread, run


# Pretty printing helper
async def pretty_print(messages):
    #print("Pretty print called")
    #print("# Messages\n")
    #if check:
    # Check if there is any message
    if messages and messages.data:
        # Access the newest message
        latest_message = messages.data[0]

        # Print or use the newest message as needed
        latest = re.sub(r'\\\\', r'\\', str(latest_message.content))
        #print(f"\n\n\nlatest =\n\n{latest}")

        return latest
    return False




async def num_tokens_from_messages(message, model="gpt-3.5-turbo-1106"):
    """Return the number of tokens used by a list of messages."""
    num_tokens = 0

    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    try:
        num_tokens += tokens_per_message
        num_tokens += len(encoding.encode(message))
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        #print(f"Generated tokens = {num_tokens}")
        return num_tokens
    except Exception as e:
        print(f"num_tokens&from_messages Error: {e}")
        return 0




async def clean_content(input_content):
    """
    Extracts the required value from the returned message by the api.
    Once the value is obtained all newline characters are removed.
    This is because html don't depend on newline characters to render new lines.
    Finally, the tokens consumed by the current call is calculated here
    before sending the result to the other function for further processing.
    """
    start_index = input_content.find('value="')
    if start_index == -1:
        start_index = input_content.find("value='")
    
    if start_index != -1:
        #print("ALL IS WELL")
        start_index += len('value="')
        end_index = input_content.rfind('"),', 0, len(input_content) - 3)
        if end_index == -1:
            end_index = input_content.rfind("'),", 0, len(input_content) - 3)

        if end_index != -1:
            #print("ALL IS WELL")
            first_content = input_content[start_index:end_index]

            # Count number of tokens used
            token_count = await num_tokens_from_messages(first_content)
            token_count_session = session.get("instruction_prompt_tokens", 0)
            if token_count_session:
                token_count_session = int(token_count_session)

            total_tokens_count = token_count + token_count_session

            # Save the total tokens used in the session
            session["currently_used_tokens"] = total_tokens_count

            print(f"\n\nGenerated count = {token_count}\n\n")

            #Update user tokens
            token_updating_func(total_tokens_count)

            cleaned_content = first_content.replace('\n', '').replace('\\n', '')
            return cleaned_content

    # Return the original content if substrings are not found
    print("NOT GOOD OOOH!")
    return input_content



#Function to save thread numbers and their associated thread id and assistant id.
def save_thread_number(thread_num, thread_id, assistant_id):
    try:
        # Connect to the database
        collection = openai_db['thread_sequence']

        obj = {
                "thread_num": thread_num,
                "thread_id": thread_id,
                "assistant_id": assistant_id
            }

        result = collection.insert_one(obj);

        if result.acknowledged and result.inserted_id:
            return True
        return False
    except Exception as e:
        print(f"save_thread_number Error: {e}")
        return False

# Function to create list of thread numbers
def create_thread_array():
    try:
        # create a list variable
        thread_list = []

        # Connect to the database
        collection = openai_db['thread_sequence']

        """list_data = [
                {
                    "thread_num": 8,
                    "thread_id": "thread_sfboKpiCS9f1R0gaiv6zzUhO",
                    "assistant_id": "asst_XfpCN5vw7Hf1nhUiCU198LdF"
                },
                {
                    "thread_num": 9,
                    "thread_id": "thread_Sqn9X555mBHdZLk15eOI26Me",
                    "assistant_id": "asst_uuHIdlxYOuyv4cg1z6KbyPtX"
                }
            ]

        collection.insert_many(list_data)"""

        result = collection.find()
        if result is not None:
            for obj in result:
                thread_list.append(obj["thread_num"])
            return thread_list
        return 0
    except Exception as e:
        print(f"create_thread_array() Error: {e}")
        return 0

# Function for shifting threads
def shift_threads(thread_num):
    print("shift threads called")
    thread_num = int(thread_num)
    try:
        # Connect to the database
        collection = openai_db["thread_sequence"]

        result = collection.find_one({"thread_num": thread_num})

        if result is not None:
            # Update the  session data
            session["thread_id"] = result["thread_id"]
            session["assistant_id"] = result["assistant_id"]

            # Start thread data retrieval process
            result = get_thread_data(result["thread_id"])
            if result:
                return result
        return False
    except Exception as e:
        print(f"shift_threads(thread_num) Error = {e}")
        return False



# Function for getting thread data
def get_thread_data(thread_id):
    try:
        # create a variable to hold thread data
        thread_data = ""

        # Connect to the database
        collection = openai_db["openai_threads"]

        result = collection.find({"thread_id": thread_id})

        if result:
            for obj in result:
                thread_data += obj["prompt"] + obj["message"]
            return thread_data
        return False
    except Exception as e:
        print(f"get_thread_data() Error = {e}")
        return False






"""
async def clean_file(input_file):
    content = ""
    with open(input_file, 'r') as file:
        content = file.read()
        print(str(content))

    start_index = content.find('value="')
    print(f"\n\nstart index = {start_index}\n\n")
    if start_index != -1:
        start_index += len('value="')
        end_index = content.rfind('"),', 0, len(content) -3)  # Exclude the last parenthesis
        print(f"\n\nend index = {end_index}\n\n")
        if end_index != -1:
            #cleaned_content = content[:start_index] + content[end_index + 2:]  # Exclude the second last parenthesis
            cleaned_content = content[start_index:end_index]
            return cleaned_content
"""




if __name__ == '__main__':
    app.run(debug=True, port=5020)
    """import uvicorn  # An ASGI server implementation

    # Add the ASGIProxyMiddleware to convert the Flask app to ASGI
    from asgiref.wsgi import WsgiToAsgi
    app = WsgiToAsgi(app)

    # Run the app using uvicorn as the server
    uvicorn.run(app, host="localhost", port=5020)
    #app.run(debug=True, port=5020)"""

