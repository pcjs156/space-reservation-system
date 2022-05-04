const onLogoutButtonMouseOver = function () {
    const logoutButton = document.getElementById('logoutButton');
    logoutButton.innerText = 'Seriously?';
};

const onLogoutButtonMouseLeave = function () {
    const logoutButton = document.getElementById('logoutButton');
    logoutButton.innerText = 'Logout';
};

const onLoginButtonMouseOver = function () {
    const loginButton = document.getElementById('loginButton');
    loginButton.innerText = 'Welcome!';
}

const onLoginButtonMouseLeave = function () {
    const loginButton = document.getElementById('loginButton');
    loginButton.innerText = 'Login';
}