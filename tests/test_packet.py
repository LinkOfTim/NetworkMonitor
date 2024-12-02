import unittest
from models.packet import NetworkPacket

class TestNetworkPacket(unittest.TestCase):
    def test_packet_creation(self):
        packet = NetworkPacket(
            timestamp='2021-01-01T00:00:00',
            source_ip='192.168.1.1',
            destination_ip='192.168.1.2',
            protocol='HTTP',
            length=1500,
            info='Test packet'
        )
        self.assertEqual(packet.source_ip, '192.168.1.1')
        self.assertEqual(packet.protocol, 'HTTP')

if __name__ == '__main__':
    unittest.main()
