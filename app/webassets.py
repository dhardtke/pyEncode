from flask_assets import Bundle

CSS_FILTERS = tuple(["cssmin", "cssrewrite"])
SCSS_FILTERS = CSS_FILTERS + tuple(["scss"])
JS_FILTERS = tuple(["jsmin"])

base_css = Bundle(
    "css/bootstrap.scss",
    "css/style.css",
    Bundle("bower_components/fontawesome/css/font-awesome.min.css"),
    "css/notify-animation.css",

    filters=SCSS_FILTERS,
    output="packed_base.css"
)

base_js = Bundle(
    Bundle(
        "bower_components/jquery/dist/jquery.min.js",
        "bower_components/bootstrap-sass/assets/javascripts/bootstrap.min.js",
        "bower_components/remarkable-bootstrap-notify/dist/bootstrap-notify.min.js",
        "bower_components/topbar/topbar.min.js"
    ),
    "bower_components/sio-client/socket.io.js",
    "js/_socket.js",
    "js/_notify.js",
    "js/_topbar.js",

    filters=JS_FILTERS,
    output="packed_base.js"
)

_statusbar_js = Bundle(
    "js/_statusbar.js",

    filters=JS_FILTERS
)

index_js = Bundle(
    base_js,
    _statusbar_js,
    "js/index.js",

    filters=JS_FILTERS,
    output="packed_overview.js"
)

index_css = Bundle(
    base_css,
    "css/index.css",

    filters=CSS_FILTERS,
    output="packed_index.css"
)

list_js = Bundle(
    base_js,
    _statusbar_js,
    "js/list.js",
    Bundle("bower_components/html.sortable/dist/html.sortable.min.js"),

    filters=JS_FILTERS,
    output="packed_list.js"
)

list_css = Bundle(
    base_css,
    "css/list.css",

    filters=CSS_FILTERS,
    output="packed_list.css"
)

filemanager_js = Bundle(
    base_js,
    # Bundle("bower_components/sortable/js/sortable.min.js")
    "js/filemanager.js",

    filters=JS_FILTERS,
    output="packed_filemanager.js"
)

filemanager_css = Bundle(
    base_css,
    "css/filemanager.css",
    # "bower_components/sortable/css/sortable-theme-bootstrap.css",

    filters=CSS_FILTERS,
    output="packed_filemanager.css"
)

log_css = Bundle(
    base_css,
    "css/log.css",

    filters=CSS_FILTERS,
    output="packed_log.css"
)
