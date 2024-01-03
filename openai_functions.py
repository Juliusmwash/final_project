from extensions import openai_client as client
import time
import re


"""
ZMC STUDENT ASSISTANT - OPENAI FUNCTIONS MODULE

Module: openai_functions.py

Developer: Julius Mwangi
Contact:
    - Email: juliusmwasstech@gmail.com

---

Disclaimer:
This project is a solo endeavor, with Julius Mwangi leading all
development efforts. For inquiries, concerns, or collaboration requests
related to OpenAI-powered functions, please direct them to the provided
contact email.

---

About

Welcome to the magical heart of the ZMC Student Assistant - the
`openai_functions.py` module. This module orchestrates the wizardry
behind handling user prompts and generating content through the OpenAI
assistant, intricately crafted by Julius Mwangi.

Developer Information

- Name: Julius Mwangi
- Contact:
  - Email: [juliusmwasstech@gmail.com]
            (mailto:juliusmwasstech@gmail.com)

Acknowledgments

Special thanks to the incredible ALX TEAM for their unwavering support
and guidance. Their influence has been instrumental in shaping my journey
as a software engineer, particularly in developing the magical
OpenAI-powered functions.

---

Note to Developers:
Feel free to explore, contribute, or connect. Your insights and feedback,
especially regarding the enchanting world of OpenAI functionality, are
highly valued and appreciated!

Happy coding!
"""


# Define function to create an assistant
async def assistant_creator():
    """
    Creates and returns an instance of the OpenAI Assistant.

    Returns:
    - OpenAI Assistant: Instance of the created assistant.
    """
    rules = ("Ouput content in html format and use p tags only."
             + "Avoid using newline characters; use <p> tags instead."
             + "Even for a single line, enclose it within <p> tags."
             + "Assist on all queries.If equations are involved use "
             + "LaTeX syntax.If 'new thread' is issued as a prompt, "
             + "reply with '<p>Thread created, how can I assist you?</p>'."
             )

    print("assistant here")
    assistant = client.beta.assistants.create(
        name="ZMC STUDENT ASSISTANT",
        instructions=rules,
        model="gpt-3.5-turbo",
    )
    return assistant


async def wait_on_run(run, thread, check=0):
    """
    Waits for the completion of the assistant's run and returns the
    final result.

    Args:
    - run: Assistant's run instance.
    - thread: Thread or thread ID associated with the run.
    - check: Flag to determine whether the thread or its ID is passed.

    Returns:
    - OpenAI Run: The final result of the assistant's run.
    """
    # print("\n\nwait here")
    value = ''
    if check:
        # print("wait check is 1")
        value = thread
    else:
        # print("wait check is 0")
        value = thread.id

    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=value,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


async def submit_message(assistant_id, thread, user_message, check=0):
    """
    Submits a user message to the assistant's thread and starts a new run.

    Args:
    - assistant_id: ID of the assistant.
    - thread: Thread or thread ID where the message will be submitted.
    - user_message: Content of the user message.
    - check: Flag to determine whether the thread or its ID is passed.

    Returns:
    - OpenAI Run: The new run started by the assistant.
    """
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
    """
    Retrieves the newest message in the given thread.

    Args:
    - thread: Thread or thread ID where the message will be retrieved.
    - check: Flag to determine whether the thread or its ID is passed.

    Returns:
    - OpenAI Message: The newest message in the thread.
    """
    value = ''
    if check:
        value = thread
    else:
        value = thread.id
    # Retrieve only the newest message in the thread
    newest_message = client.beta.threads.messages.list(
        thread_id=value,
        order="desc",  # newest to oldest
        limit=1  # Limit the result to only one message
    )
    return newest_message


async def create_thread_and_run(MATH_ASSISTANT_ID, user_input, thread_id=''):
    """
    Creates a new thread and runs the assistant on the given user input.

    Args:
    - MATH_ASSISTANT_ID: ID of the assistant.
    - user_input: User's input for the assistant.
    - thread_id: Optional thread ID. If provided, the message is submitted to
      an existing thread.

    Returns:
    - thread: Newly created thread if no thread ID is provided, else None.
    - run: Run object after submitting the user input to the assistant.
    """
    # print("\n\ncreate here")
    if thread_id:
        run = await submit_message(MATH_ASSISTANT_ID, thread_id, user_input, 1)
        return "", run

    thread = client.beta.threads.create()
    run = await submit_message(MATH_ASSISTANT_ID, thread, user_input)
    return thread, run


async def extract_openai_message(messages):
    """
    Extracts the content of the newest message from OpenAI's response.

    Args:
    - messages: OpenAI's response messages.

    Returns:
    - Content of the newest message or False if no messages are present.
    """
    # Check if there is any message
    if messages and messages.data:
        # Access the newest message
        latest_message = messages.data[0]
        latest = re.sub(r'\\\\', r'\\', str(latest_message.content))

        return latest
    return False


def show_json(obj):
    """
    Pretty prints the JSON representation of an object.

    Args:
    - obj: Object to display the JSON representation.

    """
    print(json.loads(obj.model_dump_json()))
