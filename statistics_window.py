from datetime import date, timedelta

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PySide6.QtCore import Qt

from translation import get
from database import fetch_cards, fetch_decks


class StatisticsWindow(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

        self.setWindowTitle(get("statistics"))
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.total_cards_label = QLabel()
        self.total_decks_label = QLabel()
        self.due_today_label = QLabel()

        layout.addWidget(self.total_cards_label)
        layout.addWidget(self.total_decks_label)
        layout.addWidget(self.due_today_label)

        layout.addWidget(QLabel(get("review_last_seven_days")))
        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(200)
        layout.addWidget(self.chart_view)

    def showEvent(self, event):
        self.load_stats()
        super().showEvent(event)

    def load_stats(self):
        cards = fetch_cards(self.connection)
        decks = fetch_decks(self.connection)
        today = date.today().isoformat()

        due_count = sum(1 for card in cards if card["next_review"] <= today)

        self.total_cards_label.setText(f"{get("total_cards")}: {len(cards)}")
        self.total_decks_label.setText(f"{get("total_decks")}: {len(decks)}")
        self.due_today_label.setText(f"{get("cards_due_today")}: {due_count}")

        self.load_chart()

    def load_chart(self):
        query = """
            SELECT review_date, COUNT(*) FROM review_history
            WHERE review_date >= date('now', '-6 days')
            GROUP BY review_date
            ORDER BY review_date
        """
        rows = self.connection.execute(query).fetchall()
        review_counts = {row[0]: row[1] for row in rows}

        days = []
        counts = []
        for i in range(6, -1, -1):
            day = date.today() - timedelta(days=i)
            days.append(day.strftime("%m/%d"))
            counts.append(review_counts.get(day.isoformat(), 0))

        bar_set = QBarSet(get("reviews"))
        for count in counts:
            bar_set.append(count)

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setVisible(False)

        x_axis = QBarCategoryAxis()
        x_axis.append(days)
        chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(x_axis)

        y_axis = QValueAxis()
        y_axis.setRange(0, max(counts, default=1) + 1)
        y_axis.setLabelFormat("%d")
        chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(y_axis)

        self.chart_view.setChart(chart)
