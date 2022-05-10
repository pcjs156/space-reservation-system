const withdrawConfirmBtn = document.getElementById('withdrawConfirmBtn');
let withdrawConfirmModal = document.getElementById('withdrawConfirmModal');
withdrawConfirmModal = new bootstrap.Modal(withdrawConfirmModal);

withdrawConfirmBtn.addEventListener('click', () => {
    withdrawConfirmModal.show();
});

