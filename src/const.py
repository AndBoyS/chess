from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
ASSETS_DIR = REPO_DIR / "assets"
MIN_WINDOW_SIZE = (300, 300)
# Reversed because first row in array corresponds to file h
FILES = "abcdefgh"[::-1]
BOARD_SIZE = 8
FILE_TO_I = {c: i for i, c in enumerate(FILES)}
