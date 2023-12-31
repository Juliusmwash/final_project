def openai_threads_messages_save(openai_data):
    try:
        collection = openai_db["openai_threads"]

        # Find the most recent document
        email = current_user.email
        result = collection.find_one(
                {"email": email}, sort=[("timestamp", pymongo.DESCENDING)])

        # Check if the thread_id already exists
        query = {"$and": [
            {"email": email},
            {"thread_id": openai_data['thread_id']}]}
        result2 = collection.find_one(query)

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



#Function to save thread numbers and their associated thread id and assistant id.
def save_thread_number(thread_num, thread_id, assistant_id):
    try:
        email = current_user.email
        # Connect to the database
        collection = openai_db['thread_sequence']

        obj = {
                "email": email,
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
