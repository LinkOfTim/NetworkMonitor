# python -m unittest tests/test_alert_manager.py

import unittest
from utils.alerts import AlertManager
from models.packet import NetworkPacket
import time

class TestAlertManager(unittest.TestCase):
    
    def test_detect_port_scan(self):
        alert_manager = AlertManager()
        self.received_message = None

        def mock_slot(message):
            self.received_message = message

        alert_manager.alert_generated.connect(mock_slot)  # Подключаем слот
        
        src_ip = '192.168.1.100'
        
        # Симулируем пакеты к разным портам
        for port in range(1, 12):  # Больше 10 портов для срабатывания
            packet = NetworkPacket(
                timestamp=str(time.time()),
                source_ip=src_ip,
                destination_ip='192.168.1.1',
                protocol='TCP',
                length=60,
                info='Test packet',
                destination_port=port
            )
            alert_manager.check_packet(packet)
        
        # Проверяем, было ли сгенерировано оповещение
        self.assertEqual(self.received_message, f"Обнаружено сканирование портов с IP {src_ip}")

    def test_detect_ddos(self):
        alert_manager = AlertManager()

        self.received_message = None

        def mock_slot(message):
            self.received_message = message

        alert_manager.alert_generated.connect(mock_slot)  # Подключаем слот
        
        src_ip = '192.168.1.100'
        current_time = time.time()
        
        # Симулируем 101 пакет от одного IP за короткое время
        for _ in range(101):
            packet = NetworkPacket(
                timestamp=str(current_time),
                source_ip=src_ip,
                destination_ip='192.168.1.1',
                protocol='TCP',
                length=60,
                info='Test packet'
            )
            alert_manager.check_packet(packet)
        
        # Проверяем, было ли сгенерировано оповещение
        self.assertEqual(self.received_message, f"Обнаружена возможная DDoS-атака с IP {src_ip}")

    def test_detect_unusual_packet_size(self):
        alert_manager = AlertManager()

        self.received_message = None

        def mock_slot(message):
            self.received_message = message

        alert_manager.alert_generated.connect(mock_slot)  # Подключаем слот
        
        src_ip = '192.168.1.100'
        
        # Симулируем пакет размером больше 1500 байт
        packet = NetworkPacket(
            timestamp=str(time.time()),
            source_ip=src_ip,
            destination_ip='192.168.1.1',
            protocol='TCP',
            length=2000,
            info='Test packet'
        )
        alert_manager.check_packet(packet)
        
        # Проверяем, было ли сгенерировано оповещение
        self.assertEqual(self.received_message, f"Обнаружен большой пакет (2000 байт) от {src_ip}")
