// add current note text to 'edit note' form on inspo page
const $editButton = $('.edit-button')

function populateForm(e){
    let id = $(this).data('inspo-id');
    let note = $(`.note-${id}`).text().trim();

    let input = $(`#edit-note-modal-${id} .form-control`);
    input.val(note);
}

$editButton.on('click', populateForm)