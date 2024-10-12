from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

from src.backend.game import Board, Game, Piece, is_white
from src.backend.moves import Coord, is_coord
from src.const import ASSETS_DIR, BOARD_SIZE, MIN_WINDOW_SIZE


class PieceIcon(QtWidgets.QLabel):
    def __init__(self, parent: "BoardFrame", piece: Piece, coord: Coord) -> None:
        super().__init__(parent)

        player = "w" if is_white(piece) else "b"
        piece_fname = f"{player}{piece.lower()}"
        pixmap = QtGui.QPixmap(str(ASSETS_DIR / f"pieces/{piece_fname}.png"))
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.show()

        self.coord = coord
        self._parent = parent
        self.setMinimumSize(1, 1)

    def mousePressEvent(self, ev: QtGui.QMouseEvent | None) -> None:
        if ev is None:
            return

        if ev.button() != Qt.MouseButton.LeftButton:
            ev.ignore()
            return

        ev.accept()
        self._parent.process_click(self.coord)


class Field(QtWidgets.QWidget):
    def __init__(self, parent: "BoardFrame", color: str, coord: Coord) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)
        self._parent = parent
        self.coord = coord
        self.setMinimumSize(1, 1)

    def mousePressEvent(self, ev: QtGui.QMouseEvent | None) -> None:
        if ev is None:
            return

        if ev.button() != Qt.MouseButton.LeftButton:
            ev.ignore()
            return

        ev.accept()
        self._parent.process_click(self.coord)


class BoardFrame(QtWidgets.QWidget):
    def __init__(self, board: Board) -> None:
        super().__init__()

        self.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QGridLayout()
        self._layout = layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.draw_background()

        self.piece_dict: dict[Coord, PieceIcon] = {}
        for coord, piece in board.get_all_pieces():
            piece_icon = PieceIcon(self, piece=piece, coord=coord)
            self.add_piece(piece_icon, coord=coord)

        self.selected_coord: Coord | None = None

    def draw_background(self) -> None:
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                color = "#F0D9B5" if (x + y) % 2 == 0 else "#B58863"
                coord = (x, y)
                assert is_coord(coord)
                field = Field(self, color=color, coord=coord)
                self._layout.addWidget(field, x, y)

            self._layout.setColumnStretch(x, 1)
            self._layout.setRowStretch(x, 1)

    def add_piece(self, piece: PieceIcon, coord: Coord) -> None:
        piece.coord = coord
        self._layout.addWidget(piece, *coord)
        self.piece_dict[coord] = piece

    def remove_piece(self, coord: Coord) -> None:
        piece = self.piece_dict.pop(coord)
        self._layout.removeWidget(piece)

    def move_piece(self, start: Coord, end: Coord) -> None:
        start_piece = self.piece_dict[start]
        if end in self.piece_dict:
            self.remove_piece(end)

        self.remove_piece(start)
        self.add_piece(start_piece, coord=end)

    def process_click(self, clicked_coord: Coord) -> None:
        if self.selected_coord is None:
            if clicked_coord in self.piece_dict:
                self.selected_coord = clicked_coord
            return
        self.move_piece(start=self.selected_coord, end=clicked_coord)
        self.selected_coord = None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        game = Game()
        board = BoardFrame(game.board)
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
