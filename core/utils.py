# core/utils.py
from PIL import Image
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt




def pil_to_qpixmap(pil_img, max_w=None, max_h=None):
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')
    data = pil_img.tobytes('raw', 'RGB')
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)
    pix = QPixmap.fromImage(qimg)
    if max_w or max_h:
        pix = pix.scaled(max_w or pix.width(), max_h or pix.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pix