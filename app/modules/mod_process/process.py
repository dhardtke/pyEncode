# this class / module serves as a wrapper for the avconv process
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
from app.models.file import File
from app.modules.mod_process.process_repository import ProcessRepository

# we need to monkey patch the threading module, see http://eventlet.net/doc/patching.html
eventlet.monkey_patch(thread=True)

# the pattern to fetch meta information of the current progress
AVCONV_PATTERN = re.compile(
    r"frame=\s*?([0-9]+)\s*?fps=\s*?([0-9]+)\s*?q=[0-9.]+\s*?size=\s*([0-9]+)kB\stime=([0-9.]+)\sbitrate=\s*?([0-9.]+)kbits/s")


class Process(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file
        self.active = True

    def run(self):
        # probe file first
        frame_count = self.avconv_probe_frame_count()

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

        cmd = ["avconv"]
        cmd += self.collect_parameters()
        cmd.extend(["-y", path + "/" + temp_filename])

        # app.logger.debug("Starting encoding of " + str(file.filename) + " with " + " ".join(map(str, cmd)))

        for info in Process.run_avconv(cmd, frame_count):
            # return if Thread has been marked as inactive
            if not self.active:
                return

            if info["return_code"] != -1:
                # app.logger.debug("Error occured while running avconv. Last five lines of output: ")
                # last_5 = "\n".join(total_output.splitlines()[-5:])
                # app.logger.debug(last_5)
                # print(info["last_lines"])
                ProcessRepository.file_failed(self.file)
                return

            # store information in database
            File.query.filter_by(id=self.file.id).update(
                dict(avconv_eta=info["eta"], avconv_progress=info["progress"], avconv_bitrate=info["bitrate"],
                     avconv_time=info["time"], avconv_size=info["size"], avconv_fps=info["fps"]))
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

    def avconv_probe_frame_count(self):
        instance = Popen(["avprobe", self.file.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # TODO shorter code pls
        output = ""
        for line in instance.stderr:
            output += line.decode("utf8")

            # call sleep, see https://stackoverflow.com/questions/34599578/using-popen-in-a-thread-blocks-every-incoming-flask-socketio-request
            eventlet.sleep()

        # TODO logging
        # app.logger.debug("Probing with avprobe \"" + file.filename + "\"")

        fps_reg = re.findall(r"([0-9]*\.?[0-9]+) fps|tbr", output)
        if fps_reg is None:
            return -1

        fps = float(" ".join(fps_reg))

        duration = re.findall(r"Duration: (.*?),", output)[0]
        hrs, mins, secs, hsecs = list(map(int, re.split(r"[:.]", duration)))

        # calculate the amount of frames for the calculation of progress
        frame_count = int(math.ceil((hrs * 3600 + mins * 60 + secs + hsecs / 1000) * float(fps)))

        return frame_count

    def stop(self):
        self.active = False
        return

    @staticmethod
    def run_avconv(cmd, frame_count):
        instance = Popen(map(str, cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reader = io.TextIOWrapper(instance.stderr, encoding="utf8")

        # these two variables are just needed for when the processing fails, see below
        last_lines = deque(maxlen=5)  # parameter determines how many lines to keep

        # oddly avconv writes to stderr instead of stdout
        for line in reader:
            # call sleep, see https://stackoverflow.com/questions/34599578/using-popen-in-a-thread-blocks-every-incoming-flask-socketio-request
            eventlet.sleep()

            # append current line to last_lines
            last_lines.append(line)

            match = AVCONV_PATTERN.match(line)

            # first few lines have no match
            if match:
                frame = int(match.group(1))  # current frame, needed for calculation of progress
                fps = int(match.group(2))  # needed for calculation of remaining time
                size = int(match.group(3))  # current size in kB
                time = float(match.group(4))  # time already passed for converting, in seconds
                bitrate = float(match.group(5))  # in kbits/s
                progress = round((frame / float(frame_count)) * 100, 1)  # in %

                frames_remaining = frame_count - frame  # needed for eta
                eta = frames_remaining / fps if fps != 0 else -1  # in seconds

                yield {"return_code": -1, "eta": eta, "progress": progress, "bitrate": bitrate, "time": time,
                       "size": size, "fps": fps}

        return_code = instance.wait()
        if return_code != 0:
            yield {"return_code": return_code, "last_lines": last_lines}

    def stop_avconv(self):
        pass
