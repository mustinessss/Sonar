import re
import queue
import threading
import serial


class SerialReader:
    LINE_RE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d+\s*->\s*")

    def __init__(self, port: str, baud: int, out: queue.Queue):
        self._out   = out
        self._stop  = threading.Event()
        self._ser   = serial.Serial(port, baud, timeout=1)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def close(self):
        self._stop.set()
        try:
            self._ser.close()
        except Exception:
            pass

    def _run(self):
        while not self._stop.is_set():
            try:
                raw = self._ser.readline()
            except Exception:
                break

            try:
                line = raw.decode("utf-8", errors="ignore").strip()
            except Exception:
                continue

            line  = self.LINE_RE.sub("", line)
            parts = line.split()
            if len(parts) < 3:
                continue

            try:
                dist  = float(parts[0])
                angle = float(parts[2])
            except ValueError:
                continue

            self._out.put((angle, dist))
