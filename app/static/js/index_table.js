$(function () {
    var $overview = $("#overview");
    var $template = $("#template").find("> tbody > *");

    function setProgress($file, value) {
        var $progressBar = $file.parent().find(".progress-bar");

        $progressBar.css("width", value + "%");
        $progressBar.find("span").html(value + "%");
    }

    socket.on("file_added", function(msg) {
        var $file = $template.clone().appendTo("#overview > tbody").fadeIn("slow");
        $file.attr("data-file-id", msg.data.id);
        $file.find(".filename").html(msg.data.filename);
    });

    socket.on("file_progress", function (msg) {
        var $file = $overview.find("tr[data-file-id='" + msg.data.id + "']");
        $file.find(".progress-bar").removeAttr("style");

        $file.find(".additional_info").html(msg.data.fps + " fps");
        $file.find(".eta").html(msg.data.eta);
        $file.find(".bitrate").html(msg.data.bitrate + " kbits/s");
        $file.find(".status").html(msg.data.progress + "% / " + msg.data.size);

        setProgress($file, msg.data.progress);
    });

    // listen to the "file_done" event - this happens, whenever a file is finished processing
    socket.on("file_done", function(msg) {
        var $file = $overview.find("tr[data-file-id='" + msg.data.id + "']");

        if ($file.length != 0) {
            $file.fadeOut("slow", function() {
                $(this).remove();
            })
        }
    });

    // at the beginning we need to initially load all the files
    socket.emit("file_progress", {});
});