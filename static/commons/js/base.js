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
    loginButton.innerText = 'Welcome!';
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