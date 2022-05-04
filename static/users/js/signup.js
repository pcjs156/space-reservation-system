const passwordCheckToast = new bootstrap.Toast(document.getElementById('liveToast'));

const passwordInput = document.getElementById('password');
const passwordCheckInput = document.getElementById('password-check');
const submitButton = document.getElementById('submitButton');

submitButton.addEventListener('click', function (event) {
    if ((passwordInput.value.length === 0 || passwordCheckInput.value.length === 0)
        || (passwordInput.value !== passwordCheckInput.value)) {

        passwordCheckToast.show();

        event.preventDefault();
    }
})