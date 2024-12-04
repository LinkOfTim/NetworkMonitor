class FilterController:
    """
    Класс для управления фильтрами сетевых пакетов. 
    Позволяет применять фильтры по протоколу, IP-адресу отправителя и IP-адресу получателя.
    """
    def __init__(self):
        self.protocol_filter = None
        self.source_ip_filter = None
        self.destination_ip_filter = None

    def apply_filters(self, packet):
        """
        Проверяет, проходит ли пакет через фильтры.

        Args:
            packet (NetworkPacket): Захваченный пакет.

        Returns:
            bool: True, если пакет проходит фильтры.
        """
        if self.protocol_filter and packet.protocol != self.protocol_filter:
            return False
        if self.source_ip_filter and packet.source_ip != self.source_ip_filter:
            return False
        if self.destination_ip_filter and packet.destination_ip != self.destination_ip_filter:
            return False
        return True
