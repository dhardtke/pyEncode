$(function () {
    var $overview = $("#overview");
    var $template = $("#template").find("> tbody > *");

    function setProgress($file, value) {
        var $progressBar = $file.parent().find(".progress-bar");

        $progressBar.css("width", value + "%");
        $progressBar.find("span").html(value + "%");
    }

    socket.on("file_progress", function (msg) {
        // iterate over each file
        $.each(msg.data, function (key, value) {
            var $file = $overview.find("tr[data-file-id='" + key + "']");

            // if $file does not yet exists
            if ($file.length == 0) {
                $file = $template.clone().appendTo("#overview > tbody").fadeIn("slow");
                $file.attr("data-file-id", key);
                $file.find(".filename").html(value["filename"]);
            } else {
                // only animate .progress-bar when updating
                $file.find(".progress-bar").removeAttr("style");
            }

            $file.find(".additional_info").html(value.fps + " fps");
            $file.find(".eta").html(value.eta);
            $file.find(".bitrate").html(value.bitrate + " kbits/s");
            $file.find(".status").html(value.progress + "% / " + value.size);

            setProgress($file, value.progress);
        });
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