from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import threading
import pyshark
from models.packet import NetworkPacket
from collections import deque

class CaptureController(QObject):
    """
    Класс для управления захватом сетевых пакетов. Захватывает пакеты с указанного сетевого интерфейса
    в отдельном потоке и периодически отправляет их в виде сигнала.
    """
    packets_received = pyqtSignal(list)

    def __init__(self, interface: str):
        """
        Инициализирует контроллер захвата пакетов.

        Args:
            interface (str): Имя сетевого интерфейса для захвата пакетов.
        """
        super().__init__()
        self.interface = interface
        self.capture_thread = None
        self.running = False
        self.packet_queue = deque()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.emit_packets)

    def start_capture(self) -> None:
        """
        Запускает процесс захвата пакетов в отдельном потоке.
        """
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_packets, daemon=True)
        self.capture_thread.start()
        self.timer.start()

    def stop_capture(self) -> None:
        """
        Останавливает процесс захвата пакетов и останавливает таймер.
        """
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        self.timer.stop()

    def _capture_packets(self) -> None:
        """
        Захватывает пакеты с помощью библиотеки pyshark и сохраняет их в очередь.

        Преобразует захваченные пакеты в объект `NetworkPacket` для удобного использования.
        """
        try:
            capture = pyshark.LiveCapture(interface=self.interface)
            for packet in capture.sniff_continuously():
                if not self.running:
                    break
                network_packet = NetworkPacket.from_pyshark_packet(packet)
                if network_packet:
                    self.packet_queue.append(network_packet)
        except Exception as e:
            print(f"Ошибка при захвате пакетов: {e}")

    def emit_packets(self):
        """
        Извлекает захваченные пакеты из очереди и отправляет их через сигнал `packets_received`.
        """
        if self.packet_queue:
            packets = list(self.packet_queue)
            self.packet_queue.clear()
            self.packets_received.emit(packets)
