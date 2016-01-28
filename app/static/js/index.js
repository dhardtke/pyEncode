$(function () {
    var $overview = $("#overview");
    var $template = $("#template").find("> tbody > *");

    function addFileToDOM(data) {
        var $file = $template.clone().appendTo("#overview > tbody").fadeIn("slow");
        $file.attr("data-file-id", data.id);
        $file.find(".filename").html(data.filename);

        return $file;
    }

    function setProgress($file, value) {
        var $progressBar = $file.parent().find(".progress-bar");

        $progressBar.css("width", value + "%");
        $progressBar.find("span").html(value + "%");
    }

    socket.on("file_added", function(msg) {
        addFileToDOM(msg.data);
    });

    socket.on("file_progress", function (msg) {
        var $file = $overview.find("tr[data-file-id='" + msg.data.id + "']");

        // add file if it does not yet exist
        if ($file.length == 0) {
            $file = addFileToDOM(msg.data);
        }

        $file.find(".progress-bar").removeAttr("style");

        $file.find(".additional_info").html(msg.data.fps + " fps");
        $file.find(".eta").html(msg.data.eta);
        $file.find(".bitrate").html(msg.data.bitrate + " kbits/s");
        $file.find(".status").html(msg.data.progress + "% / " + msg.data.size);

        setProgress($file, msg.data.progress);
    });

    // listen to the "file_done" event - this happens, whenever a file is finished processing
    socket.on("file_done", function(msg) {
        alert("done?");
        var $file = $overview.find("tr[data-file-id='" + msg.data.id + "']");

        if ($file.length != 0) {
            $file.fadeOut("slow", function() {
                $(this).remove();
            })
        }
    });
});