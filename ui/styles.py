APP_QSS = """
QWidget {
    background-color: #0f0f16;
    color: #f6efe7;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 14px;
}
QLabel#TitleLabel {
    font-size: 28px;
    font-weight: 700;
    color: #fff5eb;
}
QLabel#SubtitleLabel {
    font-size: 13px;
    color: #d5c7c0;
}
QLabel#ControlLabel {
    font-size: 11px;
    color: #c8bec3;
}
QFrame[card="true"] {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #171723, stop:1 #1f1b2a);
    border: 1px solid rgba(255, 234, 214, 0.18);
    border-radius: 18px;
}
QLabel[metric="true"] {
    font-size: 13px;
    color: #d8cfc9;
}
QLabel[value="true"] {
    font-size: 18px;
    font-weight: 600;
    color: #fff5eb;
}
QPushButton {
    background-color: #2a2236;
    border: 1px solid rgba(255, 233, 213, 0.25);
    border-radius: 14px;
    padding: 10px 14px;
    color: #fff3e8;
}
QPushButton:hover {
    background-color: #3a2b4b;
}
QPushButton:pressed {
    background-color: #4f3568;
}
QListWidget, QTextEdit {
    background: transparent;
    border: none;
    outline: none;
    color: #ffe7d8;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
    border: none;
}
QComboBox, QCheckBox {
    color: #fff3e8;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #2a2334;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #f2c6ff;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
"""
