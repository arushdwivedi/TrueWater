# ui/history_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from core.db import get_all_samples

class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("<b>Samples history</b>"))
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

    def refresh(self):
        self.list_widget.clear()
        rows = get_all_samples()
        grouped = {}
        for r in rows:
            id_, testId, testNumber, dateOfTest, sampleImagePath, algaeContent = r
            if testId not in grouped:
                grouped[testId] = { 'latest_date': dateOfTest, 'latest_testNumber': testNumber }
            else:
                if dateOfTest > grouped[testId]['latest_date']:
                    grouped[testId]['latest_date'] = dateOfTest
                    grouped[testId]['latest_testNumber'] = testNumber

        items = sorted(grouped.items(), key=lambda x: x[1]['latest_date'], reverse=True)
        for testId, meta in items:
            item = QListWidgetItem(f"{testId} — test #{meta['latest_testNumber']} — {meta['latest_date'][:19]}")
            item.setData(256, testId)  # Qt.UserRole = 256
            self.list_widget.addItem(item)
