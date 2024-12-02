from dataclasses import dataclass

@dataclass
class NetworkPacket:
    timestamp: str
    source_ip: str
    destination_ip: str
    protocol: str
    length: int
    info: str

    @staticmethod
    def from_pyshark_packet(packet) -> 'NetworkPacket':
        """
        Создает объект NetworkPacket из пакета pyshark.

        Args:
            packet: Пакет pyshark.

        Returns:
            NetworkPacket
        """
        try:
            return NetworkPacket(
                timestamp=str(packet.sniff_time),
                source_ip=packet.ip.src,
                destination_ip=packet.ip.dst,
                protocol=packet.highest_layer,
                length=int(packet.length),
                info=str(packet)
            )
        except AttributeError:
            # Обработка случаев, когда информация отсутствует
            return None
