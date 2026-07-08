import json
import subprocess


class PowMrLocalAdapter:
    def __init__(self, options):
        self.serial_port = options["serial_port"]
        self.protocol = options["protocol"]
        self.command = options["command"]

    def _run_command(self, command):
        cmd = [
            "mpp-solar",
            "-p",
            self.serial_port,
            "-P",
            self.protocol,
            "-c",
            command,
            "-o",
            "json",
        ]

        output = subprocess.check_output(cmd, text=True, timeout=25)
        return json.loads(output)

    def read_telemetry(self):
        return self._run_command(self.command)

    def read_warnings(self):
        return self._run_command("QPIWS")