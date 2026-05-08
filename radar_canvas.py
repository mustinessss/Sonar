import math
import tkinter as tk
from config import (MAX_DIST, SWEEP_DEG, TRAIL_STEPS,
                    BG, GREEN_DIM, GREEN_MID, GREEN_ON, GREEN_BRT)


def _angle_to_rad(deg: float) -> float:
    return math.radians(180.0 - deg * 180.0 / SWEEP_DEG)


def _polar_to_xy(cx: float, cy: float, r: float,
                 deg: float, dist: float) -> tuple[float, float]:
    ratio = max(0.0, min(dist / MAX_DIST, 1.0))
    rad   = _angle_to_rad(deg)
    return cx + r * ratio * math.cos(rad), cy - r * ratio * math.sin(rad)


class RadarCanvas:
    RINGS = 5

    def __init__(self, parent: tk.Widget):
        self.widget = tk.Canvas(parent, bg=BG, highlightthickness=0)
        self.widget.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self._points: list[list] = []
        self._sweep = 0.0

    def update_sweep(self, angle: float, dist: float | None):
        self._sweep = angle
        if dist is not None and 0 < dist < MAX_DIST:
            self._points.append([angle, dist, TRAIL_STEPS])

    def redraw(self):
        cv = self.widget
        cv.delete("all")

        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 30 or h < 30:
            return

        cx = w // 2
        cy = int(h * 0.92)
        r  = min(cx - 25, cy - 15)
        if r < 10:
            return

        self._draw_grid(cv, cx, cy, r)
        self._draw_points(cv, cx, cy, r)
        self._draw_sweep(cv, cx, cy, r)
        self._draw_base(cv, cx, cy, r)

    def _draw_grid(self, cv: tk.Canvas, cx: int, cy: int, r: int):
        for i in range(1, self.RINGS + 1):
            rr = int(r * i / self.RINGS)
            cv.create_arc(cx - rr, cy - rr, cx + rr, cy + rr,
                          start=0, extent=180,
                          outline=GREEN_DIM, style="arc", width=1)
            label = MAX_DIST * i / self.RINGS
            cv.create_text(cx + 4, cy - rr + 2,
                           text=f"{label:.0f}",
                           fill=GREEN_MID, font=("Consolas", 8), anchor="w")

        for deg in range(0, SWEEP_DEG + 1, 10):
            rad = _angle_to_rad(deg)
            x2  = cx + r * math.cos(rad)
            y2  = cy - r * math.sin(rad)
            cv.create_line(cx, cy, x2, y2, fill=GREEN_DIM, width=1)
            if deg % 20 == 0:
                lx = cx + (r + 14) * math.cos(rad)
                ly = cy - (r + 14) * math.sin(rad)
                cv.create_text(lx, ly, text=f"{deg}°",
                               fill=GREEN_MID, font=("Consolas", 8))

    def _draw_points(self, cv: tk.Canvas, cx: int, cy: int, r: int):
        alive: list[list] = []
        for pt in self._points:
            pt[2] -= 1
            if pt[2] <= 0:
                continue
            alive.append(pt)
            alpha = pt[2] / TRAIL_STEPS
            g     = int(255 * alpha)
            color = f"#00{g:02x}00"
            px, py = _polar_to_xy(cx, cy, r, pt[0], pt[1])
            sz = 2 + int(3 * alpha)
            cv.create_oval(px - sz, py - sz, px + sz, py + sz,
                           fill=color, outline="")
        self._points = alive

    def _draw_sweep(self, cv: tk.Canvas, cx: int, cy: int, r: int):
        for i in range(30):
            a = self._sweep - i * 1.2
            if a < 0:
                break
            alpha = (30 - i) / 30
            g     = int(150 * alpha)
            col   = f"#00{g:02x}00"
            rad   = _angle_to_rad(a)
            tx    = cx + r * math.cos(rad)
            ty    = cy - r * math.sin(rad)
            cv.create_line(cx, cy, tx, ty, fill=col, width=1)

        rad = _angle_to_rad(self._sweep)
        sx  = cx + r * math.cos(rad)
        sy  = cy - r * math.sin(rad)
        cv.create_line(cx, cy, sx, sy, fill=GREEN_ON, width=2)

    def _draw_base(self, cv: tk.Canvas, cx: int, cy: int, r: int):
        cv.create_line(cx - r, cy, cx + r, cy, fill=GREEN_BRT, width=2)
        cv.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                       fill=GREEN_ON, outline="")
