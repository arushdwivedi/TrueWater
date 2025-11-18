from PySide6.QtWidgets import QFileDialog




def pick_image(parent=None, title='Choose image'):
    path, _ = QFileDialog.getOpenFileName(parent, title, '', 'Images (*.png *.jpg *.jpeg *.bmp)')
    return path