from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

# chill theory constants. this file is the music-brain side of the app.
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

MAJOR_SCALE = {0, 2, 4, 5, 7, 9, 11}
MINOR_SCALE = {0, 2, 3, 5, 7, 8, 10}
DORIAN_SCALE = {0, 2, 3, 5, 7, 9, 10}
MIXOLYDIAN_SCALE = {0, 2, 4, 5, 7, 9, 10}
PENTATONIC_MAJOR = {0, 2, 4, 7, 9}
PENTATONIC_MINOR = {0, 3, 5, 7, 10}

CHORD_PATTERNS = {
    (0, 4, 7): "maj",
    (0, 3, 7): "min",
    (0, 3, 6): "dim",
    (0, 4, 8): "aug",
    (0, 5, 7): "sus4",
    (0, 2, 7): "sus2",
    (0, 4, 7, 10): "7",
    (0, 4, 7, 11): "maj7",
    (0, 3, 7, 10): "min7",
    (0, 3, 6, 10): "m7b5",
    (0, 3, 6, 9): "dim7",
    (0, 4, 7, 9): "6",
    (0, 3, 7, 9): "min6",
    (0, 7): "5",
}

INTERVAL_NAMES = {
    0: "Unison",
    1: "m2",
    2: "M2",
    3: "m3",
    4: "M3",
    5: "P4",
    6: "TT",
    7: "P5",
    8: "m6",
    9: "M6",
    10: "m7",
    11: "M7",
    12: "Octave",
}

K_KEY_PROFILES = {
    "major": [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
    "minor": [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17],
}


@dataclass
class ChordResult:
    name: str
    root: str | None
    quality: str | None
    inversion: str | None
    confidence: float
    pitch_classes: list[int]


@dataclass
class KeyResult:
    name: str
    confidence: float
    scale_notes: list[int]
    alternate: str


def midi_note_to_name(note: int) -> str:
    return f"{NOTE_NAMES[note % 12]}{(note // 12) - 1}"


def pitch_classes(notes: Iterable[int]) -> list[int]:
    return sorted(set(n % 12 for n in notes))


def normalize_to_root(pcs: list[int], root: int) -> tuple[int, ...]:
    return tuple(sorted((pc - root) % 12 for pc in pcs))


def detect_intervals(notes: list[int]) -> list[str]:
    uniq = sorted(set(notes))
    names: list[str] = []
    for i in range(len(uniq)):
        for j in range(i + 1, len(uniq)):
            names.append(INTERVAL_NAMES.get((uniq[j] - uniq[i]) % 12, str((uniq[j] - uniq[i]) % 12)))
    return names


def detect_chord(notes: list[int]) -> ChordResult:
    if not notes:
        return ChordResult("No chord", None, None, None, 0.0, [])

    pcs = pitch_classes(notes)
    bass_pc = min(notes) % 12

    for root in pcs:
        shape = normalize_to_root(pcs, root)
        if shape in CHORD_PATTERNS:
            quality = CHORD_PATTERNS[shape]
            root_name = NOTE_NAMES[root]
            inversion = None if bass_pc == root else f"/{NOTE_NAMES[bass_pc]}"
            conf = 0.92 if len(shape) >= 3 else 0.72
            return ChordResult(f"{root_name}{quality}{inversion or ''}", root_name, quality, inversion, conf, pcs)

    # partial rescue so the app still feels smart with only 2 notes
    triad_checks = {
        frozenset({0, 4}): "maj(no5)",
        frozenset({0, 3}): "min(no5)",
        frozenset({0, 7}): "5",
        frozenset({4, 7}): "maj(no1)",
        frozenset({3, 7}): "min(no1)",
    }
    for root in range(12):
        shifted = frozenset((pc - root) % 12 for pc in pcs)
        if shifted in triad_checks:
            q = triad_checks[shifted]
            return ChordResult(f"{NOTE_NAMES[root]}{q}", NOTE_NAMES[root], q, None, 0.56, pcs)

    return ChordResult("Unknown chord", None, None, None, 0.16, pcs)


def rotate_profile(profile: list[float], amount: int) -> list[float]:
    return profile[-amount:] + profile[:-amount]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def estimate_key(history_counter: Counter[int]) -> KeyResult:
    if not history_counter:
        return KeyResult("Unknown", 0.0, [], "—")

    vec = [float(history_counter.get(i, 0)) for i in range(12)]
    total = sum(vec) or 1.0
    vec = [x / total for x in vec]

    best_name = "Unknown"
    best_score = float('-inf')
    second_name = "Unknown"
    second_score = float('-inf')
    best_scale: list[int] = []

    for root in range(12):
        major_score = _dot(vec, rotate_profile(K_KEY_PROFILES['major'], root))
        minor_score = _dot(vec, rotate_profile(K_KEY_PROFILES['minor'], root))

        for mode_name, score, scale in [
            (f"{NOTE_NAMES[root]} major", major_score, sorted((root + x) % 12 for x in MAJOR_SCALE)),
            (f"{NOTE_NAMES[root]} minor", minor_score, sorted((root + x) % 12 for x in MINOR_SCALE)),
        ]:
            if score > best_score:
                second_name, second_score = best_name, best_score
                best_name, best_score, best_scale = mode_name, score, scale
            elif score > second_score:
                second_name, second_score = mode_name, score

    confidence = 0.0 if best_score <= 0 else max(0.0, min(1.0, (best_score - second_score) / best_score))
    return KeyResult(best_name, confidence, best_scale, second_name)


def detect_scale_candidates(notes: list[int], key_name: str) -> list[str]:
    if not notes:
        return ["Listening for tonal center"]

    pcs = set(pitch_classes(notes))
    options: list[str] = []
    for root in range(12):
        for mode_name, sc in [
            ("major", {(root + x) % 12 for x in MAJOR_SCALE}),
            ("minor", {(root + x) % 12 for x in MINOR_SCALE}),
            ("dorian", {(root + x) % 12 for x in DORIAN_SCALE}),
            ("mixolydian", {(root + x) % 12 for x in MIXOLYDIAN_SCALE}),
            ("maj pent", {(root + x) % 12 for x in PENTATONIC_MAJOR}),
            ("min pent", {(root + x) % 12 for x in PENTATONIC_MINOR}),
        ]:
            if pcs.issubset(sc):
                options.append(f"{NOTE_NAMES[root]} {mode_name}")

    if key_name != 'Unknown':
        root = key_name.split()[0]
        options = sorted(options, key=lambda x: (0 if x.startswith(root) else 1, x))
    return options[:4] or ["Chromatic / ambiguous"]
