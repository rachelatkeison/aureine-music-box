from __future__ import annotations
import time
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout


class PianoRollWidget(QWidget):
    # this is the gesture observatory. the big fix is: no auto-range button nonsense.
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)
        self.plot.setBackground((0, 0, 0, 0))
        self.plot.hideAxis('bottom')
        self.plot.hideAxis('left')
        self.plot.hideButtons()
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.setMenuEnabled(False)
        self.plot.setLimits(xMin=-10, xMax=0.5, yMin=30, yMax=96)
        self.plot.setXRange(-10, 0.5, padding=0)
        self.plot.setYRange(36, 96, padding=0)

        self.scale_scatter = pg.ScatterPlotItem(size=7, brush=pg.mkBrush(160, 188, 255, 65), pen=None)
        self.trail_scatter = pg.ScatterPlotItem(size=9, brush=pg.mkBrush(197, 160, 255, 72), pen=None)
        self.scatter = pg.ScatterPlotItem(size=14, brush=pg.mkBrush(255, 225, 199, 224), pen=pg.mkPen(255, 240, 228, 90))
        self.spark = pg.ScatterPlotItem(size=18, brush=pg.mkBrush(255, 206, 144, 220), pen=pg.mkPen(255, 244, 220, 120))

        self.plot.addItem(self.scale_scatter)
        self.plot.addItem(self.trail_scatter)
        self.plot.addItem(self.scatter)
        self.plot.addItem(self.spark)

        self.note_events: list[tuple[float, int]] = []
        self.scale_notes: list[int] = []
        self.spark_note: int | None = None

    def add_note(self, note: int):
        self.note_events.append((time.time(), note))
        self.refresh()

    def add_notes(self, notes: list[int]):
        now = time.time()
        for note in notes:
            self.note_events.append((now, note))
        self.refresh()

    def set_scale(self, scale_notes: list[int]):
        self.scale_notes = scale_notes[:]

    def set_spark_note(self, note: int | None):
        self.spark_note = note

    def refresh(self):
        now = time.time()
        self.note_events = [(t, n) for (t, n) in self.note_events if now - t <= 10]

        xs = [t - now for t, _ in self.note_events]
        ys = [n for _, n in self.note_events]
        self.scatter.setData(xs, ys)

        trail_xs = []
        trail_ys = []
        for t, n in self.note_events:
            if now - t <= 2.6:
                for step in range(1, 6):
                    trail_xs.append((t - now) - (step * 0.14))
                    trail_ys.append(n)
        self.trail_scatter.setData(trail_xs, trail_ys)

        scale_xs = [-9.5 + (i * 0.75) for i in range(len(self.scale_notes))]
        self.scale_scatter.setData(scale_xs, self.scale_notes)

        if self.spark_note is not None:
            self.spark.setData([-0.6], [self.spark_note])
        else:
            self.spark.setData([], [])

        # force stable view every refresh so notes are always visible.
        self.plot.setXRange(-10, 0.5, padding=0)
        self.plot.setYRange(36, 96, padding=0)
