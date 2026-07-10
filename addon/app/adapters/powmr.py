import json
import subprocess
import threading


class PowMrLocalAdapter:
    def __init__(self, options):
        self.serial_port = options["serial_port"]
        self.protocol = options["protocol"]
        self.command = options["command"]

        # Only one mpp-solar process may use the serial port at a time.
        self._serial_lock = threading.Lock()

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

        with self._serial_lock:
            output = subprocess.check_output(
                cmd,
                text=True,
                timeout=25,
            )

        return json.loads(output)

    def read_telemetry(self):
        return self._run_command(self.command)

    def read_warnings(self):
        return self._run_command("QPIWS")

    def read_settings(self):
        return self._run_command("QPIRI")

    def set_output_source_priority(self, command):
        result = self._run_command(command)
        return result.get("pop") == "ACK"

    def set_charger_source_priority(self, command):
        result = self._run_command(command)
        return result.get("pcp") == "ACK"