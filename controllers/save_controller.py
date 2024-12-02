import csv
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject

class SaveController(QObject):
    """
    Класс для сохранения данных из таблицы в файлы формата CSV или TXT.
    Обеспечивает взаимодействие с диалогом выбора файла и обработку данных таблицы.
    """
    def __init__(self, parent):
        """
        Инициализирует контроллер сохранения данных.

        Args:
            parent (QWidget): Родительский объект, содержащий таблицу для сохранения.
        """
        super().__init__()
        self.parent = parent

    def save_data(self):
        """
        Открывает диалоговое окно для выбора файла и сохраняет данные таблицы
        в выбранном формате (CSV или TXT).
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Сохранить данные",
            "",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)",
            options=options
        )
        if file_name:
            if file_name.endswith('.csv'):
                self.save_to_csv(file_name)
            elif file_name.endswith('.txt'):
                self.save_to_txt(file_name)
            else:
                self.save_to_csv(file_name + '.csv')

    def save_to_csv(self, file_name):
        """
        Сохраняет данные таблицы в файл формата CSV.

        Args:
            file_name (str): Полный путь к файлу для сохранения.
        """
        headers = [self.parent.packet_table.horizontalHeaderItem(i).text() for i in range(self.parent.packet_table.columnCount())]
        with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for row in range(self.parent.packet_table.rowCount()):
                row_data = []
                for column in range(self.parent.packet_table.columnCount()):
                    item = self.parent.packet_table.item(row, column)
                    row_data.append(item.text() if item else '')
                writer.writerow(row_data)

    def save_to_txt(self, file_name):
        """
        Сохраняет данные таблицы в файл формата TXT.

        Args:
            file_name (str): Полный путь к файлу для сохранения.
        """
        with open(file_name, 'w', encoding='utf-8') as txtfile:
            for row in range(self.parent.packet_table.rowCount()):
                row_data = []
                for column in range(self.parent.packet_table.columnCount()):
                    item = self.parent.packet_table.item(row, column)
                    row_data.append(item.text() if item else '')
                txtfile.write('\t'.join(row_data) + '\n')
