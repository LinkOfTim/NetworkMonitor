from PyQt5 import QtWidgets, QtCore, QtGui
from controllers.capture_controller import CaptureController
from controllers.filter_controller import FilterController
from controllers.save_controller import SaveController
from models.packet import NetworkPacket
from models.traffic_analyzer import TrafficAnalyzer
from utils.alerts import AlertManager
from utils.network_interfaces import get_network_interfaces
from views.graphs import TrafficGraphs

class MainWindow(QtWidgets.QMainWindow):
    """
    Главное окно приложения для мониторинга сетевого трафика.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Network Traffic Monitor')

        # Контроллеры и вспомогательные классы
        self.capture_controller = None
        self.filter_controller = FilterController()
        self.traffic_analyzer = TrafficAnalyzer()
        self.alert_manager = AlertManager()
        self.save_controller = SaveController(self)

        # Сетевые интерфейсы
        self.available_interfaces = get_network_interfaces()
        self.selected_interface = None

        # Уникальные значения для фильтров
        self.unique_source_ips = set()
        self.unique_destination_ips = set()
        self.unique_protocols = set()

        # Буфер пакетов и таймер обновления
        self.packet_buffer = []
        self.update_timer = self.init_timer(1000, self.process_packet_buffer)

        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_timer(self, interval: int, callback: callable) -> QtCore.QTimer:
        """
        Создает и запускает таймер с заданным интервалом и функцией обратного вызова.

        Args:
            interval (int): Интервал таймера в миллисекундах.
            callback (callable): Функция, вызываемая при срабатывании таймера.

        Returns:
            QtCore.QTimer: Объект таймера.
        """
        timer = QtCore.QTimer()
        timer.setInterval(interval)
        timer.timeout.connect(callback)
        timer.start()
        return timer

    def init_ui(self):
        """
        Инициализирует пользовательский интерфейс приложения.
        """
        # Создание виджетов управления
        self.start_button = QtWidgets.QPushButton("Начать мониторинг")
        self.stop_button = QtWidgets.QPushButton("Остановить мониторинг")
        self.save_button = QtWidgets.QPushButton("Сохранить данные")

        # Выпадающий список для выбора интерфейса
        self.interface_selector = QtWidgets.QComboBox()
        self.interface_selector.addItems(self.available_interfaces)
        self.interface_selector.currentIndexChanged.connect(self.interface_changed)

        # Фильтры
        self.protocol_filter_combo = QtWidgets.QComboBox()
        self.protocol_filter_combo.addItem("Все протоколы")

        self.source_ip_filter_combo = QtWidgets.QComboBox()
        self.source_ip_filter_combo.addItem("Все источники")

        self.destination_ip_filter_combo = QtWidgets.QComboBox()
        self.destination_ip_filter_combo.addItem("Все назначения")

        self.apply_filter_button = QtWidgets.QPushButton("Применить фильтр")

        # Таблица для отображения пакетов
        self.packet_table = QtWidgets.QTableWidget()
        self.packet_table.setColumnCount(6)
        self.packet_table.setHorizontalHeaderLabels([
            "Время", "Источник", "Назначение", "Протокол", "Размер", "Примечание"
        ])
        self.packet_table.cellDoubleClicked.connect(self.display_packet_details)

        # Графики
        self.graphs = TrafficGraphs()

        # Расположение виджетов
        self.setup_layouts()

        # Подключение сигналов к слотам
        self.connect_signals()

    def setup_layouts(self):
        """
        Настраивает расположение виджетов в окне приложения.
        """
        main_layout = QtWidgets.QVBoxLayout()

        # Верхняя панель с кнопками и выбором интерфейса
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(QtWidgets.QLabel("Интерфейс:"))
        button_layout.addWidget(self.interface_selector)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.save_button)

        # Панель с фильтрами
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(QtWidgets.QLabel("Протокол:"))
        filter_layout.addWidget(self.protocol_filter_combo)
        filter_layout.addWidget(QtWidgets.QLabel("Источник:"))
        filter_layout.addWidget(self.source_ip_filter_combo)
        filter_layout.addWidget(QtWidgets.QLabel("Назначение:"))
        filter_layout.addWidget(self.destination_ip_filter_combo)
        filter_layout.addWidget(self.apply_filter_button)

        # Сборка основного макета
        main_layout.addLayout(button_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.packet_table)
        main_layout.addWidget(self.graphs)

        # Установка центрального виджета
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def connect_signals(self):
        """
        Подключает сигналы виджетов к соответствующим слотам.
        """
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.save_button.clicked.connect(self.save_controller.save_data)
        self.apply_filter_button.clicked.connect(self.apply_filter)

    def interface_changed(self, index: int):
        """
        Обработчик изменения выбранного сетевого интерфейса.

        Args:
            index (int): Индекс выбранного интерфейса.
        """
        self.selected_interface = self.available_interfaces[index]

    def start_monitoring(self):
        """
        Запускает мониторинг сетевого трафика на выбранном интерфейсе.
        """
        interface = self.selected_interface or self.available_interfaces[0]
        self.capture_controller = CaptureController(interface)
        self.capture_controller.packets_received.connect(self.update_data)
        self.capture_controller.start_capture()

        # Обновляем состояние кнопок и фильтров
        self.toggle_controls(monitoring=True)

    def stop_monitoring(self):
        """
        Останавливает мониторинг сетевого трафика.
        """
        if self.capture_controller:
            self.capture_controller.stop_capture()
            self.capture_controller = None

        # Обновляем состояние кнопок и фильтров
        self.toggle_controls(monitoring=False)

    def toggle_controls(self, monitoring: bool):
        """
        Включает или отключает элементы управления в зависимости от состояния мониторинга.

        Args:
            monitoring (bool): Флаг, указывающий, идет ли мониторинг.
        """
        self.start_button.setEnabled(not monitoring)
        self.stop_button.setEnabled(monitoring)
        self.interface_selector.setEnabled(not monitoring)
        self.protocol_filter_combo.setEnabled(not monitoring)
        self.source_ip_filter_combo.setEnabled(not monitoring)
        self.destination_ip_filter_combo.setEnabled(not monitoring)
        self.apply_filter_button.setEnabled(not monitoring)

    def apply_filter(self):
        """
        Применяет выбранные фильтры к отображаемым данным.
        """
        protocol = self.protocol_filter_combo.currentText()
        source_ip = self.source_ip_filter_combo.currentText()
        destination_ip = self.destination_ip_filter_combo.currentText()

        self.filter_controller.protocol_filter = protocol if protocol != "Все протоколы" else None
        self.filter_controller.source_ip_filter = source_ip if source_ip != "Все источники" else None
        self.filter_controller.destination_ip_filter = destination_ip if destination_ip != "Все назначения" else None

    def update_data(self, packets: NetworkPacket):
        """
        Получает новые пакеты от контроллера захвата и обновляет интерфейс.

        Args:
            packet (NetworkPacket): Захваченный сетевой пакет.
        """
        for packet in packets:
            # Обновляем уникальные значения для фильтров
            self.update_unique_values(packet)

            # Проверяем, проходит ли пакет через фильтры
            if not self.filter_controller.apply_filters(packet):
                return

            # Добавляем пакет в буфер для обработки
            self.packet_buffer.append(packet)

    def update_unique_values(self, packet: NetworkPacket):
        """
        Обновляет списки уникальных значений для фильтров на основе полученного пакета.

        Args:
            packet (NetworkPacket): Захваченный сетевой пакет.
        """
        # Обновление списка уникальных IP-адресов источников
        if packet.source_ip not in self.unique_source_ips:
            self.unique_source_ips.add(packet.source_ip)
            self.source_ip_filter_combo.addItem(packet.source_ip)

        # Обновление списка уникальных IP-адресов назначения
        if packet.destination_ip not in self.unique_destination_ips:
            self.unique_destination_ips.add(packet.destination_ip)
            self.destination_ip_filter_combo.addItem(packet.destination_ip)

        # Обновление списка уникальных протоколов
        if packet.protocol not in self.unique_protocols:
            self.unique_protocols.add(packet.protocol)
            self.protocol_filter_combo.addItem(packet.protocol)

    def process_packet_buffer(self):
        """
        Обрабатывает буфер накопленных пакетов и обновляет интерфейс.
        """
        if not self.packet_buffer:
            return

        self.packet_table.setSortingEnabled(False)  # Отключаем сортировку на время обновления

        for packet in self.packet_buffer:
            # Анализ пакета и проверка на угрозы
            self.traffic_analyzer.analyze_packet(packet)
            self.alert_manager.check_packet(packet)

            # Добавляем пакет в таблицу
            self.add_packet_to_table(packet)

        self.packet_table.setSortingEnabled(True)  # Включаем сортировку

        # Очищаем буфер и обновляем графики
        self.packet_buffer.clear()
        self.graphs.update_graphs(self.traffic_analyzer)

    def add_packet_to_table(self, packet: NetworkPacket):
        """
        Добавляет информацию о пакете в таблицу интерфейса.

        Args:
            packet (NetworkPacket): Захваченный сетевой пакет.
        """
        row_position = self.packet_table.rowCount()
        self.packet_table.insertRow(row_position)
        self.packet_table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(packet.timestamp))
        self.packet_table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(packet.source_ip))
        self.packet_table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(packet.destination_ip))
        self.packet_table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(packet.protocol))
        self.packet_table.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(packet.length)))
        self.packet_table.setItem(row_position, 5, QtWidgets.QTableWidgetItem(packet.info))

    def display_packet_details(self, row: int, column: int):
        """
        Отображает подробную информацию о пакете при двойном клике по строке таблицы.

        Args:
            row (int): Индекс строки.
            column (int): Индекс столбца.
        """
        packet_info = self.packet_table.item(row, 5).text()

        # Создаем диалоговое окно с информацией о пакете
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Информация о пакете")
        layout = QtWidgets.QVBoxLayout()
        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(packet_info)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.exec_()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Обработчик события закрытия окна. Останавливает захват пакетов перед выходом.

        Args:
            event (QtGui.QCloseEvent): Событие закрытия окна.
        """
        if self.capture_controller:
            self.capture_controller.stop_capture()
        event.accept()
