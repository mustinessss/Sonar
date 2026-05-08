import sys
import queue
import tkinter as tk
from tkinter import messagebox

try:
    import serial.tools.list_ports
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Ошибка", "Установите pyserial:\n\npip install pyserial")
    sys.exit(1)

from config import BAUD_RATE, MAX_DIST, FPS, BG, GREEN_DIM, GREEN_MID, GREEN_ON
from serial_reader import SerialReader
from radar_canvas import RadarCanvas


class RadarApp:
    def __init__(self, root: tk.Tk):
        self.root    = root
        self._reader: SerialReader | None = None
        self._queue: queue.Queue = queue.Queue()

        root.title("Sonar Radar")
        root.configure(bg=BG)
        root.resizable(True, True)
        root.geometry("720x580")
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._tick()

    def _build_ui(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=10, pady=6)

        tk.Label(top, text="Порт:", bg=BG, fg=GREEN_ON,
                 font=("Consolas", 11)).pack(side="left")

        self._port_var = tk.StringVar()
        self._port_menu = tk.OptionMenu(top, self._port_var, "")
        self._port_menu.config(bg=GREEN_DIM, fg=GREEN_ON,
                               activebackground="#004400",
                               activeforeground=GREEN_ON,
                               font=("Consolas", 11), relief="flat",
                               highlightthickness=0)
        self._port_menu["menu"].config(bg=GREEN_DIM, fg=GREEN_ON,
                                       activebackground="#004400",
                                       activeforeground=GREEN_ON)
        self._port_menu.pack(side="left", padx=(4, 8))

        self._btn = tk.Button(top, text="Подключить",
                              command=self._toggle_connect,
                              bg=GREEN_DIM, fg=GREEN_ON,
                              activebackground="#004400",
                              activeforeground=GREEN_ON,
                              font=("Consolas", 11), relief="flat", padx=8)
        self._btn.pack(side="left")

        tk.Button(top, text="⟳", command=self._refresh_ports,
                  bg=BG, fg=GREEN_ON, activebackground=GREEN_DIM,
                  activeforeground=GREEN_ON,
                  font=("Consolas", 13), relief="flat",
                  padx=4).pack(side="left", padx=4)

        self._status_var = tk.StringVar(value="Не подключено")
        tk.Label(top, textvariable=self._status_var,
                 bg=BG, fg=GREEN_MID,
                 font=("Consolas", 10)).pack(side="right", padx=6)

        info = tk.Frame(self.root, bg=BG)
        info.pack(fill="x", padx=16, pady=(0, 4))

        self._dist_var  = tk.StringVar(value="Дистанция: —")
        self._angle_var = tk.StringVar(value="Угол: —")
        for var in (self._dist_var, self._angle_var):
            tk.Label(info, textvariable=var, bg=BG, fg=GREEN_ON,
                     font=("Consolas", 12)).pack(side="left", padx=12)

        self._radar = RadarCanvas(self.root)
        self._refresh_ports()

    def _refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        menu  = self._port_menu["menu"]
        menu.delete(0, "end")
        for p in ports:
            menu.add_command(label=p,
                             command=lambda v=p: self._port_var.set(v))
        self._port_var.set(ports[0] if ports else "")

    def _toggle_connect(self):
        if self._reader is not None:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        port = self._port_var.get()
        if not port:
            messagebox.showwarning("Внимание", "Выберите COM-порт")
            return
        try:
            self._reader = SerialReader(port, BAUD_RATE, self._queue)
            self._btn.config(text="Отключить", bg="#330000")
            self._status_var.set(f"Подключено: {port}")
        except Exception as exc:
            messagebox.showerror("Ошибка подключения", str(exc))

    def _disconnect(self):
        if self._reader:
            self._reader.close()
            self._reader = None
        self._btn.config(text="Подключить", bg=GREEN_DIM)
        self._status_var.set("Отключено")

    def _tick(self):
        last_angle: float | None = None
        last_dist:  float | None = None

        try:
            while True:
                angle, dist = self._queue.get_nowait()
                last_angle  = angle
                last_dist   = dist
                self._radar.update_sweep(angle, dist)
        except queue.Empty:
            pass

        if last_angle is not None:
            self._angle_var.set(f"Угол: {last_angle:.0f}°")
        if last_dist is not None:
            d = f"{last_dist:.1f}" if 0 < last_dist < MAX_DIST else "вне диапазона"
            self._dist_var.set(f"Дистанция: {d}")

        self._radar.redraw()
        self.root.after(1000 // FPS, self._tick)

    def _on_close(self):
        self._disconnect()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    RadarApp(root)
    root.mainloop()
