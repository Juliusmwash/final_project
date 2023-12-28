document.addEventListener('DOMContentLoaded', function() {
	const showPasswordButton = document.getElementById('label-confirm-password');
	const showConfirmPasswordButton = document.getElementById('label-password');
  const passwordInput = document.getElementById('password');
  const cfmPswdInput = document.getElementById('confirm-password');

  showPasswordButton.addEventListener('click', function () {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      /*const passwordIcon = showPasswordButton.querySelector('ion-icon[name="eye-off-outline"]');
      if (passwordIcon) {
        passwordIcon.setAttribute('name', 'eye-outline');
      }*/
    } else {
      passwordInput.type = "password";
      /*const passwordIcon = showPasswordButton.querySelector('ion-icon[name="eye-outline"]');
      if (passwordIcon) {
        passwordIcon.setAttribute('name', 'eye-off-outline');
      }*/
    }
  });

  showConfirmPasswordButton.addEventListener('click', function () {
    if (cfmPswdInput.type === "password") {
      cfmPswdInput.type = "text";
      /*const cfmPswdIcon = showConfirmPasswordButton.querySelector('ion-icon[name="eye-off-outline"]');
      if (cfmPswdIcon) {
        cfmPswdIcon.setAttribute('name', 'eye-outline');
      }*/
    } else {
      cfmPswdInput.type = "password";
      /*const cfmPswdIcon = showConfirmPasswordButton.querySelector('ion-icon[name="eye-outline"]');
      if (cfmPswdIcon) {
        cfmPswdIcon.setAttribute('name', 'eye-off-outline');
      }*/
    }
  });

  passwordInput.addEventListener('blur', function () {
    passwordInput.type = "password";
  });

  cfmPswdInput.addEventListener('blur', function () {
    cfmPswdInput.type = "password";
  });
});

