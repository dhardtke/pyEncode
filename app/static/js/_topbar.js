$.ajaxSetup({
    cache: true,
    beforeSend: function () {
        topbar.show();
    },
    complete: function () {
        topbar.hide();
    }
});