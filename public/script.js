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

    $("#zip").click(function(e) {
        dl_button = $(this);
        dl_button.html('Generating zip...');
        $("#logoutput").html('Generating zip file...');

        $.post("/downloadzip", {"url": $("input[name='url']").val(),
                             "quality": $("select[name='quality']").val(),
                             "email": $("input[name='email']").val(),
                             "password": $("input[name='password']").val()})
         .done(function(string) {
             // var a = document.createElement('a');
             // var url = window.URL.createObjectURL(data);
             // a.href = url;
             // a.download = 'myfile.pdf';
             // document.body.append(a);
             // a.click();
             // a.remove();
             // window.URL.revokeObjectURL(url);
             dl_button.html('Download .Zip');
             $("#logoutput").html(string);
         });
        e.preventDefault();
    });

    $("#clean").click(function(e) {
        clean_button = $(this);
        clean_button.html('Cleaning...');
        $("#logoutput").html('Cleaning server...');

        $.post("/clean", {})
         .done(function(string) {
             clean_button.html('Clean');
             $("#logoutput").html(string);
         });
        e.preventDefault();
    });

});
