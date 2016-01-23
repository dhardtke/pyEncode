$(function () {
    var $toggleBtn = $("#toggle-status-btn");
    var $countActive = $("#count-processes-active");
    var $countTotal = $("#count-processes-total");

    socket.on("active_changed", function (msg) {
        // TODO change status
        $toggleBtn.removeClass("btn-success btn-danger");
        $toggleBtn.find("span").addClass("hidden");

        if (msg.active) {
            $toggleBtn.addClass("btn-success");
            $toggleBtn.find("span[data-which='1']").removeClass("hidden");
        } else {
            $toggleBtn.addClass("btn-danger");
            $toggleBtn.find("span[data-which='0']").removeClass("hidden");
        }
    });

    // TODO file_added event
    // TODO file_deleted event

    socket.on("file_done", function (msg) {
        $countActive.html(msg.data.count_active);
    });

    socket.on("file_started", function (msg) {
        $countActive.html(msg.data.count_active);
    });

    $toggleBtn.on("click", function (e) {
        e.preventDefault();

        $.post("/toggle");
    });
});