// 그룹 삭제 관련
const groupDeleteBtn = document.getElementById('groupDeleteBtn');

let groupDeleteModal = document.getElementById('groupDeleteModal');
groupDeleteModal = new bootstrap.Modal(groupDeleteModal);

const groupNameInput = document.getElementById('groupNameInput');
const groupName = groupNameInput.getAttribute('placeholder');

const groupDeleteConfirmBtn = document.getElementById('groupDeleteConfirmBtn');

groupDeleteBtn.addEventListener('click', () => {
    groupDeleteModal.show();
});

groupNameInput.addEventListener('input', () => {
    groupDeleteConfirmBtn.disabled = groupNameInput.value !== groupName;
});

// 그룹 초대 코드 변경 관련
const groupInviteCodeInput = document.getElementById('groupInviteCodeInput');

const reissueInviteCodeBtn = document.getElementById('reissueInviteCodeBtn');
reissueInviteCodeBtn.addEventListener('click', () => {
    const requestURL = reissueInviteCodeBtn.getAttribute('requestURL');
    const httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
        alert('Failed to request: code 01');
    }

    httpRequest.onreadystatechange = () => {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                const result = JSON.parse(httpRequest.responseText);
                groupInviteCodeInput.setAttribute('value', result.new_invite_code);
            } else {
                alert('Failed to request: code 02');
            }
        }
    };

    httpRequest.open('GET', requestURL);
    httpRequest.send();
});