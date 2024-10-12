from pathlib import Path


REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "assets"
MIN_WINDOW_SIZE = (300, 300)
FILES = "abcdefgh"
FILE_TO_I = {c: i for i, c in enumerate(FILES)}
BOARD_SIZE = 8
