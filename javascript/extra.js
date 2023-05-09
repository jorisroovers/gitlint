document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".termynal").forEach(function (termynalEl) {
        new Termynal(termynalEl);
    });

    // Redirect /gitlint/configuration/#regex-style-search to /gitlint/configuration/general_options/#regex-style-search
    // This is to support old links that are in gitlint's CLI Output
    // If the trailing slash is missing from /gitlint/configuration, mkdocs will redirect to the trailing slash version,
    // and then this code will redirect to the correct page
    if (window.location.pathname == "/gitlint/configuration/" && window.location.hash === "#regex-style-search") {
        window.location.href = "/gitlint/configuration/general_options/#regex-style-search";
    }
});
