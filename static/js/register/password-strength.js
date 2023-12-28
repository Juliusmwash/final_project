document.addEventListener('DOMContentLoaded', function () {
  // Function to check password strength
  function passwordStrength(password) {
    // Check length
    if (password.length < 8) {
      return "Weak";
    }

    if (password.length >= 8 && /\d/.test(password)) {
      // The string is 8 characters or longer and contains at least one digit
      return 'Strong'
    }

    if (password.length >= 8 && /[A-Z!@#$%^&*()_+{}\[\]:;<>,.?~\\]/.test(password)) {
      // The string is 8 characters or longer and contains at least a capital letter or special character
      return 'Strong'
    }

    // Check for numbers and special characters
    if (!/\d/.test(password) || !/[!@#$%^&*()_+{}\[\]:;<>,.?~\\\-|=]/.test(password)) {
      return "Fair";
    }

    return "Strong";
  }

  // Get references to the input fields and password strength display
  const passwordInput = document.getElementById('password');
  const passwordStrengthDisplay = document.getElementById('password-strength');
  const confirmPassword = document.getElementById('confirm-password');
  const errorDiv = document.getElementById('password-error');
  const errorLengthDiv = document.getElementById('password-length-error');
	const passwordBox = document.getElementById('password-box');
	const confirmPasswordBox = document.getElementById('confirm-password-box');


  passwordInput.addEventListener('blur', () => {
    if (passwordInput.value.length < 8 && passwordInput.value !== '') {
        passwordStrengthDisplay.style.display = 'none';
        errorLengthDiv.style.display = 'flex';
        passwordInput.focus();
        passwordInput.value = '';
        passwordBox.style.borderColor = '#FF0000';
    } else if (passwordInput.value.length >= 8) {
      passwordBox.style.borderColor = '';
    }
  });




  // Check if a password is 8 characters long or more
  function passwordLengthCheck (pwdError) {
	  if (pwdError === "lengthError") {
		  passwordStrengthDisplay.textContent = "Password is less than 8 characters";
		  passwordBox.style.borderBottomColor = '#ff0000';
		  passwordStrengthDisplay.style.display = 'flex';
	  } else if (pwdError === "mismatch") {
		  errorDiv.style.display = 'flex';
		  confirmPasswordBox.style.borderBottomColor = '#FF0000';
		  confirmPassword.focus();
		  confirmPassword.value = '';
	  }
  }
  
  // Event listener for password input
  passwordInput.addEventListener('input', function () {
    const password = passwordInput.value;
    const strength = passwordStrength(password);

    errorLengthDiv.style.display = 'none';

    // Display password strength
    passwordStrengthDisplay.style.display = 'flex';
		// Condition to change strength colour
		if (strength === "Weak") {
			passwordStrengthDisplay.style.color = "red";
		} else if (strength === "Fair") {
			passwordStrengthDisplay.style.color = "orange";
		} else {
			passwordStrengthDisplay.style.color = "green";
		}
		// set errorDiv text content
    passwordStrengthDisplay.textContent = `Password strength: ${strength}`;

		// Set error div display to none
		// It should only be visible if there is password confirmation error
		errorDiv.style.display = 'none';
  });

  // Function to handle password confirmation
  function handlePasswordConfirmation() {
    // Check if input1 and input2 are not equal
    if (passwordInput.value !== confirmPassword.value) {
      // Display errorDiv
      errorDiv.style.display = 'flex';
			// Set border color to red
			confirmPasswordBox.style.borderBottomColor = '#FF0000';

      // Clear values of input1 and input2
      //passwordInput.value = '';
      confirmPassword.value = '';

      // Set focus back to passwordInput
      passwordInput.focus();
			//confirmPassword.focus();
    } else {
			passwordBox.style.borderBottomColor = '';
			confirmPasswordBox.style.borderBottomColor = '';
			//passwordStrengthDisplay.style.display = 'flex';
      // Hide errorDiv if both fields are not empty and match
      if (passwordInput.value && confirmPassword.value) {
        errorDiv.style.display = 'none';
      }
    }
  }

  // Event listener for password input losing focus
  passwordInput.addEventListener('blur', function () {
    // When input1 loses focus, hide password strength display
    passwordStrengthDisplay.style.display = 'none';
  });

  // Event listener for confirmPassword input losing focus
  confirmPassword.addEventListener('blur', function () {
    // When confirmPassword loses focus, handle password confirmation
    handlePasswordConfirmation();
  });

  // Event listener for Enter key press in confirmPassword field
  confirmPassword.addEventListener('keydown', function (event) {
    // Check if Enter key (key code 13) was pressed
    if (event.keyCode === 13) {
      // Check if input1 and input2 are not equal
      handlePasswordConfirmation();
    }
  });
});

