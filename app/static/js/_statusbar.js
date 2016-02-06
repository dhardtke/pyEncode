$(function () {
    var $toggleBtn = $("#toggle-status-btn");
    var $countActive = $("#count-processes-active");
    var $countQueued = $("#count-processes-queued");
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
        console.log(msg);
        /*
         $countActive.html(msg.data.count_active);
         $countQueued.html(msg.data.count_queued);
         $countTotal.html(msg.data.count_total);
         */
    });

    socket.on("file_started", function (msg) {
        $countActive.html(msg.data.count_active);
        $countQueued.html(msg.data.count_queued);
    });

    $toggleBtn.on("click", function (e) {
        e.preventDefault();

        $.post("/statusbar/toggle");
    });

    var $addPackageModal = $("#add-package-modal");
    var $addPackageForm = $addPackageModal.find("form");
    var $filenames = $("#filenames");

    $("#add-package-btn").on("click", function (e) {
        e.preventDefault();

        $addPackageModal.modal("show");
    });

    $addPackageModal.on("hidden.bs.modal", function (e) {
        $addPackageForm[0].reset();
        $filenames.html(""); // empty file list
    });

    $("body").on("click", ".remove-btn", function(e) {
        $(this).parent().fadeOut("fast", function () {
            this.remove()
        });
    });

    $addPackageForm.on("submit", function (e) {
        e.preventDefault();

        var title = $("#title").val();
        var paths = [];

        $filenames.find("> li span.fullpath").each(function (key, element) {
            paths.push($(element).html());
        });

        if (title == "" || paths.length == 0) {
            notify("error", lang["not_all_fields_filled"]);
            return;
        }

        $.ajax({
            url: "/statusbar/add",
            method: "post",
            data: {
                "title": title,
                "paths": JSON.stringify(paths),
                "queue": ($("#target_queue").prop("checked") ? 1 : 0)
            },
            success: function (data) {
                switch (data) {
                    case "1":
                        notify("success", lang["package_added_successfully"]);
                        $addPackageModal.modal("hide");

                        if (window.location.href.indexOf("/list/") != -1) {
                            // this is some list page, reload list using AJAX
                            $(".container > .main").parent().load(window.location.href);
                        }
                        break;

                    case "not_existing":
                        notify("error", lang["at_least_one_file_not_existing"]);
                        break;

                    case "already_in_list":
                        notify("error", lang["duplicate_file_error"]);
                        break;
                }
            }
        });

        e.stopImmediatePropagation();
    });

    // open filemanager when clicking on browse-btn
    $("#browse-btn").on("click", function (e) {
        e.preventDefault();

        // @todo width and height calculations
        window.screenTop = 400;
        var width = window.innerWidth / 2;
        var fileManager = PopupCenter("/filemanager", "Filemanager", width, 400);
    });
});

function PopupCenter(url, title, w, h) {
    // Fixes dual-screen position                         Most browsers      Firefox
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;

    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;
    var newWindow = window.open(url, title, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

    // Puts focus on the newWindow
    if (window.focus) {
        newWindow.focus();
    }
    return newWindow;
}