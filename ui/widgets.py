from __future__ import annotations
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt


class Card(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setProperty('card', True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        label = QLabel(title)
        label.setProperty('metric', True)
        layout.addWidget(label)

        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        layout.addLayout(self.body)


class MetricRow(QHBoxLayout):
    def __init__(self, label_text: str, value_text: str = '—'):
        super().__init__()
        self.label = QLabel(label_text)
        self.label.setProperty('metric', True)
        self.value = QLabel(value_text)
        self.value.setProperty('value', True)
        self.value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.addWidget(self.label)
        self.addStretch(1)
        self.addWidget(self.value)
