# ui/results_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem

class ResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        self.total_label = QLabel("Total detected: -")
        layout.addWidget(self.total_label)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Algae species", "Count"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def populate(self, result_json):
        total = result_json.get("total_count", 0)
        self.total_label.setText(f"Total detected: {total}")

        arr = result_json.get("detailed_counts", [])
        self.table.setRowCount(0)

        for i, r in enumerate(arr):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(r.get("algaeName", "-"))))
            self.table.setItem(i, 1, QTableWidgetItem(str(r.get("count", 0))))
