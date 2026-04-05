"""
popup_hint.py
─────────────
Popup rico para QTreeWidget.
    from popup_hint import PopupHint
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor


class PopupHint(QFrame):

    # Âncora pelo objectName "popup_root" — evita vazar estilo nos filhos
    _BASE = """
        QFrame#popup_root {{
            background-color: {bg};
            border: 1.5px solid {border};
            border-radius: 7px;
        }}
        QFrame#popup_root QLabel {{
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 0;
        }}
        QFrame#popup_root QLabel[role="title"] {{
            font-family: 'Courier New';
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
            color: {fg_title};
        }}
        QFrame#popup_root QLabel[role="lbl"] {{
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 1px;
            color: {fg_lbl};
        }}
        QFrame#popup_root QLabel[role="val"] {{
            font-family: 'Courier New';
            font-size: 11px;
            color: {fg_val};
        }}
        QFrame#popup_divider {{
            background-color: {divider};
            border: none;
            border-radius: 0;
        }}
    """

    THEME_LIGHT = dict(
        bg="#fafafa", border="#1c1c1c",
        fg_title="#111111", fg_lbl="#999999", fg_val="#1a1a1a",
        divider="#dddddd",
    )
    THEME_DARK = dict(
        bg="#1e1e1e", border="#555555",
        fg_title="#e8e8e8", fg_lbl="#666666", fg_val="#cccccc",
        divider="#333333",
    )

    def __init__(self, dark_mode: bool = False, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setObjectName("popup_root")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(300)

        theme = self.THEME_DARK if dark_mode else self.THEME_LIGHT
        self.setStyleSheet(self._BASE.format(**theme))

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 13)
        root.setSpacing(0)

        # título
        root.addWidget(self._lbl("RESUME", "title"))
        root.addSpacing(10)

        # account (esquerda) + created at (direita)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        col_l = QVBoxLayout()
        col_l.setSpacing(2)
        self._val_account = self._lbl("", "val")
        col_l.addWidget(self._lbl("ACCOUNT", "lbl"))
        col_l.addWidget(self._val_account)

        col_r = QVBoxLayout()
        col_r.setSpacing(2)
        col_r.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._val_created = self._lbl("", "val", right=True)
        col_r.addWidget(self._lbl("CREATED AT", "lbl", right=True))
        col_r.addWidget(self._val_created)

        row.addLayout(col_l)
        row.addLayout(col_r)
        root.addLayout(row)
        root.addSpacing(10)

        # divisor
        div = QFrame()
        div.setObjectName("popup_divider")
        div.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        div.setFixedHeight(1)
        root.addWidget(div)
        root.addSpacing(10)

        # url
        self._val_url = self._lbl("", "val")
        root.addWidget(self._lbl("URL", "lbl"))
        root.addSpacing(2)
        root.addWidget(self._val_url)
        root.addSpacing(8)

        # notes
        self._val_notes = self._lbl("", "val")
        root.addWidget(self._lbl("NOTES", "lbl"))
        root.addSpacing(2)
        root.addWidget(self._val_notes)

    @staticmethod
    def _lbl(text: str, role: str, right: bool = False) -> QLabel:
        w = QLabel(text)
        w.setProperty("role", role)
        if right:
            w.setAlignment(Qt.AlignmentFlag.AlignRight)
        return w

    @staticmethod
    def _cut(text: str, limit: int = 46) -> str:
        return text if len(text) <= limit else text[:limit] + "…"

    def set_content(self, data: dict) -> None:
        self._val_account.setText(data.get("account", "—"))
        self._val_created.setText(data.get("created_at", "—"))
        self._val_url.setText(self._cut(data.get("url", "—")))
        self._val_notes.setText(self._cut(data.get("notes", "—")))
        self.adjustSize()

    def show_near_cursor(self) -> None:
        self.move(QCursor.pos() + QPoint(16, 12))
        self.show()
        self.raise_()