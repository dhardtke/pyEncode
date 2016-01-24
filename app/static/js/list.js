/*
$(function () {
    $.ajaxSetup({
        complete: function () {
            // initialize sortable after *every* AJAX request (delete of package, adding a new package, etc.)
            init_sortable();
        }
    });

    // package actions
    $("body").on("click", ".package .heading .actions a", function (e) {
        e.preventDefault();
        var which = $(this).attr("class");
        var $element = $(this);
        var $package = $element.parents(".package");
        var packageId = $package.attr("data-packageId");

        switch (which) {
            case "delete":
                $("#deletePackageModal").data("packageId", packageId).modal("show");
                break;

            case "move":
                $.post("/package", {"packageId": packageId, "action": "move"}).done(function (data) {
                    $package.slideUp("fast", function () {
                        $(this).remove();
                    });
                    notify("success", lang["moving_package_successful"]);
                });
                break;

            case "restart":
                $("#restartPackageModal").data("packageId", packageId).modal("show");
                break;
        }
        return false;
    });

    // file actions
    $("body").on("click", ".package .mainlist .actions a", function (e) {
        e.preventDefault();
        var which = $(this).attr("class");
        var $element = $(this);
        var $package = $element.parents(".package");
        var packageId = $package.attr("data-packageId");
        var $file = $element.parents("li.file");
        var fileId = $file.attr("data-fileId");

        switch (which) {
            case "delete":
                $.post("/file", {"fileId": fileId, "action": "delete"}).done(function (response) {
                    if ($package.find(".file").length == 1) {
                        // delete whole package because only this file was left
                        $package.slideUp("fast", function () {
                            $(this).remove();
                        });
                    } else {
                        $file.slideUp("fast", function () {
                            $(this).remove();
                        });
                    }
                });
                break;

            case "restart":
                $.post("/file", {"fileId": fileId, "action": "restart"}).done(function (data) {
                    // reload list using AJAX
                    $(".container > .main").parent().load(window.location.href, function () {
                        // expand package
                        // $("#package" + packageId).collapse().collapse("show");
                        // does not work - wtf?
                        setTimeout(function () {
                            $("#package" + packageId).addClass("in");
                        }, 50);
                    }(packageId));
                });
                break;
        }
    });

    $("body").on("click", "#deletePackageModal button[type=submit]", function (e) {
        e.preventDefault();
        $("#deletePackageModal").modal("hide");
        var packageId = $("#deletePackageModal").data("packageId");
        var $package = $(".package[data-packageid='" + packageId + "']");

        $.post("/package", {"packageId": packageId, "action": "delete"}).done(function (data) {
            $package.slideUp("fast", function () {
                $(this).remove();
            });
            notify("success", lang["deleting_package_successful"]);
        });
    });

    $("body").on("click", "#restartPackageModal button[type=submit]", function (e) {
        e.preventDefault();
        $("#restartPackageModal").modal("hide");
        var packageId = $("#restartPackageModal").data("packageId");

        $.post("/package", {"packageId": packageId, "action": "restart"}).done(function (data) {
            // reload list using AJAX
            $(".container > .main").parent().load(window.location.href);
        });
    });

    // sortable list
    init_sortable();
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

function sortupdate(e, ui) {
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
*/