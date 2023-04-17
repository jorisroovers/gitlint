document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("table").forEach(function (table) {
        table.classList.add("docutils");
    });

    document.querySelectorAll(".termynal").forEach(function (termynalEl) {
        new Termynal(termynalEl);
    });
});




