function notify(msg_type, message) {
    var icon = "fa fa-fw ", type;

    switch (msg_type) {
        case "error":
            icon += "fa-times-circle";
            type = "danger";
            break;

        case "success":
            icon += "fa-smile-o";
            type = "success";
            break;

        case "warning":
            icon += "fa-exclamation-triangle";
            type = "warning";
            break;

        /*
         case "info":
         icon += "fa-info-circle";
         type = "info";
         break;
         */
    }

    $.notify({
            title: "<strong>" + lang[msg_type] + "</strong> ", // not all are defined for all types, @todo
            message: message,
            icon: icon
        },
        {
            // delay: 0,
            type: type,
            z_index: 10000
        }
    );
}