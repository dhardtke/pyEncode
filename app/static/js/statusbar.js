// this defines how often the status bar gets updated (in ms)
const REFRESH_INTERVAL = 5000;

$(function () {
    // handle answer to "status" event
    socket.on("status", function (msg) {
        console.log(msg.data);
    });

    // request "status" event every REFRESH_INTERVAL milliseconds
    setInterval(function() {
        socket.emit("status", {})
    }, REFRESH_INTERVAL);
});