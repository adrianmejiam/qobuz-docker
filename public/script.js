$(document).ready(function() {

    $("#download").click(function(e) {
        dl_button = $(this);
        dl_button.html('Downloading...');
        $("#logoutput").html('Loading...');

        $.post("/download", {"url": $("input[name='url']").val()})
            .done(function(string) {
                dl_button.html('Download');
                $("#logoutput").html(string);
            });
        e.preventDefault();
    });
});
