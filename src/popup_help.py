"""
popup_help.py
─────────────
Contextual help to '?' buttons.
    from popup_help import PopupHelp
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor


class PopupHelp(QFrame):

    _BASE = """
        QFrame#help_root {{
            background-color: {bg};
            border: 1.5px solid {border};
            border-radius: 7px;
        }}
        QFrame#help_root QLabel {{
            background: transparent;
            border: none;
            border-radius: 0;
            padding: 0;
        }}
        QFrame#help_root QLabel[role="title"] {{
            font-family: 'Courier New';
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
            color: {fg_title};
        }}
        QFrame#help_root QLabel[role="body"] {{
            font-size: 10px;
            color: {fg_body};
            line-height: 1.5;
        }}
        QFrame#help_divider {{
            background-color: {divider};
            border: none;
            border-radius: 0;
        }}
    """

    THEME_DARK = dict(
        bg="#1e1e1e", border="#555555",
        fg_title="#e8e8e8", fg_body="#aaaaaa",
        divider="#333333",
    )
    THEME_LIGHT = dict(
        bg="#fafafa", border="#1c1c1c",
        fg_title="#111111", fg_body="#555555",
        divider="#dddddd",
    )

    def __init__(self, title: str, body: str, dark_mode: bool = True, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint,
        )
        self.setObjectName("help_root")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(280)

        theme = self.THEME_DARK if dark_mode else self.THEME_LIGHT
        self.setStyleSheet(self._BASE.format(**theme))

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 13)
        root.setSpacing(0)

        # título
        lbl_title = QLabel(title)
        lbl_title.setProperty("role", "title")
        root.addWidget(lbl_title)
        root.addSpacing(8)

        # divisor
        div = QFrame()
        div.setObjectName("help_divider")
        div.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        div.setFixedHeight(1)
        root.addWidget(div)
        root.addSpacing(8)

        # corpo
        lbl_body = QLabel(body)
        lbl_body.setProperty("role", "body")
        lbl_body.setWordWrap(True)
        root.addWidget(lbl_body)

        self.adjustSize()

    def show_near(self, button: QPushButton) -> None:
        """Abre o popup abaixo e alinhado ao botão que o invocou."""
        pos = button.mapToGlobal(QPoint(0, button.height() + 4))
        self.move(pos)
        self.show()
        self.raise_()

    # def mousePressEvent(self, _) -> None:
    #     """Fecha ao clicar em qualquer lugar do popup."""
    #     self.hide()