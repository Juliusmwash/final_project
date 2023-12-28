document.addEventListener("DOMContentLoaded", function() {
  function registerUser() {
    const data = {
			verificationCode: parsedVerificationCode,
			requestCategory: "newKey" // request mode
    };

    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    };

    fetch('/register', requestOptions)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('Registration successful:', data);
      })
      .catch(error => {
        console.error('Registration failed:', error);
      });
  }

  const newCodeButton = document.getElementById("new-code-button");
  newCodeButton.addEventListener("click", registerUser);
});

