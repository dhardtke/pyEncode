# this class / module serves as a wrapper for the ffmpeg process
import io
import math
import os
import re
import subprocess
from collections import deque
from threading import Thread

import eventlet
from eventlet.green.subprocess import Popen

from app import db, config
from app.library.formatters import duration_to_seconds
from app.models.file import File
from app.modules.mod_process.process_repository import ProcessRepository

# we need to monkey patch the threading module, see http://eventlet.net/doc/patching.html
eventlet.monkey_patch(thread=True)

# the pattern to fetch meta information of the current progress
# frame=44448 fps= 14 q=-0.0 Lsize=  247192kB time=00:30:53.95 bitrate=1092.3kbits/s speed=0.577x
# TODO
# frame=  198 fps= 52 q=28.0 size=    1143kB time=00:00:06.92 bitrate=1353.6kbits/s speed=1.82x
PROGRESS_PATTERN = re.compile(
    r"frame=\s*?(\d+) fps=\s*?(\d+) q=(\-?[0-9.]+) L?size=\s*?(\d+)kB time=(.*) bitrate=([\d.]+)kbits/s speed=(\d.+)x")


class Process(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file
        self.active = True

    def run(self):
        # probe file first
        frame_count = self.ffmpeg_probe_frame_count()

        if frame_count == -1:
            # app.logger.debug("Probing of " + file.filename + " failed - aborting...")
            ProcessRepository.file_failed(self.file)
            return

        # app.logger.debug("Probing of " + file.filename + " successful.. frame count: " + str(frame_count))
        split_path = os.path.split(self.file.filename)
        path = split_path[0]
        original_filename = split_path[1]
        filename_noext = os.path.split(os.path.splitext(original_filename)[0])[1]
        temp_filename = filename_noext + ".tmp"

        cmd = ["ffmpeg"]
        cmd += self.collect_parameters()
        cmd.extend(["-y", path + "/" + temp_filename])

        # app.logger.debug("Starting encoding of " + str(file.filename) + " with " + " ".join(map(str, cmd)))

        for info in self.run_ffmpeg(cmd, frame_count):
            if info["return_code"] != -1:
                # app.logger.debug("Error occured while running ffmpeg. Last five lines of output: ")
                # last_5 = "\n".join(total_output.splitlines()[-5:])
                # app.logger.debug(last_5)
                # print(info["last_lines"])
                ProcessRepository.file_failed(self.file)
                return

            # store information in database
            File.query.filter_by(id=self.file.id).update(
                dict(ffmpeg_eta=info["eta"], ffmpeg_progress=info["progress"], ffmpeg_bitrate=info["bitrate"],
                     ffmpeg_time=info["time"], ffmpeg_size=info["size"], ffmpeg_fps=info["fps"]))
            db.session.commit()

            # tell ProcessRepository there's some progress going on
            ProcessRepository.file_progress(self.file, info)

        # TODO
        # remove original file from disk
        # print("os.remove(" + file.filename + ")")
        # os.remove(file.filename)
        # form new filename by replacing current resolution substring with the new resolution substring
        # print("filename_noext = " + re.sub(r"(\d+p)", "720p", filename_noext))
        # filename_noext = re.sub(r"(\d+p)", "720p", filename_noext)
        # @todo auch das einstellbar machen, immerhin kann man ja auch ohne Resizen vorgehen

        # full_path = path + "/" + filename_noext + "-selfmade" + ".mkv"
        # print("os.rename(" + path + "/" + temp_filename + ", " + full_path + ")")
        # os.rename(path + "/" + temp_filename, full_path)
        # @todo beim umbenennen die Erweiterung erkennen, abhängig von der Ausgabeformatseinstellung
        # @todo option für umbennen, z.B. -selfmade-Anhängung änderbar machen

        if self.active:
            ProcessRepository.file_done(self.file)
        return

    def collect_parameters(self):
        cmd = []
        cmd.extend(["-i", self.file.filename])
        # cmd.extend(["-vcodec", "libx264"])
        cmd.extend(["-acodec", config["encoding"]["acodec"]])
        cmd.extend(["-strict", config["encoding"]["strict"]])
        cmd.extend(["-s", config["encoding"]["s"]])
        cmd.extend(["-aspect", config["encoding"]["aspect"]])
        cmd.extend(["-preset", config["encoding"]["preset"]])
        cmd.extend(["-crf", config["encoding"]["crf"]])
        # fix some files not being encodable
        cmd.extend(["-c:a", "copy"])

        # @todo add audio options and make them configurable
        cmd.extend(["-f", "matroska"])
        return cmd

    """
        probe self.file and return frame count
    """

    def ffmpeg_probe_frame_count(self):
        instance = Popen(["ffprobe", self.file.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output = ""
        for line in instance.stderr:
            output += line.decode("utf8")

            # call sleep, see https://stackoverflow.com/questions/34599578/using-popen-in-a-thread-blocks-every-incoming-flask-socketio-request
            eventlet.sleep()

        # TODO logging
        # app.logger.debug("Probing with ffprobe \"" + file.filename + "\"")

        fps_reg = re.findall(r"([0-9]*\.?[0-9]+) fps|tbr", output)
        if fps_reg is None:
            return -1

        fps = float(" ".join(fps_reg))

        duration = duration_to_seconds(re.findall(r"Duration: (.*?),", output)[0])

        # calculate the amount of frames for the calculation of progress
        frame_count = int(math.ceil(duration * float(fps)))

        return frame_count

    def stop(self):
        self.active = False
        return

    def run_ffmpeg(self, cmd, frame_count):
        instance = Popen(map(str, cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reader = io.TextIOWrapper(instance.stderr, encoding="utf8")

        # these two variables are just needed for when the processing fails, see below
        last_lines = deque(maxlen=5)  # parameter determines how many lines to keep

        # oddly ffmpeg writes to stderr instead of stdout
        for line in reader:
            # kill ffmpeg when not being active anymore
            if not self.active:
                instance.kill()

            # call sleep, see https://stackoverflow.com/questions/34599578/using-popen-in-a-thread-blocks-every-incoming-flask-socketio-request
            eventlet.sleep()

            # append current line to last_lines
            last_lines.append(line)

            match = PROGRESS_PATTERN.match(line)

            # first few lines have no match
            if match:
                frame = int(match.group(1))  # current frame, needed for calculation of progress
                fps = int(match.group(2))  # needed for calculation of remaining time
                size = int(match.group(4))  # current size in kB
                time = duration_to_seconds(match.group(5))  # time already passed for converting, in seconds
                bitrate = float(match.group(6))  # in kbits/s
                progress = round((frame / float(frame_count)) * 100, 1)  # in %

                frames_remaining = frame_count - frame  # needed for eta
                eta = frames_remaining / fps if fps != 0 else -1  # in seconds

                yield {"return_code": -1, "eta": eta, "progress": progress, "bitrate": bitrate, "time": time,
                       "size": size, "fps": fps}

        return_code = instance.wait()
        if return_code != 0:
            yield {"return_code": return_code, "last_lines": last_lines}
