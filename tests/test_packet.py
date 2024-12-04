import unittest
from models.packet import NetworkPacket

class TestNetworkPacket(unittest.TestCase):
    def test_packet_creation(self):
        packet = NetworkPacket(
            timestamp='2021-01-01T00:00:00',
            source_ip='192.168.1.1',
            destination_ip='192.168.1.2',
            protocol='TCP',
            length=100,
            info='Test packet',
            source_port=1234,
            destination_port=80
        )
        self.assertEqual(packet.timestamp, '2021-01-01T00:00:00')
        self.assertEqual(packet.source_ip, '192.168.1.1')
        self.assertEqual(packet.destination_ip, '192.168.1.2')
        self.assertEqual(packet.protocol, 'TCP')
        self.assertEqual(packet.length, 100)
        self.assertEqual(packet.info, 'Test packet')
        self.assertEqual(packet.source_port, 1234)
        self.assertEqual(packet.destination_port, 80)

    def test_from_pyshark_packet(self):
        # Mock a pyshark packet
        class MockLayer:
            srcport = '1234'
            dstport = '80'

        class MockPacket:
            sniff_time = '2021-01-01T00:00:00'
            ip = type('ip', (object,), {'src': '192.168.1.1', 'dst': '192.168.1.2'})
            highest_layer = 'TCP'
            length = '100'
            transport_layer = 'TCP'

            def __getitem__(self, item):
                return MockLayer()

        packet = NetworkPacket.from_pyshark_packet(MockPacket())
        self.assertIsNotNone(packet)
        self.assertEqual(packet.source_ip, '192.168.1.1')
        self.assertEqual(packet.destination_ip, '192.168.1.2')
        self.assertEqual(packet.protocol, 'TCP')
        self.assertEqual(packet.length, 100)
        self.assertEqual(packet.source_port, 1234)
        self.assertEqual(packet.destination_port, 80)

if __name__ == '__main__':
    unittest.main()
