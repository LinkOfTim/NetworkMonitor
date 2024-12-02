from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class TrafficGraphs(QtWidgets.QWidget):
    """
    Класс для отображения графиков трафика в приложении с переключением между линейным графиком
    и круговой диаграммой. Графики обновляются на основе данных сетевого анализатора.
    """
    def __init__(self):
        """
        Инициализирует графический интерфейс, включая холст для отображения графиков
        и кнопку для переключения типа графика.
        """
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.canvas)

        self.toggle_button = QtWidgets.QPushButton("Переключить график")
        self.toggle_button.clicked.connect(self.toggle_graph)
        self.layout.addWidget(self.toggle_button)

        self.current_graph = 'line'
        self.timestamps = []
        self.packet_counts = []
        self.protocol_distribution = {}

    def toggle_graph(self):
        """
        Переключает текущий тип графика между линейным графиком и круговой диаграммой.
        """
        if self.current_graph == 'line':
            self.current_graph = 'pie'
        else:
            self.current_graph = 'line'
        self.update_graphs()

    def update_graphs(self, analyzer=None):
        """
        Обновляет графики с учетом текущих данных.
        Если передан объект analyzer, извлекает из него данные для графиков.

        :param analyzer: объект анализатора, предоставляющий данные о трафике (необязательно)
        """
        if analyzer:
            self.timestamps.append(len(self.timestamps))
            self.packet_counts.append(analyzer.packet_count)
            self.protocol_distribution = analyzer.protocol_distribution.copy()

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if self.current_graph == 'line':
            if self.timestamps and self.packet_counts:
                ax.plot(self.timestamps, self.packet_counts, label='Объем трафика')
                ax.set_xlabel('Время')
                ax.set_ylabel('Количество пакетов')
                ax.legend()
            else:
                ax.text(0.5, 0.5, 'Нет данных для отображения', horizontalalignment='center', verticalalignment='center')
        elif self.current_graph == 'pie':
            protocols = list(self.protocol_distribution.keys())
            counts = list(self.protocol_distribution.values())
            if counts:
                ax.pie(counts, labels=protocols, autopct='%1.1f%%')
                ax.set_title('Распределение по протоколам')
            else:
                ax.text(0.5, 0.5, 'Нет данных для отображения', horizontalalignment='center', verticalalignment='center')

        self.canvas.draw()
