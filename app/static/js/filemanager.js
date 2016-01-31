var resolutionRequests = [];

$(function () {
    var $body = $("body");

    $body.on("click", "#filemanager a.add_file", function (e) {
        e.preventDefault();

        var path = $(this).data("filepath");

        if (!window.opener) {
            notify("error", lang["unknown_error_occured"]);
            return;
        }

        if (add_file(path)) {
            notify("success", lang["file_has_been_added_successfully"]);
        }
    });

    /**
     * AJAX load a path when clicking on name
     */
    $body.on("click", ".ajax_path", function (e) {
        e.preventDefault();

        var path = $(this).attr("href");

        // remove filter when changing folders
        $("#filter").val("");

        load(encodeURI(path));
    });

    $body.tooltip({
        selector: "a[title]",
        placement: "left"
    });

    $body.on("keydown", "#filter", function (e) {
        if (e.which == 13) {
            load(currentPath);
            setTimeout(function () {
                $("#filter").blur().focus();
            }, 150);
        }
    });

    $body.on("click", "#filterBtn", function (e) {
        load(currentPath);
    });

    $body.on("keydown", "#jumpbox", function (e) {
        if (e.which == 13) {
            _load_jumpbox();
        }
    });

    $body.on("click", "#jumpboxBtn", function (e) {
        _load_jumpbox();
    });

    _load_resolutions();
});

function add_file(path) {
    var list = window.opener.$("#filenames");
    var filename = path.split("/").pop();

    if (list.find("li:contains('" + path + "')").length != 0) {
        notify("warning", "'" + filename + "'<br />" + lang["is_already_in_list"]);
        return false;
    }

    var listItem;
    listItem = "<li>";
    listItem += "<span style='display: none;' class='fullpath'>" + path + "</span>";
    listItem += "<span class='filename' style='display: block;'>" + filename + "</span>";
    listItem += "<a href='javascript:;' class='btn btn-xs btn-danger remove-btn' title='" + lang["remove_from_list"] + "'>";
    listItem += "<i class='fa fa-trash-o'></i>";
    listItem += "</a>";
    listItem += "</li>";
    list.append(listItem);

    return true;
}

function load(path) {
    // abort every (currently running) resolution request first
    for (var i in resolutionRequests) {
        resolutionRequests[i].abort();
    }

    resolutionRequests = [];

    $(".container").load(path + " .container > .main", {"filter": $("#filter").val()}, function (response, status, xhr) {
        if (status == "error") {
            notify("error", lang["cant_open_folder"]);
        } else {
            $("#jumpbox").val("");

            // update URL bar
            history.replaceState({}, "", path);

            // set currentPath (see base.html)
            currentPath = path;
            // sort table after AJAX
            // Sortable.init();
            // TODO

            // begin loading resolutions
            _load_resolutions();
        }
    });
}

function _load_jumpbox() {
    var path = $("#jumpbox").val();
    // is an absolute path
    if (path == "") {
    } else if (path.charAt(0) == "/") {
        load("/filemanager" + path);
    } else {
        // append current path
        load(currentPath + (currentPath != "/filemanager/" ? "/" : "") + path);
    }
}

function _select_all() {
    var checkbox;
    $("#filemanager").find("tbody tr").each(function (key, element) {
        checkbox = $(element).find("td:last > input:not([disabled='disabled'])");
        checkbox.prop("checked", true);
    });
}

function _select_none() {
    var checkbox;
    $("#filemanager").find("tbody tr").each(function (key, element) {
        checkbox = $(element).find("td:last > input:not([disabled='disabled'])");
        checkbox.prop("checked", false);
    });
}

function _load_resolutions() {
    var $filemanager = $("#filemanager");

    // don't load resolutions when no column exists (i.e. resolutions are disabled in config
    if ($filemanager.find(".resolution").length == 0) {
        return;
    }

    $filemanager.find("tbody tr").each(function (i, element) {
        var path = $(element).find("a").data("filepath");
        if (!path) {
            return true; // i.e. continue
        }
        var $resolution = $(element).find(".resolution");

        resolutionRequests.push($.post("/filemanager/resolution", {path: window.encodeURIComponent(unescape(path))}).done(function (response) {
            $resolution.html(response["human"]).attr("data-value", response["raw"]);
        }));
    });

    // when all requests are done
    $.when.apply($, resolutionRequests).then(function () {
        // allow sorting by resolution
        // $("#filemanager th")[0].removeEventListener("click", Sortable.setupClickableTH); // remove all event handlers

        // $("#filemanager").removeAttr("data-sortable-initialized").find("thead .resolution_head").removeAttr("data-sortable");
        // initialize *again*
        // $("#filemanager").attr("data-sortable", "true");
        // Sortable.init();
        // alert("blablub?");

        // Sortable.destroy();
    });
}

function add_multiple() {
    if (!window.opener) {
        notify("error", lang["unknown_error_occured"]);
        return;
    }

    var checkbox;

    $("#filemanager").find("tbody tr").each(function (key, element) {
        var $checkbox = $(element).find("td:last > input");
        if ($checkbox.is(":disabled")) {
            return true;
        }
        var checked = $checkbox.is(":checked");
        $checkbox.prop("checked", false);

        // skip not checked files
        if (!checked) {
            return true;
        }

        add_file($(element).find("a").attr("data-filepath"));
    });

    notify("success", lang["files_were_added_successfully"]);
}

function removeFile(element) {
    $(element).parent().fadeOut("fast", function () {
        this.remove()
    });
}

window.onpopstate = function (e) {
    var url = document.location.href;
    var path = url.substr(url.indexOf("/filemanager/"));
    load(path);
};