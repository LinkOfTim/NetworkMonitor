from dataclasses import dataclass
from typing import Optional

@dataclass
class NetworkPacket:
    timestamp: str
    source_ip: str
    destination_ip: str
    protocol: str
    length: int
    info: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None

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
            source_port = int(packet[packet.transport_layer].srcport)
            destination_port = int(packet[packet.transport_layer].dstport)
        except (AttributeError, KeyError):
            source_port = None
            destination_port = None

        try:
            return NetworkPacket(
                timestamp=str(packet.sniff_time),
                source_ip=packet.ip.src,
                destination_ip=packet.ip.dst,
                protocol=packet.highest_layer,
                length=int(packet.length),
                info=str(packet),
                source_port=source_port,
                destination_port=destination_port
            )
        except AttributeError:
            # Обработка случаев, когда информация отсутствует
            return None
