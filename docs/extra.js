document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("table").forEach(function (table) {
        table.classList.add("docutils");
    });
});

var termynal = new Termynal('#termynal', { startDelay: 600 });
