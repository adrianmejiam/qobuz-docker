$(document).ready(function() {

    $("#download").click(function(e) {
        dl_button = $(this);
        dl_button.html('Downloading...');
        $("#logoutput").html('Loading...');

        $.post("/download", {"url": $("input[name='url']").val(),
                             "quality": $("select[name='quality']").val(),
                             "email": $("input[name='email']").val(),
                             "password": $("input[name='password']").val()})
            .done(function(string) {
                dl_button.html('Download');
                $("#logoutput").html(string);
            });
        e.preventDefault();
    });
});
