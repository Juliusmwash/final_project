document.addEventListener("DOMContentLoaded", function() {
  const messageBox = document.querySelector('.message-box');
  const successfulRegMessage = document.getElementById('successful-reg-message');
  const timerLogicBox = document.querySelector('.timer-logic-box');
  const textInputs = document.querySelectorAll('input[type="text"]');
  const errorBox = document.querySelector('.error-box');
  const newCodeButton = document.getElementById('new-code-button');


  function verifyUser(event) {
    // Prevent the default behaviour
    event.preventDefault();

    const ver_key = processDigits();
    const myForm = document.getElementById('my-form').submit();
  }


  // Get all the input elements with the class "digit-input"
  const digitInputs = document.querySelectorAll(".digit-input");

  // Set focus on the first input element
  if (digitInputs.length > 0) {
    digitInputs[0].focus();
    digitInputs[0].removeAttribute("placeholder");
  }

  // Define a bolean variable for controlling function calls
  let callProcess = false;
  let firstCall = true;
  let tmpValue = '';
  let setNum = true;

  // Add event listeners to input fields
  digitInputs.forEach((inputElement, i) => {
    inputElement.addEventListener('focus', function () {
      // Clear the placeholder when the input is in focus
      inputElement.removeAttribute('placeholder');
    });

  inputElement.addEventListener('blur', function () {
    // Clear the placeholder when the input is in focus
    if (inputElement.value === '') {
      inputElement.setAttribute('placeholder', 'X');
    }
  });


  inputElement.addEventListener('input', function () {
    const maxLength = parseInt(inputElement.getAttribute('maxlength'), 10);
    if (inputElement.value.length >= maxLength) {
      if (firstCall) {
        tmpValue = inputElement.value;
        firstCall = false;
      }

      // Distribute excess characters to the next input elements
      for (let j = 1; j < tmpValue.length; j++) {
        if (setNum) {
          inputElement.value = tmpValue[0];
          inputElement.setAttribute('maxlength', '1');
          setNum = false;
        }
        if (i + j < digitInputs.length) {
          digitInputs[i + j].focus();
          digitInputs[i + j].value = tmpValue[j];
          if (j === digitInputs.length - 1) {
            callProcess = true;
          }
        }
      }
      firstCall = false;
      tmpValue = '';
    }

    if (!callProcess) {
      if (inputElement.value.length === 1 && i < digitInputs.length - 1) {
        digitInputs[i + 1].focus();
      }
    }

    inputElement.setAttribute('maxlength', '1');

    if (i === digitInputs.length - 1 || callProcess) {
      processDigits();
    }
    callProcess = false;
  });
});




  // Function to process the entered digits
  function processDigits() {
    // Get the values of all the digit inputs
    const digits = Array.from(digitInputs).map(function(input) {
      return input.value;
    });

    // Join the digits into a single string
    const digitString = digits.join("");

    // Convert the string to an integer
    const intValue = parseInt(digitString);

    // Set the integer value as the text content of the div
    const submit_input  = document.getElementById("submission");
  	submit_input.value = intValue;

    // Return the parsed value
    return intValue;
  }

  const verifyButton = document.getElementById("verify-button");
  verifyButton.addEventListener("click", verifyUser);
});


