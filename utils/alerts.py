from models.packet import NetworkPacket
from PyQt5.QtWidgets import QMessageBox

class AlertManager:
    def check_packet(self, packet: NetworkPacket):
        # Пример простого правила обнаружения подозрительного трафика
        if packet.protocol == 'HTTP' and packet.length > 1000:
            self.show_alert(f"Большой HTTP пакет от {packet.source_ip}")

    def show_alert(self, message: str):
        alert = QMessageBox()
        alert.setWindowTitle('Оповещение')
        alert.setText(message)
        alert.exec_()
