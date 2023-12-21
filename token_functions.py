from flask import session
from extensions import openai_db


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

