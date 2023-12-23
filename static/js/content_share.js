
/*
This scripts involves only the logic for student content sharing.
*/


/* Hide the share element and reset it back to default settings */
const shareCancelButton = document.querySelector('.share-cancel-btn');
shareCancelButton.addEventListener('click', () => {
  //const shareContainer = document.querySelector('.share-container');
  const shareWrapperSend = document.querySelector('.share-wrapper-send');
  const receiveChoiceBox = document.querySelector('.receive-choice-box');
  const useShareIdBox = document.querySelector('.use-share-id-box');
  const shareLoadingBox = document.querySelector('.share-loading-box');

  //shareContainer.style.display = 'none';
  shareWrapperSend.style.display = 'none';
  receiveChoiceBox.style.display = 'none';
  useShareIdBox.style.display = 'none';
  shareLoadingBox.style.display = 'none';
  shareHideBox();
});

/* Share content with other students */
const shareContentButton = document.querySelector('.share-content-button');
shareContentButton.addEventListener('click', () => {
  const landingButtons = document.querySelector('.landing-buttons');
  landingButtons.style.display = 'none';
  const shareWrapperSend = document.querySelector('.share-wrapper-send');
  shareWrapperSend.style.display = 'block';
});
const shareSendButton = document.querySelector('.share-button');
shareSendButton.addEventListener('click', async () => {
  const contentTitleInput = document.getElementById('content-title');
  const descriptionTextarea = document.getElementById('description');
  const taggedEmails = document.getElementById('taggedEmails');

  if (contentTitleInput.value.length === 0) {
    // Handle the case where content title is empty
    await showResponseToUser(false, "Please give your content a title");
  } else if (descriptionTextarea.value.length === 0) {
    // Handle the case where description is empty
    await showResponseToUser(false, "Please describe your content");
  } else {
    // All fields are filled, proceed with content sharing
    const threadId = document.getElementById('thread-id-holder').textContent;
    if (threadId) {
      await enableContentSharing(threadId);
    } else {
      const m = "Sorry, thread Id not found. Try reloading the thread again";
      await showResponseToUser(false, m);
    }
  }
});




/* Get shared content from the server */
const getContentButton = document.querySelector('.get-content-button');
getContentButton.addEventListener('click', () => {
  const landingButtons = document.querySelector('.landing-buttons');
  landingButtons.style.display = 'none';
  const receiveChoiceBox = document.querySelector('.receive-choice-box');
  receiveChoiceBox.style.display = 'flex';
});
const useShareIdButton = document.querySelector('.have-share-id');
useShareIdButton.addEventListener('click', () => {
  const receiveChoiceBox = document.querySelector('.receive-choice-box');
  receiveChoiceBox.style.display = 'none';
  const useShareIdBox = document.querySelector('.use-share-id-box');
  useShareIdBox.style.display = 'block';
});
const getContentBtn = document.querySelector('.get-content');
getContentBtn.addEventListener('click', async () => {
  const shareLoadingBox = document.querySelector('.share-loading-box');
  shareLoadingBox.style.display = 'flex';

  const sharedIdInput = document.querySelector('.share-id-input');
  const sharedId = sharedIdInput.value;
  await getSharedContent(sharedId);

  setTimeout(() => {
    document.querySelector('.share-cancel-btn').click();
  }, 8000);
});








/* Reveal share content element box */
const revealShareBoxButton = document.querySelector('.reveal-share-box-button');

revealShareBoxButton.addEventListener('click', () => {
  document.querySelector('.font-size-box').style.display = 'none';
  shareShowBox();
  //document.querySelector('.font-size-box').style.display = 'none';
});
function shareShowBox() {
  const shareContainer = document.querySelector('.share-container');
  shareContainer.classList.add('visible');
  shareContainer.style.backgroundColor = getRandomColor();
  const landingButtons = document.querySelector('.landing-buttons');
  landingButtons.style.display = 'flex';
}
function shareHideBox() {
  const shareContainer = document.querySelector('.share-container');
  shareContainer.classList.remove('visible');
}



// Make an HTTP Post request to the Flask API endpoint to enable content sharing
async function enableContentSharing(threadId) {
  try {
    alert("function invoked");
    const shareLoadingBox = document.querySelector('.share-loading-box1');
    shareLoadingBox.style.display = "flex";
    // Initialise form for sending data to the server
    const formData = new FormData();

    // Get elements that holds the content sharing data
    const contentTitleInput = document.getElementById('content-title');
    const descriptionTextarea = document.getElementById('description');
    const taggedEmails = document.getElementById('taggedEmails');

    formData.append('content_title', contentTitleInput.value);
    formData.append('description', descriptionTextarea.value);
    formData.append('tagged_emails', taggedEmails.value);
    formData.append('thread_id', threadId);

    const response = await fetch('/enable_content_sharing', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
      //Show error message to the user
      await showResponseToUser(false, "Network Error");
      shareLoadingBox.style.display = "none";
    }

    const data = await response.json();
    console.log(data);

    if (data.success) {
      console.log('Content sharing set successfully');
      //alert("sharing set successfully");
      //Show success message to the user
      await showResponseToUser(true, data.message);
      shareLoadingBox.style.display = "none";
    } else {
      console.error('Server response indicates failure:', data.message);
      //Show error message to the user
      await showResponseToUser(false, data.message);
      shareLoadingBox.style.display = "none";
    }
  } catch(error) {
    alert(`Error: ${error}`);
    console.error('Error fetching data:', error);
  }
}

async function showResponseToUser(success = true, message) {
  const responseInfo = document.querySelector('.response-info');

  if (success) {
    responseInfo.innerHTML = message;
    responseInfo.style.backgroundColor = "#008000";
    responseInfo.style.color = "#00FF00";
    responseInfo.style.display = 'flex';
    setTimeout(() => {
      responseInfo.style.display = 'none';
    }, 10000);
  } else {
    responseInfo.innerHTML = message;
    responseInfo.style.backgroundColor = "#8B0000";
    responseInfo.style.color = "#ff0000";
    responseInfo.style.display = 'flex';
    setTimeout(() => {
      responseInfo.style.display = 'none';
    }, 10000);
  }
}










/*
@app.route('/get_shared_content', methods=["POST"])                   async def get_shared_content():
    """                                                                   Receives the requests related to retrieval of the shared content.     Shared content will be extracted and sent to the student.
    """
                                                                          try:
        shared_id = request.form.get('shared_id', None)

        # Connect to the database                                             collection = openai_db["shared_content"]                                                                                                    # Retrieve shared content
        if shared_id:
            result = collection.find_one({"shared_id": shared_id})
            if result:
                return jsonify(
                        {"success": True, "shared_content": result})

            message = "Sorry, the shared content with that id was not
found."
            return jsonify({"success": False, "message": message})

        # Count the number of documents in the collection                     document_count = collection.count_documents({})

        # Set the desired number of random documents to retrieve
        desired_count = min(document_count, 10)

        # Use $sample to randomly select documents
        random_documents = collection.aggregate([
            { "$sample": { "size": desired_count } }
            ])

        # Retrieve titles from the extracted documents
        list_objs = []
        for doc in random_documents:
            obj = {"shared_id": doc["shared_id"], "title": doc["title"
]}
            list_objs.append(obj)
        return jsonify({"success": True, "list_objs": list_objs})
                                                                          except Exception as e:
        print(f"get_shared_content Error = {e}")                              return jsonify({"success": False, "message": e})
*/





// Make an HTTP Post request to the Flask API endpoint to fetch shared content
async function getSharedContent(shareId = "") {
  try {
    const shareLoadingBox = document.querySelector('.share-loading-box');
    shareLoadingBox.style.display = "flex";

    // Initialise form for sending data to the server
    const formData = new FormData();
    formData.append('shared_id', shareId);

    const response = await fetch('/get_shared_content', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
      alert("Error occured");
      shareLoadingBox.style.display = "flex";
    }

    const data = await response.json();
    console.log(data);

    if (data.success) {
      console.log('Content sharing set successfully');
      shareLoadingBox.style.display = "none";

      const generatorBox = document.querySelector('.generator-box');
      // Replace all occurrences of "&bksl;" with a backslash
      const inputString = data.shared_content;
      const outputString = inputString.replace(/&bksl;/g, "\\");
      generatorBox.innerHTML = outputString;

      // Trigger MathJax rendering
      MathJax.typeset();

      // Set fonts
      resetFontStyles();

      //alert(`Shared content = ${data.shared_content}`);
      /*{"success": True, "shared_content": result,                            "message": message, "used_shared_id": True})*/
    } else {
      console.error('Server response indicates failure:', data.message);
      shareLoadingBox.style.display = "none";
    }
  } catch(error) {
    alert(`Error: ${error}`);
    console.error('Error fetching data:', error);
  }
}


// Function to randomly select a color code
function getRandomColor() {
  // Array of color codes
  const colorArray = ["#253529", "#3b3c36", "#414a4c", "#232B2B", "#123524", "#1A2421", "#674846", "#704241", "#000036", "#000039", "#253529", "#32174d", "#100C08", "#080808", "#1c2841", "#480607", "#010127", "#151922", "#004242"];

  const randomIndex = Math.floor(Math.random() * colorArray.length);
  return colorArray[randomIndex];
}


function resetFontStyles() {
// Reset font styles
  const elementsToStyle = ['p', 'ul', 'li', 'span', '.generator-box'];
  elementsToStyle.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
      if (fontFamily) {
        element.style.fontFamily = fontFamily;
      }
      if (selector === 'p' || selector === 'generator-box') {
        if (choiceColor) {
          element.style.color = choiceColor;
        }
      }
    });
  });
}
