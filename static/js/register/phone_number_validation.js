document.addEventListener('DOMContentLoaded', function () {
  // Get the input element by its id
  const phoneNumberInput = document.getElementById('phone-number');

  // Get the error div element by its id
  const errorDiv = document.getElementById('phone-num-error');

  // Get the parenting element
  const phoneParent = document.getElementById('mobile-number-box');

  // Regular expressions to match the specified conditions
  const startsWithPlus254 = /^\+254\d{9}$/;
  const startsWith07or01 = /^(07|01)\d{8}$/;

  // Function to check the entered number
  function checkPhoneNumber() {
    // Get the entered phone number
    const phoneNumber = phoneNumberInput.value.trim();

    // Check if the number matches the conditions
    if (startsWithPlus254.test(phoneNumber) || startsWith07or01.test(phoneNumber)) {
      errorDiv.style.display = 'none'; // Hide the error div
      phoneParent.style.borderColor = '';
    } else {
			if (phoneNumberInput.value) {
      	errorDiv.style.display = 'flex'; // Show the error div
        // set parent border color to red
        phoneParent.style.borderColor = '#FF0000';
      	// Set focus back to the input
      	phoneNumberInput.focus();
			}
    }
  }

  // Add an event listener to check the number when the Enter key is pressed
  phoneNumberInput.addEventListener('keydown', function (event) {
    if (event.keyCode === 13) { // Check if Enter key (key code 13) was pressed
      checkPhoneNumber();
    }
  });

  // Add an event listener to check the number when the input goes out of focus
  phoneNumberInput.addEventListener('blur', checkPhoneNumber);

  // Run the checkPhoneNumber function once when the page has fully loaded
  checkPhoneNumber();
});

