function validacion(form) {
    let valid = true;
    form.querySelectorAll(".form-control").forEach(input => {
        if (!input.value) {
            valid = input.closest(".refaccion").querySelector(".item-nombre").innerText;
        }
    })
    return valid;
}
