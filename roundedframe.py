from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QPainter, QBrush, QColor, QPainterPath, QLinearGradient, QPalette
from PySide6.QtCore import Qt, QRectF

class RoundedFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # IMPORTANTE: Não force TranslucentBackground se quer a cor padrão
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Cores de estado (None significa que usaremos a cor padrão do sistema)
        self._custom_start = None
        self._custom_end = None
        self._custom_border = None

    def set_status_colors(self, start=None, end=None, border=None):
        """Define cores customizadas ou volta ao padrão se os argumentos forem None"""
        self._custom_start = QColor(start) if start else None
        self._custom_end = QColor(end) if end else None
        self._custom_border = QColor(border) if border else None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = 0

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # Lógica de Cores:
        if self._custom_start:
            # Se definimos cores (Modo New/Edit), usa o gradiente verde
            gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            gradient.setColorAt(0, self._custom_start)
            gradient.setColorAt(1, self._custom_end)
            brush = QBrush(gradient)
            border_color = self._custom_border
        else:
            # SENÃO, pega a cor de fundo padrão da janela (Window)
            bg_color = self.palette().color(QPalette.ColorRole.Window)
            brush = QBrush(bg_color)
            # Borda discreta padrão do sistema
            border_color = self.palette().color(QPalette.ColorRole.Mid)

        # Desenha o fundo
        painter.fillPath(path, brush)

        # Desenha a borda
        pen = painter.pen()
        pen.setColor(border_color)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawPath(path)