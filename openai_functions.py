from extensions import openai_client as client
import time
import re

# Define function to create an assistant
async def assistant_creator():
    print("assistant here")
    assistant = client.beta.assistants.create(
        name="ZMC STUDENT ASSISTANT",
        instructions="""Ouput content in html format and use p tags only. Avoid using newline characters; use `<p>` tags instead. Even for a single line, enclose it within `<p>` tags.Assist on all queries.If equations are involved use LaTeX syntax.If 'new thread' is issued as a prompt, reply with '<p>Thread created, how can I assist you?</p>'.""",
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
    return newest_message


async def create_thread_and_run(MATH_ASSISTANT_ID, user_input, thread_id=''):
    #print("\n\ncreate here")
    if thread_id:
        run = await submit_message(MATH_ASSISTANT_ID, thread_id, user_input, 1)
        return "", run

    thread = client.beta.threads.create()
    run = await submit_message(MATH_ASSISTANT_ID, thread, user_input)
    return thread, run


# Pretty printing helper
async def extract_openai_message(messages):
    # Check if there is any message
    if messages and messages.data:
        # Access the newest message
        latest_message = messages.data[0]
        latest = re.sub(r'\\\\', r'\\', str(latest_message.content))

        return latest
    return False


def show_json(obj):
    print(json.loads(obj.model_dump_json()))
