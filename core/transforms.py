from __future__ import annotations
import random

# little utility helpers for the transformation side of the app.

def transpose(notes: list[int], semitones: int) -> list[int]:
    return [n + semitones for n in notes]


def spread(notes: list[int]) -> list[int]:
    if len(notes) < 3:
        return notes[:]
    out = []
    for i, note in enumerate(sorted(notes)):
        out.append(note + (12 if i % 2 == 1 else 0))
    return sorted(out)


def humanized_offsets(count: int, amount_ms: float = 8.0) -> list[float]:
    return [random.uniform(-amount_ms, amount_ms) / 1000.0 for _ in range(count)]


def swing_text(amount: int) -> str:
    if amount <= 0:
        return 'Straight'
    if amount < 20:
        return 'Light swing'
    if amount < 40:
        return 'Medium swing'
    return 'Heavy swing'
