def human_size(num):
    for x in ["bytes", "KiB", "MiB", "GiB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, "TiB")


def human_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    formatted = "%d:%02d:%02d" % (h, m, s)
    return formatted