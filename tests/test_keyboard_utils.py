import sys
from pathlib import Path

from PySide6.QtCore import Qt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "boris"))

import keyboard_utils


def test_macos_arrow_keypad_modifier_is_normalized(monkeypatch):
    monkeypatch.setattr(keyboard_utils.sys, "platform", "darwin")

    modifiers = Qt.KeyboardModifier.KeypadModifier
    normalized = keyboard_utils.normalize_modifiers(Qt.Key.Key_Left, modifiers)
    sequence = keyboard_utils.key_sequence_from_key(Qt.Key.Key_Left, normalized)

    assert normalized == Qt.KeyboardModifier.NoModifier
    assert sequence.toString() == "Left"


def test_non_macos_keeps_keypad_modifier(monkeypatch):
    monkeypatch.setattr(keyboard_utils.sys, "platform", "linux")

    modifiers = Qt.KeyboardModifier.KeypadModifier
    normalized = keyboard_utils.normalize_modifiers(Qt.Key.Key_Left, modifiers)
    sequence = keyboard_utils.key_sequence_from_key(Qt.Key.Key_Left, normalized)

    assert normalized == Qt.KeyboardModifier.KeypadModifier
    assert sequence.toString() == "Num+Left"
