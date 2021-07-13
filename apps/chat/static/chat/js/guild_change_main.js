let deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
const input = document.getElementById('id_deleteConfirm');

function deleteGuild() {
    if (input.value === guildName) {
        document.location.href = deleteUrl;
    }
}

function modalOpen() {
    input.value = '';
    deleteModal.show();
}