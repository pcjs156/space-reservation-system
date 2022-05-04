const onLogoutButtonMouseOver = function () {
    const logoutButton = document.getElementById('logout-button');
    logoutButton.innerText = 'Seriously?';
};

const onLogoutButtonMouseOut = function () {
    const logoutButton = document.getElementById('logout-button');
    logoutButton.innerText = 'Logout';
};

const onLoginButtonMouseOver = function () {
    const loginButton = document.getElementById('login-button');
    loginButton.innerText = 'Hello!';
};

const onLoginButtonMouseOut = function () {
    const loginButton = document.getElementById('login-button');
    loginButton.innerText = 'Login';
};

const onLogoMouseOver = function () {
    const logo = document.getElementById('header-central-logo');

    const pathList = (new URL(logo.src)).pathname.split('/');
    pathList.pop();
    pathList.push('logo_transparent_darker.png');

    logo.src = pathList.join('/');
};

const onLogoMouseOut = function () {
    const logo = document.getElementById('header-central-logo');

    const pathList = (new URL(logo.src)).pathname.split('/');
    pathList.pop();
    pathList.push('logo_transparent.png');

    logo.src = pathList.join('/');
};

const onSignUpButtonMouseOver = function () {
    const signUpButton = document.getElementById('sign-up-button');
    signUpButton.innerText = 'Welcome!';
};

const onSignUpButtonMouseOut = function () {
    const signUpButton = document.getElementById('sign-up-button');
    signUpButton.innerText = 'Sign Up';
};

function getUrlParams() {
    const params = {};

    window.location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi,
        function (str, key, value) {
            params[key] = value;
        }
    );

    return params;
}

const popupToast = function (emoji, strongMsg, body) {
    const baseToast = new bootstrap.Toast(document.getElementById('baseToast'));

    const baseToastEmoji = document.getElementById('baseToastEmoji');
    const baseToastStrongMsg = document.getElementById('baseToastStrongMsg');
    const baseToastBody = document.getElementById('baseToastBody');

    baseToastEmoji.innerText = emoji;
    baseToastStrongMsg.innerText = strongMsg;
    baseToastBody.innerText = body;

    baseToast.show();
    console.log('hi')

    setTimeout(() => {
        baseToast.hide();
    }, 3000);
};

if (window.addEventListener) {
    const urlParams = getUrlParams();

    window.addEventListener('load', function () {
        if (urlParams.toastType !== undefined) {
            if (urlParams.toastType === 'signUp') {
                popupToast('👋', 'Welcome!', 'Say hello to ZZIM.');
            } else if (urlParams.toastType === 'login') {
                popupToast('😍', 'Hi!', 'Welcome back!');
            }
        }
    });
} else {
    const urlParams = getUrlParams();

    window.attachEvent('onload', function () {
        if (urlParams.toastType !== undefined) {
            if (urlParams.toastType === 'signUp') {
                popupToast('👋', 'Welcome!', 'Say hello to ZZIM.');
            } else if (urlParams.toastType === 'login') {
                popupToast('😍', 'Hi!', 'Welcome back!');
            }
        }
    });
}
;