document.addEventListener("DOMContentLoaded", function () {
    // JavaScript to handle the timer and input validation
    let timerInterval;
    let timerEndTime;
		const digitInputs = document.querySelectorAll('input[type="text"]');
		const verifyButton = document.getElementById('verify-button');
		const newCodeButton = document.getElementById('new-code-button');


		startCountdown(360); // Starting timer which reflects the server timing logics

    // Function to disable input fields after expiration
    function disableInputFields() {
        clearInterval(timerInterval);
        digitInputs.forEach(input => {
            input.disabled = true;
        });
    }


		function startCountdown(startingSeconds) {
    	let totalSeconds = startingSeconds;
    	const minutesElement = document.getElementById("time-min");
    	const secondsElement = document.getElementById("time-sec");

    	const countdownInterval = setInterval(function () {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;

        minutesElement.textContent = minutes.toString().padStart(2, '0');
        secondsElement.textContent = seconds.toString().padStart(2, '0');

        if (totalSeconds === 0) {
            clearInterval(countdownInterval); // Stop the countdown when it reaches 00:00
						verifyButton.style.backgroundColor = "lightgray";
						disableInputFields();
						
            verifyButton.style.display = "none";
						newCodeButton.style.display = "flex";
            
        } else {
            totalSeconds--;
        }
			}, 1000);
		}

		verifyButton.addEventListener("mouseenter", function() {
			verifyButton.style.opacity = 0.5;
		});

		// Reset opacity when mouse leaves the button
		verifyButton.addEventListener("mouseleave", function() {
			verifyButton.style.opacity = 1; // Set it back to 1 (fully opaque)
		});


		newCodeButton.addEventListener("mouseenter", function() {
			newCodeButton.style.opacity = 0.5;
		});

		// Reset opacity when mouse leaves the button
		newCodeButton.addEventListener("mouseleave", function() {
			newCodeButton.style.opacity = 1; // Set it back to 1 (fully opaque)
		});



		//startCountdown(300); // Start the countdown with 300 seconds (5 minutes)


});

