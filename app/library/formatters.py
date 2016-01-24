import os


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


def formatted_file_data(file):
    return {
        "id": file.id,
        "progress": file.avconv_progress,
        "filename": os.path.basename(file.filename),  # show only filename, without path
        "bitrate": file.avconv_bitrate,
        "fps": file.avconv_fps,
        "size": human_size(file.size * 1024),  # in kB, calculate bytes and format via human_size() method
        "time": human_time(file.avconv_time),
        "eta": human_time(file.avconv_eta)
    }


def filename_description(filename):
    allowed_extensions = {
        "mkv": "Matroska-Video",
        "mp4": "MPEG-4",
        "wmv": "Windows Media Video",
        "mov": "Quicktime Movie",
        "m2ts": "BDAV Video File",
        "f4v": "Flash Video"
    }

    extension = os.path.splitext(filename)[1][1:]

    if extension not in allowed_extensions:
        raise KeyError("File has unknown extension: %s" % filename)

    return allowed_extensions[extension] + " " + "(." + extension + ")"
