import sys

from PyQt6 import QtWidgets

from src.frontend.app import MainWindow


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
