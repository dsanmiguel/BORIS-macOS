import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence


MACOS_NAVIGATION_KEYS = {
    Qt.Key.Key_Left,
    Qt.Key.Key_Right,
    Qt.Key.Key_Up,
    Qt.Key.Key_Down,
}


def normalize_modifiers(key: Qt.Key, modifiers: Qt.KeyboardModifier) -> Qt.KeyboardModifier:
    """
    macOS may report arrow keys with KeypadModifier on Apple keyboards.
    Strip only that modifier for navigation keys so shortcuts stay portable
    without changing real keypad handling on other platforms.
    """
    if sys.platform == "darwin" and key in MACOS_NAVIGATION_KEYS:
        normalized_value = modifiers.value & ~Qt.KeyboardModifier.KeypadModifier.value
        return Qt.KeyboardModifier(normalized_value)

    return modifiers


def key_sequence_from_key(key: Qt.Key, modifiers: Qt.KeyboardModifier) -> QKeySequence:
    return QKeySequence(int(key) | modifiers.value)
