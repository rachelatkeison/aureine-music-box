from __future__ import annotations
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget


class ChordBloomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._glow = 0.2
        self.chord_name = '—'
        self.setMinimumHeight(175)
        self.anim = QPropertyAnimation(self, b'glowLevel')
        self.anim.setDuration(950)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.2)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def getGlowLevel(self):
        return self._glow

    def setGlowLevel(self, value):
        self._glow = float(value)
        self.update()

    glowLevel = Property(float, getGlowLevel, setGlowLevel)

    def trigger(self, chord_name: str):
        self.chord_name = chord_name
        self.anim.stop()
        self.anim.start()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor('#12111c'))

        cx = self.width() / 2
        cy = self.height() / 2
        base = min(self.width(), self.height()) * 0.22

        rings = [1.9, 1.45, 1.05]
        colors = [
            QColor(120, 185, 255, int(42 * self._glow + 16)),
            QColor(185, 156, 242, int(72 * self._glow + 20)),
            QColor(255, 208, 178, int(112 * self._glow + 32)),
        ]

        for mult, color in zip(rings, colors):
            p.setBrush(color)
            p.setPen(QPen(QColor(255, 245, 235, 26), 1))
            r = base * mult * (0.9 + self._glow * 0.18)
            p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))

        p.setPen(QColor('#fff6ed'))
        p.setFont(QFont('Avenir Next', 11))
        p.drawText(QRectF(0, 20, self.width(), 24), 0x84, 'Chord Bloom')
        p.setFont(QFont('Avenir Next', 24, QFont.Bold))
        p.drawText(QRectF(0, cy - 16, self.width(), 34), 0x84, self.chord_name)
