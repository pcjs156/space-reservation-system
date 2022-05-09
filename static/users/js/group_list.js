const new_group_btn = document.getElementById('new_group_btn');
let new_group_modal = document.getElementById('new_group_modal');
new_group_modal = new bootstrap.Modal(new_group_modal);

new_group_btn.addEventListener('click', () => {
    new_group_modal.show();
});

const popupGroupCreateToast = function () {
    const groupCreateToast = new bootstrap.Toast(document.getElementById('groupCreateToast'));

    groupCreateToast.show();

    setTimeout(() => {
        groupCreateToast.hide();
    }, 3000);
};

if (window.addEventListener) {
    window.addEventListener('load', function () {
        popupGroupCreateToast();
    });
} else {
    window.attachEvent('onload', function () {
        popupGroupCreateToast();
    });
}
