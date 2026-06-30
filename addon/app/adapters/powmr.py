import json
import subprocess


class PowMrLocalAdapter:
    def __init__(self, options):
        self.serial_port = options["serial_port"]
        self.protocol = options["protocol"]
        self.command = options["command"]

    def read_telemetry(self):
        cmd = [
            "mpp-solar",
            "-p",
            self.serial_port,
            "-P",
            self.protocol,
            "-c",
            self.command,
            "-o",
            "json",
        ]

        output = subprocess.check_output(cmd, text=True, timeout=25)
        return json.loads(output)