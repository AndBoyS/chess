from enum import IntEnum
from typing import Iterator, Literal, get_args

from src.backend.moves import Coord, get_possible_moves
from src.const import BOARD_SIZE

WhitePiece = Literal["P", "N", "B", "R", "Q", "K"]
BlackPiece = Literal["p", "n", "b", "r", "q", "k"]
Piece = WhitePiece | BlackPiece


class Board:
    def __init__(self) -> None:
        self._board: dict[Coord, Piece] = {}
        white_row: list[Piece] = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        black_row: list[Piece] = ["r", "n", "b", "q", "k", "b", "n", "r"]

        for y, (w_piece, b_piece) in enumerate(zip(white_row, black_row)):
            self._board[(BOARD_SIZE - 1, y)] = w_piece  # type: ignore[index]
            self._board[(0, y)] = b_piece  # type: ignore[index]
            self._board[(BOARD_SIZE - 2, y)] = "P"  # type: ignore[index]
            self._board[(1, y)] = "p"  # type: ignore[index]

    def __getitem__(self, coord: Coord) -> Piece:
        return self._board[coord]

    def __setitem__(self, coord: Coord, piece: Piece) -> None:
        self._board[coord] = piece

    def get(self, coord: Coord) -> Piece | None:
        return self._board.get(coord)

    def pop(self, coord: Coord) -> Piece:
        return self._board.pop(coord)

    def move_piece(self, start: Coord, end: Coord) -> None:
        piece = self.get(start)
        if piece is None:
            raise ValueError("INVALID_MOVE")

        self.pop(start)
        self[end] = piece

    def get_all_pieces(self) -> Iterator[tuple[Coord, Piece]]:
        yield from self._board.items()


def is_white(piece: Piece) -> bool:
    return piece in get_args(WhitePiece)


class Player(IntEnum):
    WHITE = 0
    BLACK = 1

    @property
    def is_white(self) -> bool:
        return self == Player.WHITE


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.current_player = Player.WHITE
        self.is_finished = False

    def switch_player(self) -> None:
        if self.current_player == Player.WHITE:
            self.current_player = Player.BLACK
        else:
            self.current_player = Player.WHITE

    def make_turn(self, start: Coord, end: Coord) -> None:
        player = self.current_player
        piece = self.board.get(start)
        if piece is None or is_white(piece) != (player == Player.WHITE):
            raise ValueError("INVALID_MOVE")

        possible_moves = get_possible_moves(
            piece=piece,
            board=self.board,
            start=start,
            player=player,
        )
        if end not in possible_moves:
            raise ValueError("INVALID_MOVE")

        piece_to_replace = self.board.get(end)

        if piece_to_replace is not None and piece_to_replace.lower() == "k":
            raise ValueError("INVALID_MOVE")

        self.board.move_piece(start=start, end=end)
        self.switch_player()

    def get_possible_moves(self, coord: Coord) -> list[Coord]:
        piece = self.board.get(coord)
        if piece is None:
            return []
        return get_possible_moves(piece=piece, board=self.board, start=coord, player=self.current_player)

    def is_piece_friendly(self, coord: Coord) -> bool | None:
        piece = self.board.get(coord)
        if piece is None:
            return None
        return is_white(piece) == (self.current_player == Player.WHITE)
