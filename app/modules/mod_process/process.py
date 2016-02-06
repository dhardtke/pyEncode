# this class / module serves as a wrapper for the avconv process
import os
import re
from collections import deque
from threading import Thread

# see https://github.com/miguelgrinberg/Flask-SocketIO/issues/192
import subprocess
import math

# from eventlet.green.subprocess import Popen
from subprocess import Popen

from app import db
from app.modules.mod_process.process_repository import ProcessRepository
# from app.modules.mod_process.eventlet_helpers import read

config = {
    "encoding_acodec": "aac",
    "encoding_strict": "experimental",
    "encoding_s": "1280x720",
    "encoding_aspect": "1280:720",
    "encoding_preset": "slow",
    "encoding_crf": 22
}

# the pattern to fetch meta information of the current progress
AVCONV_PATTERN = re.compile(
    r"frame=\s*?([0-9]+)\s*?fps=\s*?([0-9]+)\s*?q=[0-9.]+\s*?size=\s*([0-9]+)kB\stime=([0-9.]+)\sbitrate=\s*?([0-9.]+)kbits/s")


class Process(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file

    def run(self):
        # probe file first
        frame_count = self.avconv_probe_frame_count()

        """
        ProcessRepository.file_progress(self.file, {})

        import sys
        sys.exit(0)
        """

        if frame_count == -1:
            # app.logger.debug("Probing of " + file.filename + " failed - aborting...")
            # file.status = statusMap["failed"]
            # file.process = None
            # db.session.delete(process)
            # db.session.commit()
            # sys.exit(1)
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

        for info in self.run_avconv(cmd, frame_count):
            if info["return_code"] != -1 and info["return_code"] != 0:
                # TODO nicht einfach auf failed setzen, sondern eine methode wie fail() callen
                # print("Error occured while running avconv. Check log for details")
                # app.logger.debug("Error occured while running avconv. Last five lines of output: ")
                # last_5 = "\n".join(total_output.splitlines()[-5:])
                # app.logger.debug(last_5)
                # quit(None, None)
                return  # TODO

            # @todo catch when process does no longer exists in DB, because user has been deleted

            # store information in database
            """
            self.file.eta = info["eta"]
            self.file.progress = info["progress"]
            self.file.bitrate = info["bitrate"]
            self.file.time = info["time"]
            self.file.size = info["size"]
            self.file.fps = info["fps"]
            db.session.commit()
            """
            # TODO is this necessary?
            # tell ProcessRepository there's some progress going on
            info["id"] = self.file.id  # TODO nicer way of doing this
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

        ProcessRepository.file_done(self.file)
        return

    def collect_parameters(self):
        cmd = []
        cmd.extend(["-i", self.file.filename])
        # cmd.extend(["-vcodec", "libx264"])
        cmd.extend(["-acodec", config["encoding_acodec"]])
        cmd.extend(["-strict", config["encoding_strict"]])
        cmd.extend(["-s", config["encoding_s"]])
        cmd.extend(["-aspect", config["encoding_aspect"]])
        cmd.extend(["-preset", config["encoding_preset"]])
        cmd.extend(["-crf", config["encoding_crf"]])
        # fix some files not being encodable
        cmd.extend(["-c:a", "copy"])

        # @todo add audio options and make them configurable
        cmd.extend(["-f", "matroska"])
        return cmd

    """
        probe self.file and return frame count
    """

    def avconv_probe_frame_count(self):
        instance = Popen(["avprobe", self.file.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
        output = "\n".join(instance.communicate())

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
        pass

    def run_avconv(self, cmd, frame_count):
        instance = Popen(map(str, cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

        # set avconv_pid
        self.file.avconv_pid = instance.pid
        db.session.commit()

        # these two variables are just needed for when the processing fails, see below
        last_lines = deque(maxlen=5)  # parameter determines how many lines to keep

        # oddly avconv writes to stderr instead of stdout
        for line in instance.stderr:
            # append current line to last_lines
            last_lines.append(line)

            match = AVCONV_PATTERN.match(line)

            # first few lines have no match
            if not match:
                continue

            frame = int(match.group(1))  # current frame, needed for calculation of progress
            fps = int(match.group(2))  # needed for calculation of remaining time
            size = int(match.group(3))  # current size in kB
            time = float(match.group(4))  # time already passed for converting, in seconds
            bitrate = float(match.group(5))  # in kbits/s
            progress = round((frame / float(frame_count)) * 100, 1)  # in %

            frames_remaining = frame_count - frame  # needed for eta
            eta = frames_remaining / fps if fps != 0 else -1  # in seconds

            yield {"return_code": -1, "eta": eta, "progress": progress, "bitrate": bitrate, "time": time, "size": size,
                   "fps": fps}

        return_code = instance.wait()
        if return_code != 0:
            yield {"return_code": return_code, "last_lines": last_lines}

    def stop_avconv(self):
        pass
