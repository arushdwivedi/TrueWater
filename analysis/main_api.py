# analysis/main_api.py
from ultralytics import YOLO
from PIL import Image

class AnalysisAPI:
    def __init__(self, model_path, conf=0.25):
        self.model = YOLO(model_path)
        self.conf = conf

    def run(self, image_path):
        img = Image.open(image_path).convert("RGB")
        res = self.model(img, conf=self.conf)[0]
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
        return {"status": "success", "total_count": total, "detailed_counts": detailed}
