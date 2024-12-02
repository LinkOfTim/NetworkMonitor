class TrafficAnalyzer:
    """
    Класс для анализа сетевого трафика. Отслеживает общее количество пакетов,
    общий объем данных (в байтах) и распределение пакетов по протоколам.
    """
    def __init__(self):
        """
        Инициализирует начальные значения статистики трафика:
        - packet_count: общее количество пакетов.
        - total_bytes: общее количество байтов данных.
        - protocol_distribution: распределение пакетов по протоколам.
        """
        self.packet_count = 0
        self.total_bytes = 0
        self.protocol_distribution = {}

    def analyze_packet(self, packet):
        """
        Анализирует пакет и обновляет статистику.

        Args:
            packet (NetworkPacket): Захваченный пакет.
        """
        self.packet_count += 1
        self.total_bytes += packet.length

        protocol = packet.protocol
        if protocol in self.protocol_distribution:
            self.protocol_distribution[protocol] += 1
        else:
            self.protocol_distribution[protocol] = 1
