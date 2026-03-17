from __future__ import annotations
from dataclasses import dataclass
import time

from core.generation import AccompanimentEngine
from core.midi_bridge import MidiBridge
from core.music_theory import (
    ChordResult,
    KeyResult,
    detect_chord,
    detect_intervals,
    detect_scale_candidates,
    estimate_key,
    midi_note_to_name,
)
from core.state import PerformanceState
from core.transforms import spread, transpose, swing_text

KEYBOARD_MAP = {
    'A': 0,
    'W': 1,
    'S': 2,
    'E': 3,
    'D': 4,
    'F': 5,
    'T': 6,
    'G': 7,
    'Y': 8,
    'H': 9,
    'U': 10,
    'J': 11,
    'K': 12,
}

SCENES = {
    'Bloom Chord': [60, 64, 67, 71],
    'Dream Cadence': [57, 60, 64, 67],
    'Starlit Suspense': [62, 67, 69, 74],
    'Glass Dominant': [55, 59, 62, 65],
    'Iridescent Spread': spread([60, 64, 67, 71]),
    'Luminous Lift': transpose([60, 64, 67], 7),
}


@dataclass
class Snapshot:
    active_note_names: list[str]
    active_note_numbers: list[int]
    chord: ChordResult
    key: KeyResult
    scales: list[str]
    intervals: list[str]
    harmony_label: str
    progression: list[str]
    arp_preview: str
    rhythm_label: str
    rhythm_pattern: str
    transform_label: str
    bpm: int | None
    midi_status: str
    midi_out_status: str
    scale_note_numbers: list[int]
    spark_note: int | None
    recent_notes: list[str]
    new_notes_for_roll: list[int]


class MusicBoxEngine:
    # this is the main coordinator. every ui piece gets fed from here.
    def __init__(self):
        self.state = PerformanceState()
        self.accompaniment = AccompanimentEngine()
        self.midi = MidiBridge()
        self.base_octave = 60
        self.midi_name = self.midi.open_first() or 'Demo / keyboard mode'
        self.midi_out_name = self.midi.open_first_output() or 'No MIDI output'
        self.demo_name = 'No scene loaded'
        self.demo_hold_until: float | None = None
        self.spark_note: int | None = None
        self.auto_spread = False
        self.auto_octave = 0
        self.transpose_amount = 0
        self.midi_echo = False
        self.humanize_preview = False
        self.swing_amount = 0
        self._last_roll_index = 0

    def press_note(self, note: int, velocity: int = 96, channel: int = 0, source: str = 'internal'):
        self.state.note_on(note, velocity, channel, source)

    def release_note(self, note: int, channel: int = 0):
        self.state.note_off(note, channel)

    def clear(self):
        self.state.clear()
        self.spark_note = None

    def handle_qt_key_press(self, key_text: str):
        key = key_text.upper()
        if key == 'Z':
            self.base_octave = max(24, self.base_octave - 12)
            return
        if key == 'X':
            self.base_octave = min(84, self.base_octave + 12)
            return
        if key == ' ':
            self.clear()
            return
        if key in KEYBOARD_MAP:
            note = self.base_octave + KEYBOARD_MAP[key]
            self.press_note(note, 100, source='computer')

    def handle_qt_key_release(self, key_text: str):
        key = key_text.upper()
        if key in KEYBOARD_MAP:
            note = self.base_octave + KEYBOARD_MAP[key]
            self.release_note(note)

    def load_demo(self, notes: list[int], name: str, hold_seconds: float = 4.6):
        self.clear()
        for i, note in enumerate(notes):
            self.press_note(note, velocity=min(118, 92 + i * 7), source='scene')
        self.demo_name = name
        self.demo_hold_until = time.time() + hold_seconds

    def demo_scene(self, scene_name: str):
        self.load_demo(SCENES[scene_name], scene_name)

    def poll_midi(self):
        for msg in self.midi.poll():
            msg_type = getattr(msg, 'type', '')
            if msg_type == 'note_on':
                if getattr(msg, 'velocity', 0) == 0:
                    self.release_note(msg.note, getattr(msg, 'channel', 0))
                else:
                    self.press_note(msg.note, msg.velocity, getattr(msg, 'channel', 0), source='midi')
            elif msg_type == 'note_off':
                self.release_note(msg.note, getattr(msg, 'channel', 0))

    def tick(self) -> Snapshot:
        self.poll_midi()
        if self.demo_hold_until and time.time() >= self.demo_hold_until:
            self.clear()
            self.demo_hold_until = None

        notes = self.state.all_active_notes()
        transformed_notes = notes[:]
        if self.auto_spread:
            transformed_notes = spread(transformed_notes)
        if self.auto_octave:
            transformed_notes = transpose(transformed_notes, self.auto_octave)
        if self.transpose_amount:
            transformed_notes = transpose(transformed_notes, self.transpose_amount)

        chord = detect_chord(transformed_notes)
        key = estimate_key(self.state.history_counter)
        scales = detect_scale_candidates(transformed_notes, key.name)
        intervals = detect_intervals(transformed_notes)
        bpm = self.state.estimated_bpm()
        harmony = self.accompaniment.suggest(
            chord,
            key.name,
            spread_on=self.auto_spread,
            transpose_amt=self.transpose_amount,
            humanize_on=self.humanize_preview,
            swing_amount=self.swing_amount,
        )
        arp_preview = self.accompaniment.arp_preview(harmony.notes, bpm, self.swing_amount)
        self.spark_note = self.accompaniment.next_arp_note(harmony.notes, bpm)

        if self.midi_echo and harmony.notes:
            self.midi.send_notes(harmony.notes[:3])

        transform_bits = []
        if self.auto_spread:
            transform_bits.append('Open spread')
        if self.auto_octave:
            transform_bits.append('Octave lift')
        if self.transpose_amount:
            transform_bits.append(f'Transpose {self.transpose_amount:+d}')
        if self.humanize_preview:
            transform_bits.append('Humanized')
        transform_bits.append(swing_text(self.swing_amount))
        transform_label = ' · '.join(transform_bits)

        scale_note_numbers = [60 + pc for pc in key.scale_notes]
        midi_status = self.midi_name if self.midi_name else self.midi.error or 'Demo mode'
        midi_out_status = self.midi_out_name if self.midi_out_name else 'Off'

        recent_events_list = list(self.state.recent_events)
        new_events = recent_events_list[self._last_roll_index:]
        self._last_roll_index = len(recent_events_list)
        new_notes_for_roll = [note for _, note in new_events]

        recent_notes = [
            f"{entry['name']}  vel {entry['velocity']}  dur {entry['duration']:.2f}s  [{entry['source']}]"
            for entry in self.state.completed_notes[-12:]
        ]

        return Snapshot(
            active_note_names=[midi_note_to_name(n) for n in transformed_notes],
            active_note_numbers=transformed_notes,
            chord=chord,
            key=key,
            scales=scales,
            intervals=intervals,
            harmony_label=harmony.label,
            progression=harmony.progression,
            arp_preview=arp_preview,
            rhythm_label=self.state.rhythm_density(),
            rhythm_pattern=harmony.rhythm_pattern,
            transform_label=transform_label,
            bpm=bpm,
            midi_status=midi_status,
            midi_out_status=midi_out_status,
            scale_note_numbers=scale_note_numbers,
            spark_note=self.spark_note,
            recent_notes=recent_notes,
            new_notes_for_roll=new_notes_for_roll,
        )
