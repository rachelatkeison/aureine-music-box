from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QGridLayout,
    QCheckBox,
    QTextEdit,
    QSlider,
)

from core.engine import MusicBoxEngine, SCENES
from ui.chord_bloom import ChordBloomWidget
from ui.piano_roll import PianoRollWidget
from ui.styles import APP_QSS
from ui.tonal_orbit import TonalOrbitWidget
from ui.widgets import Card, MetricRow


class AppWindow(QWidget):
    def __init__(self, engine: MusicBoxEngine):
        super().__init__()
        self.engine = engine
        self.last_chord_name = 'No chord'
        self.setWindowTitle('Aureine MIDI Intelligence Engine — Music Box')
        self.resize(1500, 920)
        self.setMinimumSize(1360, 860)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(APP_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        title = QLabel('Aureine Music Box')
        title.setObjectName('TitleLabel')
        subtitle = QLabel("Music Box — a real-time harmonic intelligence system for expressive MIDI performance")
        subtitle.setObjectName('SubtitleLabel')
        root.addWidget(title)
        root.addWidget(subtitle)

        top = QHBoxLayout()
        top.setSpacing(14)
        root.addLayout(top, 1)

        left_col = QVBoxLayout(); left_col.setSpacing(14); top.addLayout(left_col, 1)
        middle_col = QVBoxLayout(); middle_col.setSpacing(14); top.addLayout(middle_col, 1)
        right_col = QVBoxLayout(); right_col.setSpacing(14); top.addLayout(right_col, 1)

        self.status_card = Card('Performance Memory')
        self.active_list = QListWidget()
        self.status_card.body.addWidget(self.active_list)
        self.keyboard_hint = QLabel('Keyboard input: A W S E D F T G Y H U J K · Z/X octave · Space clears')
        self.keyboard_hint.setProperty('metric', True)
        self.status_card.body.addWidget(self.keyboard_hint)
        left_col.addWidget(self.status_card)

        self.monitor_card = Card('Activity Monitor')
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        self.monitor_card.body.addWidget(self.activity_text)
        left_col.addWidget(self.monitor_card)

        self.analysis_card = Card('Harmonic Insight')
        self.row_chord = MetricRow('Chord', '—')
        self.row_key = MetricRow('Key', '—')
        self.row_scale = MetricRow('Scales', '—')
        self.row_intervals = MetricRow('Intervals', '—')
        self.analysis_card.body.addLayout(self.row_chord)
        self.analysis_card.body.addLayout(self.row_key)
        self.analysis_card.body.addLayout(self.row_scale)
        self.analysis_card.body.addLayout(self.row_intervals)
        middle_col.addWidget(self.analysis_card)

        self.gen_card = Card('Generative Bloom')
        self.row_harmony = MetricRow('Harmony', '—')
        self.row_progression = MetricRow('Progression', '—')
        self.row_arp = MetricRow('Arp', '—')
        self.row_rhythm = MetricRow('Rhythm pattern', '—')
        self.row_transform = MetricRow('Transform', 'Straight')
        self.gen_card.body.addLayout(self.row_harmony)
        self.gen_card.body.addLayout(self.row_progression)
        self.gen_card.body.addLayout(self.row_arp)
        self.gen_card.body.addLayout(self.row_rhythm)
        self.gen_card.body.addLayout(self.row_transform)
        middle_col.addWidget(self.gen_card)

        self.bloom_card = Card('Bloom Field')
        self.bloom = ChordBloomWidget()
        self.bloom_card.body.addWidget(self.bloom)
        middle_col.addWidget(self.bloom_card)

        self.meta_card = Card('System Aura')
        self.row_midi = MetricRow('Input', self.engine.midi_name)
        self.row_out = MetricRow('Output', self.engine.midi_out_name)
        self.row_bpm = MetricRow('Tempo sense', '—')
        self.row_scene = MetricRow('Scene', self.engine.demo_name)
        self.meta_card.body.addLayout(self.row_midi)
        self.meta_card.body.addLayout(self.row_out)
        self.meta_card.body.addLayout(self.row_bpm)
        self.meta_card.body.addLayout(self.row_scene)

        self.chk_spread = QCheckBox('Open voicing bloom')
        self.chk_oct = QCheckBox('Octave lift')
        self.chk_echo = QCheckBox('MIDI echo if available')
        self.chk_humanize = QCheckBox('Humanize preview')
        self.meta_card.body.addWidget(self.chk_spread)
        self.meta_card.body.addWidget(self.chk_oct)
        self.meta_card.body.addWidget(self.chk_echo)
        self.meta_card.body.addWidget(self.chk_humanize)

        self.swing_label = QLabel('Swing amount')
        self.swing_label.setObjectName('ControlLabel')
        self.swing_slider = QSlider(Qt.Horizontal)
        self.swing_slider.setRange(0, 60)
        self.swing_slider.setValue(0)
        self.meta_card.body.addWidget(self.swing_label)
        self.meta_card.body.addWidget(self.swing_slider)

        self.transpose_label = QLabel('Transpose semitones')
        self.transpose_label.setObjectName('ControlLabel')
        self.transpose_slider = QSlider(Qt.Horizontal)
        self.transpose_slider.setRange(-12, 12)
        self.transpose_slider.setValue(0)
        self.meta_card.body.addWidget(self.transpose_label)
        self.meta_card.body.addWidget(self.transpose_slider)
        right_col.addWidget(self.meta_card)

        self.scene_card = Card('Aureine Demo Constellations')
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        for i, scene in enumerate(SCENES):
            btn = QPushButton(scene)
            btn.clicked.connect(lambda _, s=scene: self._trigger_scene(s))
            grid.addWidget(btn, i // 2, i % 2)
        self.scene_card.body.addLayout(grid)
        right_col.addWidget(self.scene_card)

        self.orbit_card = Card('Tonal Orbit')
        self.tonal_orbit = TonalOrbitWidget()
        self.orbit_card.body.addWidget(self.tonal_orbit)
        right_col.addWidget(self.orbit_card)

        bottom = QHBoxLayout(); bottom.setSpacing(14)
        root.addLayout(bottom, 2)
        self.roll_card = Card('Gesture Observatory')
        self.piano_roll = PianoRollWidget()
        self.roll_card.body.addWidget(self.piano_roll)
        bottom.addWidget(self.roll_card, 3)

        self.chk_spread.toggled.connect(self._set_spread)
        self.chk_oct.toggled.connect(self._set_octave)
        self.chk_echo.toggled.connect(self._set_echo)
        self.chk_humanize.toggled.connect(self._set_humanize)
        self.swing_slider.valueChanged.connect(self._set_swing)
        self.transpose_slider.valueChanged.connect(self._set_transpose)

    def _trigger_scene(self, scene_name: str):
        self.engine.demo_scene(scene_name)
        self.piano_roll.add_notes(SCENES.get(scene_name, []))

    def _set_spread(self, checked: bool):
        self.engine.auto_spread = checked

    def _set_octave(self, checked: bool):
        self.engine.auto_octave = 12 if checked else 0

    def _set_echo(self, checked: bool):
        self.engine.midi_echo = checked

    def _set_humanize(self, checked: bool):
        self.engine.humanize_preview = checked

    def _set_swing(self, value: int):
        self.engine.swing_amount = value

    def _set_transpose(self, value: int):
        self.engine.transpose_amount = value

    def tick(self):
        snapshot = self.engine.tick()

        self.active_list.clear()
        self.active_list.addItems(snapshot.active_note_names or ['—'])

        self.row_chord.value.setText(snapshot.chord.name)
        key_text = snapshot.key.name if snapshot.key.name != 'Unknown' else 'Listening…'
        if snapshot.key.confidence:
            key_text += f'  ({int(snapshot.key.confidence * 100)}%)'
        self.row_key.value.setText(key_text)
        self.row_scale.value.setText(' • '.join(snapshot.scales[:2]))
        self.row_intervals.value.setText(', '.join(snapshot.intervals[:4]) if snapshot.intervals else '—')
        self.row_harmony.value.setText(snapshot.harmony_label)
        self.row_progression.value.setText(' → '.join(snapshot.progression[:4]))
        self.row_arp.value.setText(snapshot.arp_preview)
        self.row_rhythm.value.setText(snapshot.rhythm_pattern)
        self.row_transform.value.setText(snapshot.transform_label)

        self.row_midi.value.setText(snapshot.midi_status)
        self.row_out.value.setText(snapshot.midi_out_status)
        self.row_bpm.value.setText(str(snapshot.bpm) if snapshot.bpm else '—')
        self.row_scene.value.setText(self.engine.demo_name)

        self.activity_text.setPlainText('\n'.join(snapshot.recent_notes[-8:]) if snapshot.recent_notes else 'Waiting for notes')
        self.tonal_orbit.update_state(snapshot.active_note_numbers, snapshot.scale_note_numbers, snapshot.key.name)

        if snapshot.chord.name != self.last_chord_name and snapshot.chord.name != 'No chord':
            self.bloom.trigger(snapshot.chord.name)
            self.last_chord_name = snapshot.chord.name

        for note in snapshot.new_notes_for_roll:
            self.piano_roll.add_note(note)
        self.piano_roll.set_scale(snapshot.scale_note_numbers)
        self.piano_roll.set_spark_note(snapshot.spark_note)
        self.piano_roll.refresh()

    def keyPressEvent(self, event: QKeyEvent):
        text = event.text()
        if text:
            self.engine.handle_qt_key_press(text)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        text = event.text()
        if text:
            self.engine.handle_qt_key_release(text)
        super().keyReleaseEvent(event)
