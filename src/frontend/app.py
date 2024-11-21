from enum import Enum
from functools import cache
from typing import Literal

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

from src.backend.game import Game, Piece, is_white
from src.backend.moves import Coord, is_coord
from src.const import ASSETS_DIR, BOARD_SIZE, MIN_WINDOW_SIZE


class BoardFrameDelegator:
    _parent: "BoardFrame"
    coord: Coord

    def mousePressEvent(self, ev: QtGui.QMouseEvent | None) -> None:
        if ev is None:
            return

        if ev.button() != Qt.MouseButton.LeftButton:
            ev.ignore()
            return

        ev.accept()
        self._parent.process_click(self.coord)


class PieceIcon(QtWidgets.QLabel, BoardFrameDelegator):
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


FieldColorType = Literal["default", "active", "moved_out"]


class FieldColor(Enum):
    DEFAULT1 = QtGui.QColor("#F0D9B5")
    DEFAULT2 = QtGui.QColor("#B58863")
    ACTIVE = QtGui.QColor("#9AFAAE")
    MOVED_OUT = QtGui.QColor("#a6bf7e")


def blend_colors(color1: QtGui.QColor, color2: QtGui.QColor) -> QtGui.QColor:
    color1_ratio = 0.25
    color2_ratio = 0.75
    return QtGui.QColor(
        int(color1_ratio * color1.red()) + int(color2_ratio * color2.red()),
        int(color1_ratio * color1.green()) + int(color2_ratio * color2.green()),
        int(color1_ratio * color1.blue()) + int(color2_ratio * color2.blue()),
        255,
    )


class Field(QtWidgets.QWidget, BoardFrameDelegator):
    def __init__(self, parent: "BoardFrame", color: QtGui.QColor, coord: Coord) -> None:
        super().__init__(parent)
        self.color_dict: dict[FieldColorType, QtGui.QColor] = {
            "default": color,
            "active": blend_colors(color, FieldColor.ACTIVE.value),
            # Color of field when piece has just left it
            "moved_out": blend_colors(color, FieldColor.MOVED_OUT.value),
        }
        self.default_color = color
        self.setAutoFillBackground(True)
        self.set_color("default")
        self._parent = parent
        self.coord = coord
        self.setMinimumSize(1, 1)

    def set_color(self, kind: FieldColorType) -> None:
        color = self.color_dict[kind]
        if kind != "default":
            print(color.red(), color.green(), color.blue(), color.alpha())
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)


@cache
def dot_pixmap() -> QtGui.QPixmap:
    return QtGui.QPixmap(str(ASSETS_DIR / "misc/dot.png"))


@cache
def circle_pixmap() -> QtGui.QPixmap:
    return QtGui.QPixmap(str(ASSETS_DIR / "misc/circle.png"))


class FieldHighlight(QtWidgets.QLabel, BoardFrameDelegator):
    def __init__(self, parent: "BoardFrame", coord: Coord) -> None:
        super().__init__(parent)

        self.setScaledContents(True)
        self.setMinimumSize(1, 1)
        self._parent = parent
        self.coord = coord

    def show_on_empty_field(self) -> None:
        self.setPixmap(dot_pixmap())
        self.show()

    def show_on_occupied_field(self) -> None:
        self.setPixmap(circle_pixmap())
        self.show()


class BoardFrame(QtWidgets.QWidget):
    def __init__(self, game: Game) -> None:
        super().__init__()

        self.game = game
        self.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QGridLayout()
        self._layout = layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.highlight_dict: dict[Coord, FieldHighlight] = {}
        self.visible_highlight: list[FieldHighlight] = []

        self.field_dict: dict[Coord, Field] = {}
        self.draw_background()

        self.piece_dict: dict[Coord, PieceIcon] = {}

        for coord, piece in game.board.get_all_pieces():
            piece_icon = PieceIcon(self, piece=piece, coord=coord)
            self.add_piece(piece_icon, coord=coord)

        self.selected_coord: Coord | None = None

        self.last_moved_in_field: Field | None = None
        self.last_moved_out_field: Field | None = None

    def draw_background(self) -> None:
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                color = FieldColor.DEFAULT1.value if (x + y) % 2 == 0 else FieldColor.DEFAULT2.value
                coord = (x, y)
                assert is_coord(coord)
                field = Field(self, color=color, coord=coord)
                self.field_dict[coord] = field
                self._layout.addWidget(field, x, y)

                highlight = FieldHighlight(parent=self, coord=coord)
                self.highlight_dict[coord] = highlight
                self._layout.addWidget(highlight, *coord)

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
        try:
            self.game.make_turn(start=start, end=end)
        except ValueError:
            return
        start_piece = self.piece_dict[start]
        if end in self.piece_dict:
            self.remove_piece(end)

        self.remove_piece(start)
        self.add_piece(start_piece, coord=end)

        self.hide_possible_moves()
        self.selected_coord = None
        if self.last_moved_in_field is not None:
            self.last_moved_in_field.set_color("default")

        self.last_moved_in_field = self.field_dict[end]
        self.last_moved_in_field.set_color("active")

        if self.last_moved_out_field is not None:
            self.last_moved_out_field.set_color("default")

        self.last_moved_out_field = self.field_dict[start]
        self.last_moved_out_field.set_color("moved_out")

    def select_piece(self, coord: Coord) -> None:
        self.hide_possible_moves()

        if self.selected_coord is not None:
            self.field_dict[self.selected_coord].set_color("default")
        moves = self.game.get_possible_moves(coord)
        if not moves:
            return
        if coord in self.piece_dict:
            self.selected_coord = coord
            self.field_dict[self.selected_coord].set_color("active")
        self.show_possible_moves(coord)

    def process_click(self, clicked_coord: Coord) -> None:
        is_piece_friendly = self.game.is_piece_friendly(clicked_coord)

        if self.selected_coord is None or is_piece_friendly:
            self.select_piece(clicked_coord)
        else:
            self.move_piece(start=self.selected_coord, end=clicked_coord)

    def show_possible_moves(self, coord: Coord) -> None:
        coords = self.game.get_possible_moves(coord)
        for coord in coords:
            highlight = self.highlight_dict[coord]
            if coord in self.piece_dict:
                highlight.show_on_occupied_field()
            else:
                highlight.show_on_empty_field()
            self.visible_highlight.append(highlight)

    def hide_possible_moves(self) -> None:
        for highlight in self.visible_highlight:
            highlight.hide()
        self.visible_highlight = []


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        game = Game()
        board = BoardFrame(game)
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
