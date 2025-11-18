# gui_app.py
from PySide6.QtWidgets import QApplication
import sys
import os


# ensure we run from project root so relative assets/data paths work
if getattr(sys, 'frozen', False):
# if packaged
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)


from ui.main_window import MainWindow




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())




if __name__ == '__main__':
    main()