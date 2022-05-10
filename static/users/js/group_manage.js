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