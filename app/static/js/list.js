$(function () {
    var $body = $("body");
    var $confirmationModal = $("#confirm-modal");

    /*
     $.ajaxSetup({
     complete: function () {
     // initialize sortable after *every* AJAX request (delete of package, adding a new package, etc.)
     // init_sortable();
     // TODO
     }
     });
     */

    // package actions
    $body.on("click", ".package .heading .actions a", function (e) {
        e.preventDefault();
        e.stopPropagation();

        var which = $(this).attr("class");
        var $element = $(this);
        var $package = $element.parents(".package");

        var packageId = $package.data("package-id");
        $confirmationModal.data("package-id", packageId);

        switch (which) {
            case "delete":
                $confirmationModal.find(".text").addClass("hidden");
                $confirmationModal.find(".text[data-what='delete_package']").removeClass("hidden");
                $confirmationModal.modal("show");
                break;

            case "move":
                $.post("/list/move_package", {"package_id": packageId}).done(function (ignore) {
                    $package.slideUp("fast", function () {
                        $(this).remove();
                    });

                    notify("success", lang["moving_package_successful"]);
                });
                break;

            case "restart":
                $confirmationModal.find(".text").addClass("hidden");
                $confirmationModal.find(".text[data-what='restart_package']").removeClass("hidden");
                $confirmationModal.modal("show");
                break;
        }
    });

    // file actions
    $body.on("click", ".package .mainlist .actions a", function (e) {
        e.preventDefault();
        e.stopPropagation();

        var which = $(this).attr("class");

        var $element = $(this);
        var $package = $element.parents(".package");
        var $file = $element.parents("li.file");

        var packageId = $package.data("package-id");
        var fileId = $file.data("file-id");

        switch (which) {
            case "delete":
                if ($package.find(".file").length == 1) {
                    // delete whole package because only this file was left
                    $.post("/list/delete_package", {"package_id": packageId}).done(function () {
                        $package.slideUp("fast", function () {
                            $(this).remove();
                        });

                        notify("success", lang["deleting_package_successful"]);
                    });
                } else {
                    $.post("/list/delete_file", {"file_id": fileId}).done(function () {
                        $file.slideUp("fast", function () {
                            $(this).remove();
                        });
                    });
                }

                break;

            case "restart":
                $.post("/list/restart_file", {"file_id": fileId}).done(function () {
                    // reload list using AJAX
                    $(".container > .main").parent().load(window.location.href + " .main", function () {
                        // expand package
                        // $("#package" + packageId).collapse().collapse("show");
                        // does not work - wtf?
                        setTimeout(function () {
                            $("#package" + packageId).addClass("in");
                        }, 100);
                    }(packageId));
                });
                break;
        }
    });

    $confirmationModal.find("button[type='submit']").on("click", function (e) {
        e.preventDefault();

        $confirmationModal.modal("hide");

        var packageId = $confirmationModal.data("package-id");
        var $package = $(".package[data-package-id='" + packageId + "']");

        if (!$confirmationModal.find(".text[data-what='delete_package']").hasClass("hidden")) {
            // delete package
            $.post("/list/delete_package", {"package_id": packageId}).done(function () {
                $package.slideUp("fast", function () {
                    $(this).remove();
                });

                notify("success", lang["deleting_package_successful"]);
            });
        } else {
            // restart package
            $.post("/list/restart_package", {"package_id": packageId}).done(function () {
                // reload list using AJAX
                // .modal-backdrop doesn't get removed automatically?!?
                $(".modal-backdrop").remove();
                $(".container > .main").parent().load(window.location.href + " .main");
            });
        }

    });

    // sortable list
    // init_sortable();
});

function init_sortable() {
    $("#packages").sortable({
        forcePlaceholderSize: true,
        handle: ".trigger"
    }).on("sortupdate", sortupdate);

    $(".mainlist").sortable({
        forcePlaceholderSize: true,
        handle: ".trigger"
    }).on("sortupdate", sortupdate);
}

function sortupdate(ignore, ui) {
    // build new order array to store in DB
    // determine what type of item is being sorted

    var selector = [];
    // parent container selector
    selector["package"] = "#packages";
    selector["file"] = ".mainlist";

    var $item = ui.item;
    var which = $item.hasClass("file") ? "file" : "package";
    var packageId = which == "package" ? $item.attr("data-packageid") : $item.parent().parent().attr("data-packageid");

    var newOrder = [];
    $item.parents(selector[which]).find("li." + which).each(function (index, element) {
        newOrder.push(parseInt($(element).attr("data-" + which + "id")));
    });
    $.post("/package", {
        action: "new_position",
        which: which,
        packageId: packageId,
        new_order: JSON.stringify(newOrder)
    });
}