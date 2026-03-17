from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass
import time
from typing import Deque

from core.music_theory import midi_note_to_name


@dataclass
class ActiveNote:
    note: int
    velocity: int
    channel: int
    start_time: float
    source: str = 'internal'


class PerformanceState:
    # this is basically the memory of the whole app.
    # it keeps active notes, note history, event timing, and completed note stats.
    def __init__(self):
        self.active_notes: dict[tuple[int, int], ActiveNote] = {}
        self.completed_notes: list[dict] = []
        self.history_counter: Counter[int] = Counter()
        self.recent_note_ons: Deque[float] = deque(maxlen=128)
        self.recent_events: Deque[tuple[float, int]] = deque(maxlen=256)

    def note_on(self, note: int, velocity: int, channel: int = 0, source: str = 'internal'):
        now = time.time()
        key = (channel, note)
        self.active_notes[key] = ActiveNote(note, velocity, channel, now, source)
        self.history_counter[note % 12] += 1
        self.recent_note_ons.append(now)
        self.recent_events.append((now, note))

    def note_off(self, note: int, channel: int = 0):
        now = time.time()
        key = (channel, note)
        active = self.active_notes.pop(key, None)
        if active:
            self.completed_notes.append({
                'note': note,
                'name': midi_note_to_name(note),
                'velocity': active.velocity,
                'duration': now - active.start_time,
                'start': active.start_time,
                'end': now,
                'source': active.source,
            })
            self.completed_notes = self.completed_notes[-100:]

    def clear(self):
        for channel, note in list(self.active_notes.keys()):
            self.note_off(note, channel)

    def all_active_notes(self) -> list[int]:
        return sorted(note.note for note in self.active_notes.values())

    def rhythm_density(self) -> str:
        now = time.time()
        window = [t for t in self.recent_note_ons if now - t <= 4.0]
        rate = len(window) / 4.0
        if rate < 0.75:
            return 'Breathing / sparse'
        if rate < 1.75:
            return 'Gentle pulse'
        if rate < 3.0:
            return 'Flowing eighth-note feel'
        return 'Sparkling dense motion'

    def rhythm_pattern(self) -> str:
        times = list(self.recent_note_ons)[-8:]
        if len(times) < 4:
            return 'Waiting for phrase'
        gaps = [times[i] - times[i - 1] for i in range(1, len(times)) if 0.05 <= times[i] - times[i - 1] <= 1.5]
        if not gaps:
            return 'Waiting for phrase'
        avg = sum(gaps) / len(gaps)
        spread = max(gaps) - min(gaps) if len(gaps) > 1 else 0.0
        if avg < 0.2:
            return '16th-note shimmer'
        if spread < 0.05:
            return 'Steady grid pulse'
        if spread < 0.12:
            return 'Human groove / loose pulse'
        return 'Rubato / elastic phrase'

    def estimated_bpm(self) -> int | None:
        times = list(self.recent_note_ons)
        if len(times) < 4:
            return None
        deltas = [times[i] - times[i - 1] for i in range(1, len(times)) if 0.08 <= times[i] - times[i - 1] <= 1.5]
        if not deltas:
            return None
        avg = sum(deltas[-12:]) / min(12, len(deltas))
        if avg <= 0:
            return None
        bpm = int(round(60.0 / avg))
        return max(40, min(220, bpm))
