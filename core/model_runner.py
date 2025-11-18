from PySide6.QtCore import QThread, Signal
from ultralytics import YOLO
from PIL import Image

class ModelRunner(QThread):
    finished_signal = Signal(dict)

    def __init__(self, model_path, conf=0.25):
        super().__init__()
        self.model_path = model_path
        self._model = None
        self._image_path = None
        self.conf = conf

    def load_model(self):
        self._model = YOLO(self.model_path)

    def analyze(self, image_path):
        self._image_path = image_path
        if not self.isRunning():
            self.start()

    def run(self):
        try:
            if self._model is None:
                self.load_model()
        except Exception as e:
            self.finished_signal.emit({"status": "error", "message": f"Model load failed: {e}"})
            return

        try:
            img = Image.open(self._image_path).convert("RGB")
            results = self._model(img, conf=self.conf)
            res = results[0]
            names = res.names

            try:
                cls_list = res.boxes.cls.tolist()
            except Exception:
                cls_list = [int(c) for c in getattr(res.boxes, "cls", [])]

            counts = {}
            for c in cls_list:
                counts[c] = counts.get(c, 0) + 1

            detailed = []
            total = 0
            for ci, cnt in counts.items():
                detailed.append({"algaeName": names[int(ci)], "count": cnt})
                total += cnt

            self.finished_signal.emit({
                "status": "success",
                "total_count": total,
                "detailed_counts": detailed
            })
        except Exception as e:
            self.finished_signal.emit({"status": "error", "message": str(e)})
