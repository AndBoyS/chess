import sys

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

from src.const import ASSETS_DIR, MIN_WINDOW_SIZE

Position = tuple[int, int]


class PieceIcon(QtWidgets.QLabel):
    def __init__(self, parent: "BoardFrame", piece: str, pos: Position) -> None:
        super().__init__(parent)

        pixmap = QtGui.QPixmap(str(ASSETS_DIR / f"pieces/{piece}.png"))
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.show()

        self.position = pos
        self._parent = parent
        self.setMinimumSize(1, 1)

    def mousePressEvent(self, ev: QtGui.QMouseEvent | None) -> None:
        if ev is None:
            return

        if ev.button() != Qt.MouseButton.LeftButton:
            ev.ignore()
            return

        ev.accept()
        self._parent.process_click(self.position)


class Field(QtWidgets.QWidget):
    def __init__(self, parent: "BoardFrame", color: str, pos: Position) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)
        self._parent = parent
        self.position = pos
        self.setMinimumSize(1, 1)

    def mousePressEvent(self, ev: QtGui.QMouseEvent | None) -> None:
        if ev is None:
            return

        if ev.button() != Qt.MouseButton.LeftButton:
            ev.ignore()
            return

        ev.accept()
        self._parent.process_click(self.position)


class BoardFrame(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.piece_dict: dict[Position, PieceIcon] = {}

        self.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QGridLayout()
        self._layout = layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        for x in range(8):
            for y in range(8):
                color = "#F0D9B5" if (x + y) % 2 == 0 else "#B58863"
                field = Field(self, color=color, pos=(x, y))
                layout.addWidget(field, x, y)

            layout.setColumnStretch(x, 1)
            layout.setRowStretch(x, 1)
        pos = (4, 3)
        piece = PieceIcon(self, piece="bk", pos=pos)
        self.add_piece(piece, pos=pos)

        self.selected_pos: Position | None = None

    def add_piece(self, piece: PieceIcon, pos: Position) -> None:
        piece.position = pos
        self._layout.addWidget(piece, *pos)
        self.piece_dict[pos] = piece

    def remove_piece(self, pos: Position) -> None:
        piece = self.piece_dict.pop(pos)
        self._layout.removeWidget(piece)

    def move_piece(self, start_pos: Position, end_pos: Position) -> None:
        start_piece = self.piece_dict[start_pos]
        if end_pos in self.piece_dict:
            self.remove_piece(end_pos)

        self.remove_piece(start_pos)
        self.add_piece(start_piece, pos=end_pos)

    def process_click(self, clicked_pos: Position) -> None:
        if self.selected_pos is None:
            if clicked_pos in self.piece_dict:
                self.selected_pos = clicked_pos
            return
        self.move_piece(start_pos=self.selected_pos, end_pos=clicked_pos)
        self.selected_pos = None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        board = BoardFrame()
        self.setCentralWidget(board)
        self.setMinimumSize(*MIN_WINDOW_SIZE)

    def resizeEvent(self, ev: QtGui.QResizeEvent | None) -> None:
        # Make window square
        if ev is None:
            return

        w, h = ev.size().width(), ev.size().height()
        if w > h:
            self.resize(h, h)
        else:
            self.resize(w, w)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
