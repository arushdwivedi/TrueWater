# ui/main_window.py
import os
import uuid
import datetime
import json
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QListWidgetItem, QMessageBox, QTabWidget
from PySide6.QtCore import Qt
from core.db import init_db, insert_sample, get_all_samples, get_samples_by_testId, get_latest_test_number, update_sample_content_by_path
from core.model_runner import ModelRunner
from core.utils import pil_to_qpixmap
from ui.dialogs import pick_image
from ui.results_widget import ResultsWidget
from ui.trend_widget import TrendWidget
from ui.history_widget import HistoryWidget
from PIL import Image

MODEL_PATH = os.path.join("assets", "best.pt")
REF_IMG = os.path.join("assets", "image.png")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrueWater — Offline Algae Analyzer")
        self.resize(1200, 720)
        init_db()

        self.model_runner = ModelRunner(MODEL_PATH)
        self.model_runner.finished_signal.connect(self.on_analysis_finished)

        self.current_testId = None
        self.current_sample_path = None

        # left sidebar
        self.history_widget = HistoryWidget()
        self.history_widget.list_widget.itemClicked.connect(self.on_history_item_clicked)

        # center/right area
        self.upload_btn = QPushButton("Upload Sample")
        self.upload_btn.clicked.connect(self.on_upload_clicked)
        self.retest_btn = QPushButton("Retest Sample")
        self.retest_btn.clicked.connect(self.on_retest_clicked)
        self.retest_btn.setEnabled(False)

        self.image_label = QLabel("No sample loaded")
        self.image_label.setFixedSize(480, 360)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.ref_label = QLabel("Reference")
        self.ref_label.setFixedSize(240, 180)
        self.ref_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(REF_IMG):
            try:
                pil = Image.open(REF_IMG)
                self.ref_label.setPixmap(pil_to_qpixmap(pil, max_w=240, max_h=180))
            except Exception:
                self.ref_label.setText("Reference (invalid)")

        self.results_widget = ResultsWidget()
        self.trend_widget = TrendWidget()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.results_widget, "Content")
        self.tabs.addTab(self.trend_widget, "History")

        controls = QHBoxLayout()
        controls.addWidget(self.upload_btn)
        controls.addWidget(self.retest_btn)
        controls.addStretch()

        images = QHBoxLayout()
        images.addWidget(self.image_label)
        images.addWidget(self.ref_label)

        right_layout = QVBoxLayout()
        right_layout.addLayout(controls)
        right_layout.addLayout(images)
        right_layout.addWidget(self.tabs)

        right_container = QWidget()
        right_container.setLayout(right_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.history_widget)
        main_layout.addWidget(right_container)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # populate initial
        self.refresh_history()

    def refresh_history(self):
        self.history_widget.refresh()

    def on_history_item_clicked(self, item: QListWidgetItem):
        testId = item.data(256)
        self.load_test_history(testId)

    def load_test_history(self, testId):
        rows = get_samples_by_testId(testId)
        if not rows:
            QMessageBox.information(self, "No records", "No records found for this sample.")
            return
        latest = rows[-1]
        _, testId, testNumber, dateOfTest, sampleImagePath, algaeContent = latest
        self.current_testId = testId
        self.retest_btn.setEnabled(True)
        if sampleImagePath and os.path.exists(sampleImagePath):
            try:
                pil = Image.open(sampleImagePath)
                self.image_label.setPixmap(pil_to_qpixmap(pil, max_w=480, max_h=360))
            except Exception:
                self.image_label.setText("Image invalid")
        else:
            self.image_label.setText("No image")

        try:
            parsed = json.loads(algaeContent)
            self.results_widget.populate(parsed)
        except Exception:
            self.results_widget.populate({"total_count": 0, "detailed_counts": []})

        # trend
        self.trend_widget.render(rows)

    def on_upload_clicked(self):
        file_path = pick_image(self, "Choose image")
        if not file_path:
            return
        testId = str(uuid.uuid4())[:8]
        testNumber = 1
        record = {
            "id": str(uuid.uuid4()),
            "testId": testId,
            "testNumber": testNumber,
            "dateOfTest": datetime.datetime.utcnow().isoformat(),
            "sampleImagePath": file_path,
            "algaeContent": json.dumps({"status": "pending"})
        }
        insert_sample(record)
        self.refresh_history()
        try:
            pil = Image.open(file_path)
            self.image_label.setPixmap(pil_to_qpixmap(pil, max_w=480, max_h=360))
        except Exception:
            self.image_label.setText("Image invalid")
        self.current_testId = testId
        self.current_sample_path = file_path
        self.retest_btn.setEnabled(True)
        self.results_widget.total_label.setText("Analyzing...")
        self.results_widget.table.setRowCount(0)
        self.model_runner.analyze(file_path)

    def on_retest_clicked(self):
        if not self.current_testId:
            QMessageBox.information(self, "No sample selected", "Select or upload a sample first.")
            return
        file_path = pick_image(self, "Choose new image for retest")
        if not file_path:
            return
        latest = get_latest_test_number(self.current_testId)
        new_num = (latest or 0) + 1
        record = {
            "id": str(uuid.uuid4()),
            "testId": self.current_testId,
            "testNumber": new_num,
            "dateOfTest": datetime.datetime.utcnow().isoformat(),
            "sampleImagePath": file_path,
            "algaeContent": json.dumps({"status": "pending"})
        }
        insert_sample(record)
        self.refresh_history()
        self.current_sample_path = file_path
        try:
            pil = Image.open(file_path)
            self.image_label.setPixmap(pil_to_qpixmap(pil, max_w=480, max_h=360))
        except Exception:
            self.image_label.setText("Image invalid")
        self.results_widget.total_label.setText("Analyzing...")
        self.model_runner.analyze(file_path)

    def on_analysis_finished(self, result):
        if result.get("status") != "success":
            self.results_widget.total_label.setText("Analysis error")
            QMessageBox.warning(self, "Analysis error", str(result.get("message", "Unknown error")))
            update_sample_content_by_path(self.current_sample_path, json.dumps(result))
            return
        result["analyzedAt"] = datetime.datetime.utcnow().isoformat()
        update_sample_content_by_path(self.current_sample_path, json.dumps(result))
        self.results_widget.populate(result)
        self.refresh_history()
        if self.current_testId:
            self.load_test_history(self.current_testId)
