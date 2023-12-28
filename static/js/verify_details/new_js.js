<!DOCTYPE html>
<html>
<head>
    <title>Number Input Form</title>
</head>
<body>
    <form id="myForm" action="your_server_script.php" method="post">
        <input type="text" class="digit-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
        <input type="text" class="digit-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
        <input type="text" class="digit-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
        <input type="text" class="digit-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
        <input type="submit" id="submitBtn" value="Submit">
        <div id="resultDiv"></div>
    </form>

    <script>
        // Get all the input elements with the class "digit-input"
        var digitInputs = document.querySelectorAll(".digit-input");

        // Add event listeners to each input for digit entry and focus control
        digitInputs.forEach(function(input, index) {
            input.addEventListener("input", function() {
                // Ensure that only one digit is entered
                if (this.value.length === 1) {
                    // Move focus to the next input, if available
                    if (index < digitInputs.length - 1) {
                        digitInputs[index + 1].focus();
                    } else {
                        // If it's the last input, prevent form submission and process the digits
                        event.preventDefault();
                        processDigits();
                    }
                }
            });
        });

        // Function to process the entered digits and submit the form
        function processDigits() {
            // Get the values of all the digit inputs
            var digits = Array.from(digitInputs).map(function(input) {
                return input.value;
            });

            // Join the digits into a single string
            var digitString = digits.join("");

            // Convert the string to an integer
            var intValue = parseInt(digitString);

            // Set the integer value as the text content of the div
            var resultDiv = document.getElementById("resultDiv");
            resultDiv.textContent = intValue;

            // Submit the form with the integer value
            document.getElementById("myForm").submit();
        }
    </script>
</body>
</html>

