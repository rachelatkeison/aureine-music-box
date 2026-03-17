from __future__ import annotations
import math
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QWidget

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


class TonalOrbitWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.active_pitch_classes: set[int] = set()
        self.scale_pitch_classes: set[int] = set()
        self.key_name: str = 'Unknown'
        self.setMinimumHeight(255)

    def update_state(self, active_notes: list[int], scale_notes: list[int], key_name: str):
        self.active_pitch_classes = {n % 12 for n in active_notes}
        self.scale_pitch_classes = {n % 12 for n in scale_notes}
        self.key_name = key_name
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor('#12111c'))

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2
        r = min(w, h) * 0.34

        ring_pen = QPen(QColor('#4f3f66'))
        ring_pen.setWidth(2)
        painter.setPen(ring_pen)
        painter.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        painter.drawEllipse(QRectF(cx - r * 0.65, cy - r * 0.65, 2 * r * 0.65, 2 * r * 0.65))

        order = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
        painter.setFont(QFont('Avenir Next', 10, QFont.Bold))

        for i, pc in enumerate(order):
            angle = -math.pi / 2 + (2 * math.pi * i / 12)
            x = cx + math.cos(angle) * r
            y = cy + math.sin(angle) * r
            node_r = 18

            if pc in self.active_pitch_classes:
                fill = QColor('#ffd0b5')
                text = QColor('#2a1d18')
            elif pc in self.scale_pitch_classes:
                fill = QColor('#b99cf2')
                text = QColor('#160f22')
            else:
                fill = QColor('#2a2337')
                text = QColor('#f5e9df')

            painter.setBrush(fill)
            painter.setPen(QPen(QColor('#f8efe7'), 1))
            painter.drawEllipse(QRectF(x - node_r, y - node_r, node_r * 2, node_r * 2))
            painter.setPen(text)
            painter.drawText(QRectF(x - 16, y - 10, 32, 20), Qt.AlignCenter, NOTE_NAMES[pc])

        painter.setPen(QColor('#fff4ea'))
        painter.setFont(QFont('Avenir Next', 13, QFont.Bold))
        painter.drawText(QRectF(0, cy - 16, w, 18), Qt.AlignCenter, 'Tonal Orbit')
        painter.setPen(QColor('#d8c9c0'))
        painter.setFont(QFont('Avenir Next', 10))
        painter.drawText(QRectF(0, cy + 4, w, 18), Qt.AlignCenter, self.key_name)
