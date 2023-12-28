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

    // Initialise a form to send the verification code
    const formData = new FormData();
    formData.append("verification_code", parsedVerificationCode);
    alert(parsedVerificationCode);

    console.log("Request data:", data);

    const requestOptions = {
      method: 'POST',
      body: formData
    };

    console.log("Verification Code:", data.verificationCode);

    fetch('/verify_post', requestOptions)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        console.log("Registration Successful");
        //return response.text();
      })
  }

  // Assuming you have an HTML button with the id "verify-button"
  const verifyButton = document.getElementById("verify-button");
  verifyButton.addEventListener("click", verifyUser);
});

