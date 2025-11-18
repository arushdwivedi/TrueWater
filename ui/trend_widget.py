# ui/trend_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from PySide6.QtGui import QPixmap

class TrendWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.plot_label = QLabel()
        self.plot_label.setFixedHeight(220)
        self.plot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.history_text)
        self.layout.addWidget(self.plot_label)
        self.setLayout(self.layout)

    def render(self, rows):
        # rows: list of tuples from DB: (id, testId, testNumber, dateOfTest, sampleImagePath, algaeContent)
        lines = []
        totals = []
        for r in rows:
            tnum = r[2]
            date = r[3]
            content = r[5]
            try:
                import json
                parsed = json.loads(content)
                total = parsed.get("total_count", 0)
            except Exception:
                total = 0
            lines.append(f"Test #{tnum} ({date[:19]}): total={total}")
            totals.append(total)
        self.history_text.setText("\n".join(lines))

        if totals:
            fig, ax = plt.subplots(figsize=(6, 2.5))
            ax.plot(range(1, len(totals)+1), totals, marker="o")
            ax.set_xlabel("Test #")
            ax.set_ylabel("Total detected")
            fig.tight_layout()
            tmp = "data/_trend_tmp.png"
            os.makedirs("data", exist_ok=True)
            fig.savefig(tmp)
            plt.close(fig)
            if os.path.exists(tmp):
                pix = QPixmap(tmp)
                self.plot_label.setPixmap(pix.scaled(self.plot_label.width(), self.plot_label.height()))
        else:
            self.plot_label.clear()
