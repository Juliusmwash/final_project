let fileInput = document.getElementById("file");
let image = document.getElementById("image");
let downloadButton = document.getElementById("download");
let aspectRatio = document.querySelectorAll(".aspect-ratio-button");
const previewButton = document.getElementById("preview");
const previewImage = document.getElementById("preview-image");
const options = document.querySelectorAll(".options");
const imageContainer = document.querySelector('.container');
const imgCont = document.querySelector('.image-container');
const choosePhoto = document.getElementById('choose-a-photo');
const sendPromptBtn = document.getElementById('text-prompt-btn');
const textArea = document.getElementById('text-area');
const changeFontBtn = document.getElementById('change-font-btn');
const fontDrodownBox = document.querySelector('.font-dropdown-box')
const okay = document.querySelector('.okay');
const decrementButton = document.querySelector('.decrement');
const incrementButton = document.querySelector('.increment');

let cropper;
let fileName;
let threadChosen;
let counterCheck = 14;
let interval;
let newThreadController = true;

/*
// Moved to the first script
let choiceBackground;
let fontSize = 14;
let fontFamily = "Roboto";
let choiceColor;
*/

//<div class="exit-font-dropdown">Exit</div>

/* USER PREFERED STYLING */

const UserStylingBtn = document.querySelector(".user-styling-button");
UserStylingBtn.addEventListener('click', async () => {
  // Call the function to send user styling to the server
  document.querySelector('.font-size-box').style.display = 'none';
  await sendUserStylingFunc();
});

async function sendUserStylingFunc() {
  // Assuming 'fontSize', 'choiceColor', and 'choiceBackground' are defined elsewhere in your code
  let obj = {};
  obj["font_family"] = fontFamily;
  obj["font_size"] = fontSize;

  if (choiceColor) {
    obj["text_color"] = choiceColor;
  } else {
    obj["text_color"] = "#29ADB2";
  }

  if (choiceBackground) {
    obj["background_color"] = choiceBackground;
  } else {
    obj["background_color"] = "#040D12";
  }
  const requestData = {"user_styling": obj}

  const url = '/update_user_styling';

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestData),
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(responseData => {
    // Handle the response data as needed
    if (responseData.success) {
      alert("User styling saved successfully");
    } else {
      alert("User styling saved failed");
    }
    console.log('Response:', responseData);
  })
  .catch(error => {
    // Handle errors during the fetch operation
    console.error('Error during fetch operation:', error);
  });
}

/* USER PREFERED STYLING END */





/* DECIDE ELEMENT SCRIPT */
document.addEventListener('DOMContentLoaded', function () {
  function decideLoadingFunc(action = "activate") {
    const decideSection = document.querySelector('.decide-section');
    const loadingBox = decideSection.querySelector('.loading-box3');
    const chooseThreadLabel = document.querySelector('.chose-thread-label');
    const newThread = document.querySelector('.new-thread');
    const mostRecentThread = document.querySelector('.most-recent-thread');

    if (action === "activate") {
      newThread.style.pointerEvents = 'none';
      mostRecentThread.style.pointerEvents = 'none';
      newThread.style.cursor = 'not-allowed';
      mostRecentThread.style.pointerEvents  = 'not-allowed';

      chooseThreadLabel.style.display = 'none';
      loadingBox.style.display = "flex";
    } else {
      loadingBox.style.display = "none";
      newThread.style.pointerEvents = 'unset';
      mostRecentThread.style.pointerEvents = 'unset';
      newThread.style.cursor = 'pointer';
      mostRecentThread.style.cursor = 'pointer';
    }
  }

  const element1 = document.querySelector('.new-thread');
  const element2 = document.querySelector('.most-recent-thread');

  element1.addEventListener('click', function () {
    sendData({ thread_choice: "new_thread", prompt: 'new thread'});
  });

  element2.addEventListener('click', function () {
    sendData({ thread_choice: "most_recent_thread", prompt: "continuation"});
  });


  function activateGeneratorSection() {
    document.querySelector('.generator-section').style.display = 'block';
    document.querySelector('.decide-section').style.display = 'none';
    document.querySelector('.token-label').style.display = 'flex';
    document.querySelector('.tokens-counter').style.display = 'flex';
    document.querySelector('.signin-status').style.display = 'flex';
    document.querySelector('header').style.boxShadow = 'none';
  }



  function sendData(data) {
    // Call the loading function
    decideLoadingFunc();
    const url = '/zmc_assistant_data';

    // Fix: Correct the typo in FormData instantiation
    const formData = new FormData();
    formData.append('thread_choice', data.thread_choice);
    formData.append('prompt', data.prompt);

    fetch(url, {
      method: 'POST',
      body: formData,
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(responseData => {
        if (responseData.success) {
          //alert(`${responseData.response_text}`);

          // Save thread_id
          const threadIdHolder = document.getElementById('thread-id-holder');
          // Save thread_id
          if (data.hasOwnProperty('thread_id')) {
            threadIdHolder.textContent = data.thread_id
          }

          const generatorBox = document.querySelector('.generator-box');
          // Replace all occurrences of "&bksl;" with a backslash

          const inputString = responseData.response_text;
          const outputString = inputString.replace(/&bksl;/g, "\\");
          generatorBox.innerHTML = outputString;

          // Create elements to represent available threads in the server
          generateThreadButtons(responseData.threads)

          // Activate the generator section and other related elements while
          //  deactivating decide section elements
          activateGeneratorSection();
        }
      })
      .catch(error => {
        // Handle errors during the fetch operation
        alert(error);
        console.error('Error during fetch operation:', error);
      })
      .finally(() => {
        // Ensure this runs even in case of success or error
        decideLoadingFunc("deactivate");
      });
  }

});

/* END */










const changeBackgroundBtn = document.getElementById('change-background-btn');
const backgroundDropdownBox = document.querySelector('.background-dropdown-box');
const backgroundDropdownAll = document.querySelectorAll('.background-dropdown');

changeBackgroundBtn.addEventListener('click', () => {
  document.querySelector('.background-dropdown-box').style.display = 'flex';
  showBox3();
  document.querySelector('.font-size-box').style.display = 'none';
});

backgroundDropdownAll.forEach((element) => {
  element.addEventListener('click', () => {
    choiceBackground = element.getAttribute('data-background-code')
    document.querySelector('.font-size-box').style.display = 'none';
    hideBox3();
    document.querySelector('.generator-box').style.backgroundColor = choiceBackground;
    document.querySelectorAll('p').forEach((element) => {
      element.style.color = choiceColor;
    });
  });
});


function showBox3() {
  const animatedBox = document.querySelector('.background-dropdown-box');
  animatedBox.classList.add('visible');
}
function hideBox3() {
  const animatedBox = document.querySelector('.background-dropdown-box');
  animatedBox.classList.remove('visible');
}




const changeColorBtn = document.getElementById('change-color-btn');
changeColorBtn.addEventListener('click', () => {
  document.querySelector('.color-dropdown-box').style.display = 'flex';
  showBox2();
  document.querySelector('.font-size-box').style.display = 'none';
});


function showBox2() {
  const animatedBox = document.querySelector('.color-dropdown-box');
  animatedBox.classList.add('visible');
}
function hideBox2() {
  const animatedBox = document.querySelector('.color-dropdown-box');
  animatedBox.classList.remove('visible');
}

const colorDropdownAll = document.querySelectorAll('.color-dropdown');
colorDropdownAll.forEach((element) => {
  element.addEventListener('click', () => {
    choiceColor = element.getAttribute('data-color-code')
    document.querySelector('.font-size-box').style.display = 'none';
    hideBox2();
    document.querySelector('.generator-box').style.color = choiceColor;
    document.querySelectorAll('p').forEach((element) => {
      element.style.color = choiceColor;
    });
  });
});
const exitColorDropdown = document.querySelector('.exit-color-dropdown');
const exitBackgroundDropdown = document.querySelector('.exit-background-dropdown');
exitColorDropdown.addEventListener('click', () => {
  document.querySelector('.color-dropdown-box').style.display = 'none';
});
exitBackgroundDropdown.addEventListener('click', () => {
  document.querySelector('.background-dropdown-box').style.display = 'none';
});



programInfoBtn = document.querySelector(".program-info-btn");
programInfoBtn.addEventListener('click', async () => {
  document.querySelector('.font-size-box').style.display = 'none';
  // Get information about this project from the server
  await getProgramInfo();
});



document.querySelector('.increment').addEventListener('click', () => {
  updateCounter(1);
});

document.querySelector('.decrement').addEventListener('click', () => {
  updateCounter(-1);
});

document.querySelector('.increment').addEventListener('mousedown', () => {
  interval = setInterval(() => {
    updateCounter(1);
  }, 150);
});

document.querySelector('.increment').addEventListener('mouseup', () => {
  clearInterval(interval);
});

document.querySelector('.increment').addEventListener('touchstart', () => {
  interval = setInterval(() => {
    updateCounter(1);
  }, 150);
});

document.querySelector('.increment').addEventListener('touchend', () => {
  clearInterval(interval);
});

document.querySelector('.increment').addEventListener('touchcancel', () => {
  clearInterval(interval);
});

document.querySelector('.decrement').addEventListener('mousedown', () => {
  interval = setInterval(() => {
    updateCounter(-1);
  }, 150);
});

document.querySelector('.decrement').addEventListener('mouseup', () => {
  clearInterval(interval);
});

document.querySelector('.decrement').addEventListener('touchstart', () => {
  interval = setInterval(() => {
    updateCounter(-1);
  }, 150);
});

document.querySelector('.decrement').addEventListener('touchend', () => {
  clearInterval(interval);
});

document.querySelector('.decrement').addEventListener('touchcancel', () => {
  clearInterval(interval);
});


function updateCounter(value) {
  const counterElement = document.querySelector('.font-counter');
  let currentCount = parseInt(counterElement.textContent, 10);
  if (counterCheck > 9 && counterCheck < 25) {
    currentCount += value;
    counterElement.textContent = currentCount;
    counterCheck += value;
    document.querySelector('.generator-box').style.fontSize = counterCheck + "px";
    document.querySelectorAll('p').forEach((element) => {
      fontSize = counterCheck;
      element.style.fontSize = counterCheck + "px";
    });
  } else {
    document.querySelector('.decrement').style.display = "none";
    document.querySelector('.increment').style.display = "none";
    setTimeoutFunc();
  }
}


function setTimeoutFunc() {
  setTimeout(() => {
    document.querySelector('.font-counter').textContent = 14;
    document.querySelector('.decrement').style.display = "flex";
    document.querySelector('.increment').style.display = "flex";
    counterCheck = 14;
    fontSize = 14;
  }, 5000);
}


const changeOtherBtn = document.getElementById('change-other-btn');
changeOtherBtn.addEventListener('click', () => {
  document.querySelector('.font-dropdown-box').style.display = "none";
  document.querySelector('.thread-dropdown-box').style.display = "none";
  const fontSizeBox = document.querySelector('.font-size-box');

  fontSizeBox.style.display = fontSizeBox.style.display === "block" ? "none" : "block";
});


function showBox() {
  const animatedBox = document.querySelector('.appearing-box');
  animatedBox.classList.add('visible');
}
function hideBox() {
  const animatedBox = document.querySelector('.appearing-box');
  animatedBox.classList.remove('visible');
}


const fontSizeBoxBtn = document.querySelector('.font-size-box-btn');
fontSizeBoxBtn.addEventListener('click', () => {
  showBox();
  const fontSizeBox = document.querySelector('.font-size-box');
  fontSizeBox.style.display = "none";
});


okay.addEventListener('click', () => {
  hideBox();
});




(() => {
  changeFontBtn.addEventListener('click', () => {
    document.querySelector('.thread-dropdown-box').style.display = "none";
    document.querySelector('.font-size-box').style.display = "none";
    //document.querySelector('.font-size-box-btn').style.display = "none";

    const fontDropdownBox = document.querySelector('.font-dropdown-box');
    fontDropdownBox.style.display = fontDropdownBox.style.display === 'block' ? 'none' : 'block';
  });
})();

function changeFontFamily(font_family) {
  const generatorBox = document.querySelector('.generator-box');
  const allParagraphs = document.querySelectorAll('p');
  const allH3 = document.querySelectorAll('h3');
  const allH1 = document.querySelectorAll('h1');
  const allSpan = document.querySelectorAll('span');
  const allUl = document.querySelectorAll('ul');
  const allLi = document.querySelectorAll('li');

  fontFamily = font_family;

  generatorBox.style.fontFamily = font_family;
  allH3.forEach((element) => {
    element.style.fontSize = "20px";
  });
  allH1.forEach((element) => {
    element.style.fontSize = "20px";
  });


  allParagraphs.forEach(paragraph => {
    paragraph.style.fontSize = fontSize;
    if (font_family === "Whisper") {
      paragraph.style.fontSize = "30px";
    }
    paragraph.style.fontFamily = font_family;
  });

  allSpan.forEach((element) => {
    element.style.fontFamily = fontFamily;
  });

  allUl.forEach((element) => {
    element.style.fontFamily = fontFamily;
  });

  allLi.forEach((element) => {
    element.style.fontFamily = fontFamily;
  });

  if (font_family === "Whisper") {
    generatorBox.style.fontSize = "40px";
    allH3.forEach((element) => {
      element.fontSize = "22px";
    });
    allH1.forEach((element) => {
      element.style.fontSize = "22px";
    });
  }
}


(() => {
  const fontDropdowns = document.querySelectorAll('.font-dropdown');
  fontDropdowns.forEach((fontDropdown) => {
    fontDropdown.addEventListener('click', () => {
      changeFontFamily(fontDropdown.textContent);
      fontDrodownBox.style.display = "none";
    });
  });
})();





/*
<div class="confirm-new-thread">                                             <span class="accept-label">Sure you want a new thread?</span>              <div class="confirm-new-thread-btns">                                        <span class="accept-btn">Yes</span>                                        <span class="decline-btn">No</span>                                      </div>                                                                   </div>
*/


function newThreadShow() {
  const confirmNewThread = document.querySelector('.confirm-new-thread');
  confirmNewThread.classList.add('visible');
}
function newThreadHide() {
  const confirmNewThread = document.querySelector('.confirm-new-thread');
  confirmNewThread.classList.remove('visible');
}


const NewThreadBtn = document.getElementById('request-new-thread');
const acceptBtn = document.querySelector('.accept-btn');
const declineBtn = document.querySelector('.decline-btn');

NewThreadBtn.addEventListener('click', () => {
  newThreadShow();
});
acceptBtn.addEventListener('click', async () => {
  newThreadHide();
  if (newThreadController) {
    newThreadController = false;
    const loadingBox = document.querySelector('.loading-box2');
    loadingBox.style.display = "block";
    buttonColor(NewThreadBtn);
    await sendCroppedImage(false, "new thread", "new", 0);
    newThreadController = true;
    loadingBox.style.display = "none";
  }
});
declineBtn.addEventListener('click', async () => {
  newThreadHide();
});

function buttonColor(element, color = "green") {
  let originalColor = "blue";

  if (color === "pink") {
    originalColor = "green";
  }
  // Change the button color to green
  element.style.backgroundColor = color;

  // Set a timeout to reset the color after 2 seconds (adjust as needed)
  setTimeout(() => {
    element.style.backgroundColor = originalColor;
  }, 500);
}


// Defining and calling the function at the same time
(() => {
  const threadSelector = document.getElementById('thread-selector');
    threadSelector.addEventListener('click', () => {
      document.querySelector('.font-size-box').style.display = "none";
      //document.querySelector('.font-size-box-btn').style.display = "none";
      document.querySelector('.font-dropdown-box').style.display = "none"; 
      buttonColor(threadSelector);
      const threadDropdownBox = document.querySelector('.thread-dropdown-box');
      threadDropdownBox.style.display = threadDropdownBox.style.display === "block" ? "none" : "block";
    });
})();

function addListenersToThreadButtons() {
  const threadDropdownBox = document.querySelector('.thread-dropdown-box');
  const threadDropDowns = document.querySelectorAll('.thread-dropdown');
  threadDropDowns.forEach((element) => {
    element.addEventListener('click', async () => {
      buttonColor(element, 'pink');
      threadChosen = element.textContent;
      threadDropdownBox.style.display = 'none';
      //alert(parseInt(threadChosen));
      await sendCroppedImage(false, false, "active", parseInt(threadChosen));
    });
  });
}
// Call it initially after loading
addListenersToThreadButtons();



function generateThreadButtons(array) {
  const threadDropdownBox = document.querySelector('.thread-dropdown-box');
  // Empty it to hold the newly generated elements
  threadDropdownBox.innerHTML = "";

  // Sorting the array in ascending order
  array.sort((a, b) => a - b);

  for (const num of array) {
    // Create a new div element for each thread
    const element = document.createElement('div');
    element.className = 'thread-dropdown';
    element.innerHTML = num;

    // Append the element to threadDropdownBox
    threadDropdownBox.appendChild(element);
  }
  addListenersToThreadButtons();
}

// Call it initially after loading
if (threadsDataSequence) {
  generateThreadButtons(threadsDataSequence);
}









sendPromptBtn.addEventListener('click', async () => {
  if (textArea.value) {
    //alert("sending prompt");
    const loadHolder = document.querySelector('.loading-box');
    const starContMain = document.querySelector('.star-container-main');
    const generatorBox = document.querySelector('.generator-box');
    const btns = document.querySelectorAll('.btnBtn');
    const textArea = document.getElementById('text-area');

    btns.forEach((element) => {
      element.style.display = 'none';
    });

    //generatorBox.style.display = 'none';
    imageContainer.style.display = 'none';
    loadHolder.style.display = 'flex';
    //starContMain.style.display = 'flex';
    //alert("here");
    await sendCroppedImage(false, textArea.value);
    //alert("here two");
    loadHolder.style.display = 'none';
    //starContMain.style.display = 'none';
    generatorBox.style.display = 'block';
    textArea.value = "";
  }
});




choosePhoto.addEventListener('click', (e) => {
  const btns = document.querySelectorAll('.btnBtn');
  btns.forEach((element) => {
    element.style.display = 'flex';
    if (element.id = "download") {
      element.classList.add('hide');
    }
  });

  handleFileSelect();
});


fileInput.addEventListener('change', handleFileSelect);

function handleFileSelect() {
    //alert("file load");
    document.querySelector('.container').style.display = "flex";
    downloadButton.classList.add("hide");

    let reader = new FileReader();
    reader.readAsDataURL(fileInput.files[0]);

    reader.onload = () => {
        image.setAttribute("src", reader.result);

        image.onload = () => {
            if (cropper) {
                cropper.destroy();
            }

            //cropper = new Cropper(image);
            cropper = new Cropper(image, {
              scalable: false,
              zoomable: false,
            });


            options.forEach((element) => {
                element.classList.remove("hide");
            });

            previewButton.classList.remove("hide");
        };
    };
}



//Set aspect ration
aspectRatio.forEach((element) => {
  element.addEventListener("click", () => {
    if (element.innerText == "Free") {
      cropper.setAspectRatio(NaN);
    } else {
      cropper.setAspectRatio(eval(element.innerText.replace(":", "/")));
    }
  });
});


previewButton.addEventListener("click", (e) => {
  const loadHolder = document.getElementById('load-tmp-holder');
  loadHolder.style.display = 'flex';

  e.preventDefault();
  // Get cropped canvas and perform actions
  let imgSrc = cropper.getCroppedCanvas().toDataURL();
  imgSrc = cropper.getCroppedCanvas().toDataURL();
  previewImage.src = imgSrc;
  /*downloadButton.download = `cropped_${fileName}.png`;
  downloadButton.setAttribute("href", imgSrc);*/
  downloadButton.classList.remove("hide");

  loadHolder.style.display = 'none';
});

downloadButton.addEventListener('click', async (e) => {
  const loadHolder = document.querySelector('.loading-box');
  const starContMain = document.querySelector('.star-container-main');
  const generatorBox = document.querySelector('.generator-box');
  const btns = document.querySelectorAll('.btnBtn');
  const textArea = document.getElementById('text-area');

  btns.forEach((element) => {
    element.style.display = 'none';
  });

  e.preventDefault();

  //generatorBox.style.display = 'none';
  imageContainer.style.display = 'none';
  loadHolder.style.display = 'flex';
  //starContMain.style.display = 'flex';
  await sendCroppedImage(true, textArea.value);
  loadHolder.style.display = 'none';
  //starContMain.style.display = 'none';
  generatorBox.style.display = 'block';
});


// Make an HTTP Post request to the Flask API endpoint
async function getProgramInfo() {
  fetch('/get_program_info')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data && data.program_intro) {
        console.log('Retrieved Data:', data);
        const generatorBox = document.querySelector('.generator-box');
        // Use the replace method to replace all occurrences of "&bksl;" with a backslash
        const inputString = data.program_intro;
        const outputString = inputString.replace(/&bksl;/g, "\\");
        generatorBox.innerHTML = outputString;

        // Trigger MathJax rendering
        MathJax.typeset();
      } else {
        console.error('Server response indicates failure:', data.error);
      }
      // Reset font styles
      const elementsToStyle = ['p', 'ul', 'li', 'span', '.generator-box'];
      elementsToStyle.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          if (selector === 'p' || selector === 'generator-box') {
            if (choiceColor) {
              element.style.color = choiceColor;
            }
          }
          element.style.fontFamily = fontFamily;
        });
      });
    })
    .catch(error => {
      alert(`Error: ${error}`);
      console.error('Error fetching data:', error);
    });
}








async function sendCroppedImage(imagePrompt = false, textPrompt = '', threadStatus = "active", threadNum = 0) {
  let headers = {'File-Type': 'Text'};
  const formData = new FormData();
  formData.append('thread_status', threadStatus);
  formData.append('prompt', textPrompt);
  formData.append('thread_num', threadNum);

  if (imagePrompt) {
    const canvas = cropper.getCroppedCanvas();
    const blob = await new Promise(resolve => canvas.toBlob(resolve));
    formData.append('image', blob, 'cropped_image.png');
    headers = {'File-Type': 'Image'};
  }

  try {
    const response = await fetch('/zmc_assistant_data', {
      method: 'POST',
      body: formData,
      headers: headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log(data);

    if (data.success) {
      const generatorBox = document.querySelector('.generator-box');
      const threadIdHolder = document.getElementById('thread-id-holder');

      // Save thread_id
      if (data.hasOwnProperty('thread_id')) {
        threadIdHolder.textContent = data.thread_id
      }

      // Replace all occurrences of "&bksl;" with a backslash
      const inputString = data.response_text;
      const outputString = inputString.replace(/&bksl;/g, "\\");
      generatorBox.innerHTML = outputString;

      // Trigger MathJax rendering
      MathJax.typeset();

      // Update tokens div element
      const tokensCounter = document.querySelector('.tokens-counter');
      tokensCounter.textContent = data.tokens_count;
      //alert(data.tokens_count)
      const integerValue = parseInt((data.tokens_count).replace(/,/g, ''), 0);
      if (integerValue <= 1000) {
        tokensCounter.style.color = "#FF0000";
      }

      console.log('Image successfully processed on the server.');
    } else {
      console.error('Server response indicates failure:', data.error);
    }

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

    document.getElementById('blur-div').style.bottom = 0;
  } catch (error) {
    alert(`Send Cropped Image Function Error = ${error}`);
    console.error('Error sending or processing cropped image:', error);
  }
}




