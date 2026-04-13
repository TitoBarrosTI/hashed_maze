from PySide6.QtCore import QPropertyAnimation, QPoint
from shiboken6 import isValid

# Animates a widget to draw attention

def shake_widget(container, widget):
    rect = widget.geometry()

    # Stop previous animation if exists
    if hasattr(widget, "_shake_anim") and isValid(widget._shake_anim):
        return
        # widget._shake_anim.stop()

    anim = QPropertyAnimation(widget, b"geometry")
    widget._shake_anim = anim

    anim.setDuration(300)

    offsets = [8, -8, 6, -6, 4, -4, 0]

    for i, dx in enumerate(offsets):
        anim.setKeyValueAt(i / len(offsets), rect.translated(dx, 0))

    anim.setEndValue(rect)

    # Keep reference
    container._anims = getattr(container, "_anims", [])
    container._anims.append(anim)
    # anim.finished.connect(lambda: container._anims.remove(anim))
    anim.finished.connect(lambda: container._anims.remove(anim) if anim in container._anims else None)

    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)