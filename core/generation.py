from __future__ import annotations
from dataclasses import dataclass
import time

from core.music_theory import ChordResult, NOTE_NAMES, midi_note_to_name
from core.transforms import swing_text


@dataclass
class HarmonySuggestion:
    notes: list[int]
    label: str
    progression: list[str]
    rhythm_pattern: str


class AccompanimentEngine:
    # this is the generative side. it turns detected harmony into supportive suggestions.
    def __init__(self):
        self.arp_patterns = {
            'bloom': [0, 1, 2, 1, 2, 1],
            'up': [0, 1, 2, 3],
            'down': [3, 2, 1, 0],
            'pulse': [0, 2, 1, 2],
        }
        self.arp_mode = 'bloom'
        self.arp_index = 0
        self.last_step_time = time.time()
        self.step_interval = 0.18

    def suggest(self, chord: ChordResult, key_name: str, *, spread_on: bool = False, transpose_amt: int = 0, humanize_on: bool = False, swing_amount: int = 0) -> HarmonySuggestion:
        if chord.root is None:
            return HarmonySuggestion([], '—', ['—'], 'No rhythmic accompaniment yet')

        root_pc = NOTE_NAMES.index(chord.root)
        quality = chord.quality or 'maj'
        if quality.startswith('maj') or quality in {'6', '7', '+7', 'sus2', 'sus4', '5'}:
            pattern = [0, 4, 7, 11] if 'maj7' in quality else [0, 4, 7, 10] if quality == '7' else [0, 4, 7]
            rhythm = 'lifted broken-chord pulse'
        elif quality.startswith('min') or quality in {'m7b5', 'dim7'}:
            pattern = [0, 3, 7, 10] if '7' in quality else [0, 3, 7]
            if quality == 'm7b5':
                pattern = [0, 3, 6, 10]
            if quality == 'dim7':
                pattern = [0, 3, 6, 9]
            rhythm = 'dark rolling accompaniment'
        elif quality == 'dim':
            pattern = [0, 3, 6]
            rhythm = 'tense rhythmic pulse'
        elif quality == 'aug':
            pattern = [0, 4, 8]
            rhythm = 'rising unstable shimmer'
        else:
            pattern = [0, 4, 7]
            rhythm = 'steady support'

        base = 48 + root_pc + transpose_amt
        notes = [base + x for x in pattern]
        if spread_on and len(notes) >= 3:
            notes = [notes[0], notes[1] + 12, notes[2]] + notes[3:]

        label = ', '.join(midi_note_to_name(n) for n in notes)
        if humanize_on:
            label += ' · humanized preview'
        label += f' · {swing_text(swing_amount)}'

        progression = self.progression_suggestions(chord, key_name)
        return HarmonySuggestion(notes, label, progression, rhythm)

    def progression_suggestions(self, chord: ChordResult, key_name: str) -> list[str]:
        if chord.root is None:
            return ['—']
        root = chord.root
        if 'major' in key_name:
            presets = {
                'C': ['Cmaj7', 'G', 'Am7', 'Fmaj7'],
                'G': ['G', 'D', 'Em7', 'Cmaj7'],
                'D': ['D', 'A', 'Bm7', 'Gmaj7'],
                'F': ['Fmaj7', 'C', 'Dm7', 'Bbmaj7'],
            }
            return presets.get(root, [f'{root}{chord.quality or ""}', 'vi', 'IV', 'V'])
        presets = {
            'A': ['Am', 'F', 'C', 'G'],
            'E': ['Em', 'C', 'G', 'D'],
            'D': ['Dm', 'Bb', 'F', 'C'],
        }
        return presets.get(root, [f'{root}{chord.quality or ""}', 'bVI', 'bIII', 'bVII'])

    def arp_preview(self, notes: list[int], bpm: int | None = None, swing_amount: int = 0) -> str:
        if not notes:
            return '—'
        if bpm:
            self.step_interval = max(0.08, 60.0 / bpm / 2.0)
        pattern = self.arp_patterns.get(self.arp_mode, [0, 1, 2, 1])
        clamped = [notes[i % len(notes)] for i in pattern]
        preview = ' · '.join(midi_note_to_name(n) for n in clamped[:8])
        return f'{preview} · {swing_text(swing_amount)}'

    def next_arp_note(self, notes: list[int], bpm: int | None = None) -> int | None:
        if not notes:
            return None
        if bpm:
            self.step_interval = max(0.08, 60.0 / bpm / 2.0)
        now = time.time()
        if now - self.last_step_time < self.step_interval:
            return None
        self.last_step_time = now
        pattern = self.arp_patterns.get(self.arp_mode, [0, 1, 2, 1])
        idx = pattern[self.arp_index % len(pattern)] % len(notes)
        self.arp_index += 1
        return notes[idx]
