from models.packet import NetworkPacket
from PyQt5.QtCore import QObject, pyqtSignal
import time

class AlertManager(QObject):
    alert_generated = pyqtSignal(str)  # Сигнал для передачи оповещений в интерфейс

    def __init__(self):
        super().__init__()
        # Словарь для отслеживания активности IP-адресов
        self.ip_activity = {}

    def check_packet(self, packet: NetworkPacket):
        """
        Проверяет пакет на соответствие правилам угроз и генерирует оповещения.
        Args:
            packet (NetworkPacket): Захваченный пакет.
        """
        self.detect_port_scan(packet)
        self.detect_ddos(packet)
        self.detect_unusual_packet_size(packet)

    def detect_port_scan(self, packet: NetworkPacket):
        """
        Обнаружение сканирования портов.
        """
        src_ip = packet.source_ip
        current_time = time.time()

        # Инициализация записи для IP, если необходимо
        if src_ip not in self.ip_activity:
            self.ip_activity[src_ip] = {}

        ip_data = self.ip_activity[src_ip]

        # Инициализация ключей 'ports' и 'timestamps' для сканирования портов
        ip_data.setdefault('ports', set())
        ip_data.setdefault('port_scan_timestamps', [])

        # Добавление порта назначения в список
        if hasattr(packet, 'destination_port') and packet.destination_port:
            ip_data['ports'].add(packet.destination_port)
        ip_data['port_scan_timestamps'].append(current_time)

        # Очистка старых записей
        ip_data['port_scan_timestamps'] = [t for t in ip_data['port_scan_timestamps'] if current_time - t < 10]

        # Если за последние 10 секунд было подключение к более чем 10 различным портам
        if len(ip_data['ports']) > 10:
            alert_msg = f"Обнаружено сканирование портов с IP {src_ip}"
            self.alert_generated.emit(alert_msg)
            # Сброс данных для этого IP
            ip_data['ports'].clear()
            ip_data['port_scan_timestamps'].clear()

    def detect_ddos(self, packet: NetworkPacket):
        """
        Обнаружение DDoS-атаки.
        """
        src_ip = packet.source_ip
        current_time = time.time()

        # Инициализация записи для IP, если необходимо
        if src_ip not in self.ip_activity:
            self.ip_activity[src_ip] = {}

        ip_data = self.ip_activity[src_ip]

        # Инициализация ключей 'packet_count' и 'ddos_timestamps' для DDoS
        ip_data.setdefault('packet_count', 0)
        ip_data.setdefault('ddos_timestamps', [])

        ip_data['ddos_timestamps'].append(current_time)

        # Очистка старых записей
        ip_data['ddos_timestamps'] = [t for t in ip_data['ddos_timestamps'] if current_time - t < 5]
        ip_data['packet_count'] = len(ip_data['ddos_timestamps'])

        # Если за последние 5 секунд от IP пришло более 100 пакетов
        if ip_data['packet_count'] > 100:
            alert_msg = f"Обнаружена возможная DDoS-атака с IP {src_ip}"
            self.alert_generated.emit(alert_msg)
            # Сброс данных для этого IP
            ip_data['packet_count'] = 0
            ip_data['ddos_timestamps'].clear()

    def detect_unusual_packet_size(self, packet: NetworkPacket):
        """
        Обнаружение пакетов с необычным размером.
        """
        # Например, если размер пакета превышает 1500 байт
        if packet.length > 1500:
            alert_msg = f"Обнаружен большой пакет ({packet.length} байт) от {packet.source_ip}"
            self.alert_generated.emit(alert_msg)
