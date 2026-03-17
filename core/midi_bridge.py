from __future__ import annotations

# midi is optional. if it doesn't work, the app still works perfectly in demo/keyboard mode.
try:
    import mido
except Exception:
    mido = None


class MidiBridge:
    def __init__(self):
        self.inport = None
        self.outport = None
        self.error = None
        self.enabled = mido is not None

    def open_first(self):
        if not self.enabled:
            self.error = 'mido not installed'
            return None
        try:
            names = mido.get_input_names()
            if names:
                self.inport = mido.open_input(names[0])
                return names[0]
        except Exception as exc:
            self.error = str(exc)
        return None

    def open_first_output(self):
        if not self.enabled:
            return None
        try:
            names = mido.get_output_names()
            if names:
                self.outport = mido.open_output(names[0])
                return names[0]
        except Exception:
            return None
        return None

    def poll(self) -> list[object]:
        if not self.inport:
            return []
        try:
            return list(self.inport.iter_pending())
        except Exception as exc:
            self.error = str(exc)
            return []

    def send_notes(self, notes: list[int], velocity: int = 64):
        if not (self.enabled and self.outport and notes):
            return
        try:
            for note in notes:
                self.outport.send(mido.Message('note_on', note=int(note), velocity=velocity))
        except Exception as exc:
            self.error = str(exc)
