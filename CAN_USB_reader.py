import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QKeySequence, QShortcut
import configparser
import os
import time

import Libs.usb_can_bridge.usb_can_bridge as usb_can_bridge
from Libs.can_unit.can_unit import Widget
import UI.can_usb_bridge_client_widget as can_usb_bridge_client_widget
import UI.can_usb_bridge_client_win as can_usb_bridge_client_win

class Widgets(QtWidgets.QVBoxLayout):
    action = QtCore.pyqtSignal([list])

    def __init__(self, parent, **kw):
        super().__init__(parent)
        for key in sorted(kw):
            if key == "interface":
                self.interface = kw.pop(key)
        self.parent = parent
        self.unit_list = []
        #
        self.total_cnt = 1
        self.aw_err_cnt = 0
        #
        self.setContentsMargins(5, 5, 0, 0)
        pass

    def add_unit(self):
        widget_to_add = Widget(self.parent, num=len(self.unit_list), interface=self.interface)
        self.unit_list.append(widget_to_add)
        self.addWidget(widget_to_add)
        widget_to_add.action_signal.connect(self.multi_action)
        pass

    def multi_action(self, table_data):
        sender = self.sender()
        #
        self.aw_err_cnt += sender.aw_err_cnt
        self.total_cnt += sender.total_cnt
        #
        self.action.emit(table_data)

    def delete_unit_by_num(self, n):
        try:
            widget_to_dlt = self.unit_list.pop(n)
            widget_to_dlt.deleteLater()
            # self.unit_layout.removeWidget(widget_to_dlt)
            for i in range(len(self.unit_list)):
                self.unit_list[i].set_num(i)
        except IndexError:
            pass
        self.update()
        pass

    def delete_all_units(self):
        for i in range(self.count()):
            self.itemAt(0).widget().close()
            self.takeAt(0)
        self.unit_list = []
        pass

    def redraw(self):
        self.update()
        pass

    def get_cfg(self, config):
        for i in range(len(self.unit_list)):
            cfg_dict = self.unit_list[i].get_cfg()
            config["Unit %d" % i] = cfg_dict
        return config

    def load_cfg(self, config):
        units_cfg = config.sections()
        self.delete_all_units()
        for i in range(len(units_cfg)):
            if "Unit" in units_cfg[i]:
                self.add_unit()
                self.unit_list[-1].load_cfg(config[units_cfg[i]])
        return config


class ClientGUIWindow(QtWidgets.QFrame, can_usb_bridge_client_widget.Ui_Form):
    def __init__(self, parent, **kw):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__(parent)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        #
        self.interface = None
        self.serial_number = "000000000000"
        for key in sorted(kw):
            if key == "interface":
                self.interface = kw.pop(key)
        #
        self.config = None
        #
        if self.interface is None:
            self.interface = usb_can_bridge.MyUSBCANDevice(serial_numbers=[], debug=True)
            self.connectionPButton.clicked.connect(self.connect)
        else:
            self.connectionPButton.hide()
            self.devIDLEdit.hide()
        # контейнеры для вставки юнитов
        self.units_widgets = Widgets(self.unitsSArea, interface=self.interface)
        self.units_widgets.action.connect(self.data_table_slot)
        self.setLayout(self.units_widgets)

        # привязка сигналов к кнопкам
        #
        self.addUnitPButton.clicked.connect(self.units_widgets.add_unit)
        self.dltUnitPButt.clicked.connect(self.dlt_unit)
        self.dltAllUnitsPButt.clicked.connect(self.units_widgets.delete_all_units)
        #
        self.loadCfgPButt.clicked.connect(self.load_cfg)
        self.saveCfgPButt.clicked.connect(self.save_cfg)
        # таймер для работы с циклами опросов
        self.cycleTimer = QtCore.QTimer()
        self.cycleTimer.timeout.connect(self.start_request_cycle)
        self.cycle_step_count = 0
        self.cycleStartPButton.clicked.connect(lambda: self.cycleTimer.start(1000))
        self.cycleStopPButton.clicked.connect(self.stop_request_cycle)

        #
        self.load_init_cfg()
        self.interface.serial_numbers.append(self.serial_number)
        # LOG-s files
        self.can_log_file = None
        self.serial_log_file = None
        self.recreate_log_files()
        # timers for different purpose
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.update_data)
        self.updateTimer.start(1000)

        self.shortcut_Ctrl_K = QShortcut(QKeySequence('Ctrl+K'), self)
        self.shortcut_Ctrl_K.activated.connect(self.connect)
        
    def update_data(self):
        # log_files
        for log_str in self.interface.get_can_log():
            self.can_log_file.write(log_str + "\n")
        for log_str in self.interface.get_serial_log():
            self.serial_log_file.write(log_str + "\n")
        # state check
        self.connectionPButton.setText(self.interface.state_check()[0])
        self.connectionPButton.setStyleSheet('QPushButton {background-color: %s;}' % (self.interface.state_check()[1]))
        pass

    def connect(self):
        self.serial_number = self.devIDLEdit.text()
        self.interface.serial_numbers = [self.serial_number]
        self.interface.reconnect()
        pass

    def start_request_cycle(self):
        period = self.cycleIntervalSBox_3.value()
        self.cycleTimer.setInterval(int(period * 1000))
        #
        unit_num = len(self.units_widgets.unit_list)
        if self.cycle_step_count == 0:
            self.cycle_step_count = self.cycleNumSBox_3.value() * unit_num
            return
        else:
            self.cycle_step_count -= 1
            # print("%04X" % self.kpa.mko_aw)
            if self.cycle_step_count == 0:
                self.stop_request_cycle()
        elapsed_time = period * self.cycle_step_count
        self.cycleElapsedTimeEdit.setTime(QtCore.QTime(0, 0).addSecs(int(elapsed_time)))
        #
        self.units_widgets.unit_list[(unit_num - 1) - (self.cycle_step_count % unit_num)].action()
        #
        try:
            self.cyclePrBar.setValue(int(100 - ((100 * self.cycle_step_count) / (self.cycleNumSBox_3.value() * unit_num))))
        except ValueError:
            self.cyclePrBar.setValue(100)
        pass

    def stop_request_cycle(self):
        self.cyclePrBar.setValue(0)
        self.cycleTimer.stop()
        self.cycle_step_count = 0
        self.cycleElapsedTimeEdit.setTime(QtCore.QTime(0, 0))
        pass

    def data_table_slot(self, table_data):
        # на всякий пожарный сохраняем текущую конфигурацию
        self.save_init_cfg()
        #
        if table_data:
            self.dataTWidget.setRowCount(len(table_data))
            for row in range(len(table_data)):
                for column in range(self.dataTWidget.columnCount()):
                    try:
                        table_item = QtWidgets.QTableWidgetItem(table_data[row][column])
                        self.dataTWidget.setItem(row, column, table_item)
                    except IndexError:
                        pass
        pass

    def dlt_unit(self):
        n = self.dltUnitNumSBox.value()
        self.units_widgets.delete_unit_by_num(n)
        pass

    def load_init_cfg(self):
        self.config = configparser.ConfigParser()
        file_name = "CAN-USB_init.cfg"
        self.config.read(file_name)
        if self.config.sections():
            self.units_widgets.load_cfg(self.config)
        else:
            self.units_widgets.add_unit()
        try:
            self.serial_number = self.config["usb_can bridge device"]["id"]
            self.devIDLEdit.setText(self.config["usb_can bridge device"]["id"])
        except KeyError as error:
            print(error)
        pass

    def save_init_cfg(self):
        self.config = configparser.ConfigParser()
        self.config = self.units_widgets.get_cfg(self.config)
        self.config["usb_can bridge device"] = {"id": self.devIDLEdit.text()}
        file_name = "CAN-USB_init.cfg"
        try:
            with open(file_name, 'w') as configfile:
                self.config.write(configfile)
        except FileNotFoundError:
            pass
        pass

    def load_cfg(self):
        config = configparser.ConfigParser()
        home_dir = os.getcwd()
        try:
            os.mkdir(home_dir + "\\CAN-USB_Config")
        except OSError as error:
            pass
        file_name = QtWidgets.QFileDialog.getOpenFileName(self,
                                                          "Открыть файл конфигурации",
                                                          home_dir + "\\CAN-USB_Config",
                                                          r"config(*.cfg);;All Files(*)")[0]
        config.read(file_name)
        try:
            self.interface.serial_numbers.append(config["usb_can bridge device"]["id"])
            self.devIDLEdit.setText(config["usb_can bridge device"]["id"])
        except KeyError as error:
            pass
        self.units_widgets.load_cfg(config)
        pass

    def save_cfg(self):
        home_dir = os.getcwd()
        config = configparser.ConfigParser()
        config = self.units_widgets.get_cfg(config)
        config["usb_can bridge device"] = {"id": self.devIDLEdit.text()}
        try:
            os.mkdir(home_dir + "\\CAN-USB_Config")
        except OSError:
            pass
        file_name = QtWidgets.QFileDialog.getSaveFileName(self,
                                                          "Сохранить файл конфигурации",
                                                          home_dir + "\\CAN-USB_Config",
                                                          r"config(*.cfg);;All Files(*)")[0]
        try:
            configfile = open(file_name, 'w')
            config.write(configfile)
            configfile.close()
        except FileNotFoundError as error:
            pass
        pass

    # LOGs #
    @staticmethod
    def create_log_file(file=None, prefix="", dir_prefix="", extension=".txt"):
        dir_name = "Logs"
        sub_dir_name = dir_name + "\\" + time.strftime("%Y_%m_%d ", time.localtime()) + dir_prefix
        sub_sub_dir_name = sub_dir_name + "\\" + time.strftime("%Y_%m_%d %H-%M-%S ",
                                                               time.localtime()) + dir_prefix
        try:
            os.makedirs(sub_sub_dir_name)
        except (OSError, AttributeError) as error:
            pass
        try:
            if file:
                file.close()
        except (OSError, NameError, AttributeError) as error:
            pass
        file_name = sub_sub_dir_name + "\\" + time.strftime("%Y_%m_%d %H-%M-%S ",
                                                            time.localtime()) + dir_prefix + " " + prefix + extension
        file = open(file_name, 'a')
        return file

    @staticmethod
    def close_log_file(file=None):
        if file:
            try:
                file.close()
            except (OSError, NameError, AttributeError) as error:
                pass
        pass

    def recreate_log_files(self):
        self.can_log_file = self.create_log_file(prefix="can", dir_prefix="CAN-USB_bridge")
        self.serial_log_file = self.create_log_file(prefix="serial", dir_prefix="CAN-USB_bridge")
        pass

    def closeEvent(self, event):
        self.close_log_file(self.serial_log_file)
        self.close_log_file(self.can_log_file)


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем

    class MainWindow(QtWidgets.QMainWindow, can_usb_bridge_client_win.Ui_MainWindow):
        def __init__(self):
            # Это здесь нужно для доступа к переменным, методам
            # и т.д. в файле design.py
            #
            super().__init__()
            self.setupUi(self)  # Это нужно для инициализации нашего дизайна
            #
            self.can_usb_client_widget = ClientGUIWindow(self)
            self.gridLayout.addWidget(self.can_usb_client_widget, 0, 0, 1, 1)

        def closeEvent(self, event):
            self.can_usb_client_widget.save_init_cfg()
            pass

    # QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # os.environ["QT_SCALE_FACTOR"] = "1.0"
    #
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()
    app.exec()  # и запускаем приложение