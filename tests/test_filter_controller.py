import unittest
from controllers.filter_controller import FilterController
from models.packet import NetworkPacket

class TestFilterController(unittest.TestCase):
    def test_apply_filters(self):
        filter_controller = FilterController()
        filter_controller.protocol_filter = 'TCP'
        filter_controller.source_ip_filter = '192.168.1.1'
        filter_controller.destination_ip_filter = '192.168.1.2'

        packet = NetworkPacket(
            timestamp='2021-01-01T00:00:00',
            source_ip='192.168.1.1',
            destination_ip='192.168.1.2',
            protocol='TCP',
            length=100,
            info='Test packet'
        )

        self.assertTrue(filter_controller.apply_filters(packet))

        # Test with non-matching protocol
        packet.protocol = 'UDP'
        self.assertFalse(filter_controller.apply_filters(packet))

        # Reset protocol filter
        filter_controller.protocol_filter = None
        self.assertTrue(filter_controller.apply_filters(packet))

if __name__ == '__main__':
    unittest.main()
