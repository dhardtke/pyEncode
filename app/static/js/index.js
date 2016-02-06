$(function () {
    var $overview = $("#overview");
    var $template = $("#template").find("> tbody > *");

    /**
     * add a new file to the DOM
     * @param data the file's data
     * @returns {*|{opacity}} the newly created file in the DOM
     */
    function addFileToDOM(data) {
        var $file = $template.clone().appendTo("#overview > tbody").fadeIn("slow");
        $file.attr("data-file-id", data.id);
        $file.find(".filename").html(data.filename);

        return $file;
    }

    /**
     * set the file data of an existing file
     * @param $file
     * @param data
     */
    function setFileData($file, data) {
        $file.find(".progress-bar").removeAttr("style");

        $file.find(".additional_info").html(data.fps + " fps");
        $file.find(".eta").html(data.eta);
        $file.find(".bitrate").html(data.bitrate + " kbits/s");
        $file.find(".status").html(data.progress + "% / " + data.size);

        setProgress($file, data.progress);
    }

    /**
     * set a new progress bar value for a given file
     * @param $file
     * @param value
     */
    function setProgress($file, value) {
        var $progressBar = $file.parent().find(".progress-bar");

        $progressBar.css("width", value + "%");
        $progressBar.find("span").html(value + "%");
    }

    /**
     * initially add a file whenever we receive the "file_started" event
     */
    socket.on("file_started", function (msg) {
        var $file = addFileToDOM(msg.data);
        setFileData($file, msg.data);
    });

    /**
     * update a file in the DOM whenever we receive the "file_progress" event
     */
    socket.on("file_progress", function (msg) {
        var $file = $overview.find("tr[data-file-id='" + msg.data.id + "']");

        setFileData($file, msg.data);
    });

    /**
     * remove a file whenever we receive the "file_done" event
     */
    socket.on("file_done", function (msg) {
        var $file = $overview.find("tr[data-file-id='" + msg.data.id + "']");

        if ($file.length != 0) {
            $file.fadeOut("slow", function () {
                $(this).remove();
            })
        }
    });

    /**
     * empty the file list whenever we connect to the server
     * TODO find a way not to do this when switching between pages
     */
    socket.on("disconnect", function(msg) {
        $overview.find("tbody > *").remove();
    })
});