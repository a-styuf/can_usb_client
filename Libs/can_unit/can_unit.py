from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QKeySequence, QShortcut
import Libs.can_unit.can_unit_widget as can_unit_widget
import Libs.NorbyFrameParser.norby_data as norby_data



class Widget(QtWidgets.QFrame, can_unit_widget.Ui_Frame):

    action_signal = QtCore.pyqtSignal([list])

    def __init__(self, parent, **kw):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__(parent)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        # инициаллизация МКО #
        self.num = 0
        self.name = "..."
        for key in sorted(kw):
            if key == "interface":
                self.interface = kw.pop(key)
            elif key == "num":
                self.num = kw.pop(key)
            elif key == "name":
                self.name = kw.pop(key)
            else:
                pass
        # конфигурация
        self.cfg_dict = {"name": "ADCS TMI2",
                         "channel_num": "0",
                         "dev_id": "4",
                         "var_id": "5",
                         "offset": "40",
                         "length": "128",
                         "data": " ".join(["0" for i in range(128)]),
                         "mode": "read",
                         }
        self.state = 0
        self.action_state = 0
        self.bus_state = 0
        self.channel_num = 0
        self.dev_id = 0
        self.var_id = 0
        self.offset = 0
        self.length = 0
        self.mode = "read"
        self.data = [0]
        self.table_data = [["Нет данных", ""]]
        #
        self.total_cnt = 1
        self.aw_err_cnt = 0
        self.time_out = 0
        #
        self.load_cfg()
        #
        self.numLabel.setText("%d" % self.num)
        self.actionPButton.clicked.connect(self.action)
        #
        self.request_timer = QtCore.QTimer()
        self.request_timer.timeout.connect(self.set_data_to_unit)

        self.shortcut_Ctrl_Space = QShortcut(QKeySequence('Ctrl+Space'), self)
        self.shortcut_Ctrl_Space.activated.connect(self.action)
        self.shortcut_Ctrl_Space.setContext(QtCore.Qt.ShortcutContext.WidgetWithChildrenShortcut)

    def set_num(self, n):
        self.num = n
        self.numLabel.setText("%d" % self.num)

    def load_cfg(self, cfg_dict=None):
        if cfg_dict:
            self.cfg_dict = cfg_dict
        #
        self.name = self.cfg_dict.get("name", "NA")
        self.nameLine.setText(self.name)
        #
        self.channel_num = self.cfg_dict.get("channel_num", "0")
        self.CANChanNUMSBox.setValue(int(self.channel_num))
        #
        self.dev_id = self.cfg_dict.get("dev_id", "1")
        self.devIDSBox.setValue(int(self.dev_id))
        #
        self.var_id = self.cfg_dict.get("var_id", "0")
        self.varIDSBox.setValue(int(self.var_id))
        #
        self.offset = self.cfg_dict.get("offset", "0")
        self.offsetSBox.setValue(int(self.offset))
        #
        self.length = self.cfg_dict.get("length", "0")
        self.lengthSBox.setValue(int(self.length))
        #
        data = self.cfg_dict.get("data", "00").split(" ")
        self.data = [int(var, 16) for var in data]
        self.insert_data(self.data)
        #
        self.action_state = 0 if self.cfg_dict.get("mode", "read") in "read" else 1
        if self.action_state == 0:
            self.modeBox.setCurrentText("Чтение")
        else:
            self.modeBox.setCurrentText("Запись")

    def get_cfg(self):
        self.name = self.nameLine.text()
        self.cfg_dict["name"] = self.name
        #
        self.channel_num = self.CANChanNUMSBox.value()
        self.cfg_dict["dev_id"] = "%d" % self.channel_num
        #
        self.dev_id = self.devIDSBox.value()
        self.cfg_dict["dev_id"] = "%d" % self.dev_id
        #
        self.var_id = self.varIDSBox.value()
        self.cfg_dict["var_id"] = "%d" % self.var_id
        #
        self.offset = self.offsetSBox.value()
        self.cfg_dict["offset"] = "%d" % self.offset
        #
        self.length = self.lengthSBox.value()
        self.cfg_dict["length"] = "%d" % self.length
        #
        self.cfg_dict["mode"] = "read" if self.modeBox.currentText() in "Чтение" else "write"
        #
        self.get_data()
        if self.modeBox.currentText() == "Чтение":
            pass
        else:
            self.cfg_dict["data"] = " ".join(["%02X" % var for var in self.data])
        return self.cfg_dict

    def write(self):
        try:
            if self.interface.is_open:
                parameters = self.get_action_parameters()
                self.interface.request(**parameters)
                self.state = 0
            else:
                self.state = 2
            self.action_signal.emit([])
            self.state_check()
        except Exception as error:
            print("can_unit: write :", error)
        pass

    def read(self):
        if self.interface.is_open:
            self.actionPButton.setEnabled(False)
            parameters = self.get_action_parameters()
            self.interface.request(**parameters)
            self.request_timer.singleShot(150, self.set_data_to_unit)
            self.time_out = 5
            self.state = 0
        else:
            self.state = 2
        self.state_check()
        pass

    def get_action_mode(self):
        if self.modeBox.currentText() in "Чтение":
            return "read"
        else:
            return "write"

    def get_action_parameters(self):
        self.channel_num = int(self.CANChanNUMSBox.value())
        self.dev_id = int(self.devIDSBox.value())
        self.var_id = int(self.varIDSBox.value())
        self.offset = int(self.offsetSBox.value())
        self.length = int(self.lengthSBox.value())
        self.mode = self.get_action_mode()
        self.data = self.get_data_bytes(int(self.lengthSBox.value()))
        return {"can_num": self.channel_num, "dev_id": self.dev_id,
                "mode": self.mode, "var_id": self.var_id,
                "offset": self.offset, "d_len":self.length,
                "data": self.data}

    def check_id_var(self, id_var):
        res1, rtr, res2, offset, var_id, dev_id = self.interface.process_id_var(id_var)
        if dev_id == self.dev_id and var_id == self.var_id and offset == self.offset:
            return True
        return False

    def set_data_to_unit(self):
        self.total_cnt += 1
        self.time_out -= 1
        if self.time_out > 0:
            self.request_timer.singleShot(50, self.set_data_to_unit)
            id_var, data = self.interface.get_last_data()
            self.idVarLine.setText("0x{:02X}".format(id_var))
            if self.check_id_var(id_var):
                if self.mode in "read":  # read
                    self.insert_data(data)
                self.state = 0
                self.get_data()
                self.table_data = norby_data.frame_parcer(self.data)
                # при приеме инициируем сигнал, который запустит отображение таблицы данных
                try:
                    self.action_signal.emit(self.table_data)
                except TypeError:
                    pass
                self.actionPButton.setEnabled(True)
                self.state_check()
                self.time_out = 0
            else:
                self.state = 1
                self.request_timer.singleShot(50, self.set_data_to_unit)
        else:
            self.actionPButton.setEnabled(True)
            self.state = 1
        pass

    def action(self):
        if self.modeBox.currentText() in "Чтение":  # read
            self.read()
            self.table_data = norby_data.frame_parcer(self.data)
        else:
            self.write()
        pass

    def state_check(self):
        if self.state == 1:
            self.statusLabel.setText("CAN-USB")
            self.statusLabel.setStyleSheet('QLabel {background-color: orangered;}')
        elif self.state == 2:
            self.statusLabel.setText("Подключение")
            self.statusLabel.setStyleSheet('QLabel {background-color: coral;}')
        elif self.state == 0:
            self.statusLabel.setText("Норма")
            self.statusLabel.setStyleSheet('QLabel {background-color: seagreen;}')
        pass

    def connect(self):
        # todo обдумать возможность использования данной функции
        return self.state

    def insert_data(self, data):
        for row in range(self.dataTable.rowCount()):
            for column in range(self.dataTable.columnCount()):
                try:
                    table_item = QtWidgets.QTableWidgetItem("%02X" % data[row*(self.dataTable.columnCount()) + column])
                except (IndexError, TypeError):
                    table_item = QtWidgets.QTableWidgetItem(" ")
                self.dataTable.setItem(row, column, table_item)
        pass

    def get_data(self):
        data = []
        for row in range(self.dataTable.rowCount()):
            for column in range(self.dataTable.columnCount()):
                try:
                    data.append(int(self.dataTable.item(row, column).text(), 16))
                except ValueError:
                    data.append(0)
        self.data = data
        return self.data

    def get_data_bytes(self, length):
        data = []
        data_words = self.get_data()
        for var in data_words:
            data.append((var >> 0) & 0xFF)
        return data[:length]