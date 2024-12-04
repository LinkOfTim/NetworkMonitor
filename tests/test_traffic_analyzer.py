import unittest
from models.traffic_analyzer import TrafficAnalyzer
from models.packet import NetworkPacket

class TestTrafficAnalyzer(unittest.TestCase):
    def test_analyze_packet(self):
        analyzer = TrafficAnalyzer()

        packet = NetworkPacket(
            timestamp='2021-01-01T00:00:00',
            source_ip='192.168.1.1',
            destination_ip='192.168.1.2',
            protocol='HTTP',
            length=500,
            info='Test packet'
        )

        analyzer.analyze_packet(packet)
        self.assertEqual(analyzer.packet_count, 1)
        self.assertEqual(analyzer.total_bytes, 500)
        self.assertEqual(analyzer.protocol_distribution, {'HTTP': 1})

        # Analyze another packet
        packet.protocol = 'TCP'
        packet.length = 1000
        analyzer.analyze_packet(packet)
        self.assertEqual(analyzer.packet_count, 2)
        self.assertEqual(analyzer.total_bytes, 1500)
        self.assertEqual(analyzer.protocol_distribution, {'HTTP': 1, 'TCP': 1})

if __name__ == '__main__':
    unittest.main()
