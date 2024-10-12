from typing import TYPE_CHECKING, Literal, TypeGuard


from src.const import BOARD_SIZE, FILE_TO_I, FILES


if TYPE_CHECKING:
    from src.backend.game import Board, Player, Piece


class Position(str):
    pass


def is_position(pos: str) -> TypeGuard[Position]:
    if len(pos) != 2:
        return False

    x = pos[0]
    y = pos[1]
    if x not in FILES or not y.isnumeric() or not (1 <= int(y) < BOARD_SIZE + 1):
        return False
    return True


CoordInt = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]
Coord = tuple[CoordInt, CoordInt]


def pos_to_coord(pos: Position) -> Coord:
    x = FILE_TO_I[pos[0]]
    y = int(pos[1]) - 1
    coord = x, y
    assert is_coord(coord)
    return coord


def coord_to_pos(coord: Coord) -> Position:
    pos = f"{FILES[coord[0]]}{coord[1]+1}"
    assert is_position(pos)
    return pos


def is_coord(coord: tuple[int, int]) -> TypeGuard[Coord]:
    return 0 <= coord[0] < BOARD_SIZE and 0 <= coord[1] < BOARD_SIZE


def get_trajectories(coord: Coord, kind: Literal["straight", "diag"]) -> list[list[Coord]]:
    from src.const import BOARD_SIZE

    direction_dict = {
        "straight": [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        ],
        "diag": [
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        ],
    }
    # how coordinates increment on each axis
    directions = direction_dict[kind]

    trajs: list[list[Coord]] = []

    x, y = coord

    for mul_x, mul_y in directions:
        traj: list[Coord] = []
        for i in range(1, BOARD_SIZE):
            offset_x = i * mul_x
            offset_y = i * mul_y

            new_coord = (x + offset_x, y + offset_y)
            if not is_coord(new_coord):
                break
            traj.append(new_coord)
        trajs.append(traj)
    return trajs


def get_moves(coord: Coord, kind: Literal["straight", "diag"]) -> list[Coord]:
    moves: set[Coord] = set()

    for traj in get_trajectories(coord, kind=kind):
        for end in traj:
            moves.add(end)

    return list(moves)


def get_paths(start: Coord, end: Coord, kind: Literal["straight", "diag"]) -> list[list[Coord]]:
    paths: list[list[Coord]] = []

    for traj in get_trajectories(start, kind=kind):
        path: list[Coord] = []
        for coord in traj:
            if coord == end:
                paths.append(path)
                break
            path.append(coord)

    return paths


def all_pawn_moves(player: "Player", board: "Board", coord: Coord) -> list[Coord]:
    from src.backend.game import is_white

    direction = 1 if player.is_white else -1
    x, y = coord

    possible_moves: list[Coord] = []

    # move forward
    new_coord = (x, y + direction)
    if is_coord(new_coord) and board.get(new_coord) is None:
        possible_moves.append(new_coord)

    # move diag
    new_coords = [
        (x - 1, y + direction),
        (x + 1, y + direction),
    ]

    for new_coord in new_coords:
        if not is_coord(new_coord):
            continue
        targeted_piece = board.get(new_coord)

        can_move_diag = targeted_piece is not None and is_white(targeted_piece) != player.is_white
        if can_move_diag:
            possible_moves.append(new_coord)

    # long move
    is_starting_coord = (y == 1 and player.is_white) or (y == BOARD_SIZE - 2 and not player.is_white)

    new_coord = (x, y + 2 * direction)
    if is_coord(new_coord) and is_starting_coord and board.get(new_coord) is None:
        possible_moves.append(new_coord)

    return possible_moves


def all_rook_moves(coord: Coord) -> list[Coord]:
    return get_moves(coord, kind="straight")


def all_knight_moves(coord: Coord) -> list[Coord]:
    moves: list[Coord] = []
    offsets = [
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
        (2, 1),
        (-2, 1),
        (2, -1),
        (-2, -1),
    ]

    x, y = coord
    for offset_x, offset_y in offsets:
        new_coord = (x + offset_x, y + offset_y)
        if is_coord(new_coord):
            moves.append(new_coord)

    return moves


def all_bishop_moves(coord: Coord) -> list[Coord]:
    return get_moves(coord, kind="diag")


def all_king_moves(coord: Coord) -> list[Coord]:
    moves: list[Coord] = []

    x, y = coord

    for offset_x in (-1, 0, -1):
        for offset_y in (-1, 0, -1):
            new_coord = (x + offset_x, y + offset_y)
            if not is_coord(new_coord) or new_coord == coord:
                continue

            moves.append(new_coord)

    return moves


def all_queen_moves(coord: Coord) -> list[Coord]:
    return get_moves(coord, kind="straight") + get_moves(coord, kind="diag")


def get_all_moves(piece: "Piece", coord: Coord, player: "Player", board: "Board") -> list[Coord]:
    if piece.lower() == "p":
        return all_pawn_moves(player=player, board=board, coord=coord)

    func_dict = {
        "n": all_knight_moves,
        "b": all_bishop_moves,
        "r": all_rook_moves,
        "q": all_queen_moves,
        "k": all_king_moves,
    }

    return func_dict[piece.lower()](coord)


def get_possible_moves(piece: "Piece", board: "Board", start: "Coord", player: "Player") -> list[Coord]:
    from src.backend.game import is_white, Player

    moves: list[Coord] = []

    if is_white(piece) != (player == Player.WHITE):
        return []

    all_moves = get_all_moves(piece=piece, board=board, coord=start, player=player)
    for end in all_moves:
        end_piece = board.get(end)
        if end_piece is not None and is_white(end_piece) == is_white(piece):
            continue

        paths = get_paths(start, end, kind="straight") + get_paths(start, end, kind="diag")

        for path in paths:
            is_path_free = True
            for temp_coord in path:
                if board.get(temp_coord) is not None:
                    is_path_free = False
                    break
            if is_path_free:
                break

        if (paths and is_path_free) or piece.lower() == "n":
            moves.append(end)

    return moves
