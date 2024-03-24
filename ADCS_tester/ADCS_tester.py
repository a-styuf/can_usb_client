import sys

from can_unit import Widget
import usb_can_bridge
import configparser

from can_unit import ClientGUIWindow
from UI import ADCS_tester_widget, ADCS_tester_win
from data_logic import *
from test_logic import *
from EF_RW_logic import *

from defines import *




class ADCSClientGUI(QtWidgets.QFrame, ADCS_tester_widget.Ui_Form):
    def __init__(self, parent, **kw):
        super().__init__(parent)
        self.setupUi(self)

        self.can_num = self.CANChanNUMSBox.value()
        self.dev_id = std_dev_id
        self.can_lock = threading.Lock()

        self.interface = None
        self.serial_number = "000000000000"
        for key in sorted(kw):
            if key == "interface":
                self.interface = kw.pop(key)

        self.config = None

        if self.interface is None:
            self.interface = usb_can_bridge.MyUSBCANDevice(serial_numbers=[], debug=True)
            self.connectionPButton.clicked.connect(self.connect)
        else:
            self.connectionPButton.hide()
            self.devIDLEdit.hide()

        self.can_log_file = None
        self.serial_log_file = None
        self.recreate_log_files()

        self.interface.serial_numbers.append(self.serial_number)
        self.load_init_cfg()

        self.canUnitWidget = Widget(self.canUnitFrame, interface=self.interface)
        self.canUnitWidget.dev_id = self.dev_id
        self.canUnitWidget.devIDSBox.setValue(self.dev_id)
        self.canUnitWidget.actionPButton.setEnabled(False)
        # self.canUnitWidget.line.hide()
        self.canUnitWidget.CANChanNUMSBox.setEnabled(False)
        self.canUnitWidget.CANChanNUMSBox.setValue(self.can_num)

        self.FWTimer = QtCore.QTimer()
        self.FWRdr = FWReader(self, ifs=self.interface, tmi=2, dev_id=self.dev_id)

        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.update_data)
        self.updateTimer.start(int(update_timer_interval*1000))

        self.dataWidget = DataWidget(self.dataUnitFrame, self.interface, self.can_lock,
                                     self.dev_id, self.can_num)
        self.dataWidget.cb_clicked.connect(self.on_data_cb_clicked)
        self.testWidget = TestWidget(self.testUnitFrame, self.interface,
                                     self.can_lock, self.dev_id, self.can_num)

        self.TMIWidget = TMIWidget(self.TMI_Frame, self.interface, self.can_lock,
                                    self.dev_id, self.can_num)

        self.CANChanNUMSBox.valueChanged.connect(self.on_can_num_clicked)

    def update_data(self):
        # log files
        for log_str in self.interface.get_can_log():
            self.can_log_file.write(log_str + "\n")
        for log_str in self.interface.get_serial_log():
            self.serial_log_file.write(log_str + "\n")

        # state check
        self.connectionPButton.setText(self.interface.state_check()[0])
        self.connectionPButton.setStyleSheet('QPushButton {background-color: %s;}' % (self.interface.state_check()[1]))

        if self.interface.state > 0 and not self.dataWidget.infoCB.isChecked():
            self.canUnitWidget.actionPButton.setEnabled(True)
        else:
            self.canUnitWidget.actionPButton.setEnabled(False)

    def load_init_cfg(self):
        self.config = configparser.ConfigParser()
        file_name = "../CAN-USB_init.cfg"
        self.config.read(file_name)
        try:
            self.serial_number = self.config["usb_can bridge device"]["id"]
            self.devIDLEdit.setText(self.config["usb_can bridge device"]["id"])
        except KeyError as error:
            print(error)
        pass

    def connect(self):
        self.dev_id = self.IDDEVSBox.value()
        self.FWRdr.set_id_dev(self.dev_id)
        self.dataWidget.set_id_dev(self.dev_id)
        self.testWidget.set_id_dev(self.dev_id)
        self.TMIWidget.set_id_dev(self.dev_id)

        self.canUnitWidget.dev_id = self.dev_id
        self.canUnitWidget.devIDSBox.setValue(self.dev_id)

        self.serial_number = self.devIDLEdit.text()
        self.interface.serial_numbers = [self.serial_number]
        self.interface.reconnect()

        self.FWRdr.acquire_data(self.CANChanNUMSBox.value())
        self.FWTimer.singleShot(150, lambda: self.FWFrameData.setText(self.FWRdr.get_data()))
        pass

    def on_can_num_clicked(self):
        self.can_num = self.CANChanNUMSBox.value()
        self.dataWidget.set_can_num(self.can_num)
        self.canUnitWidget.CANChanNUMSBox.setValue(self.can_num)

    def on_data_cb_clicked(self, checked):
        self.canUnitWidget.actionPButton.setEnabled(not checked)
        self.testWidget.testLaunchPButton.setEnabled(not checked)
        pass

    def recreate_log_files(self):
        self.can_log_file = ClientGUIWindow.create_log_file(prefix="can", dir_prefix="ADCS_tester")
        self.serial_log_file = ClientGUIWindow.create_log_file(prefix="serial", dir_prefix="ADCS_tester")
        pass

    def closeEvent(self, event):
        ClientGUIWindow.close_log_file(self.serial_log_file)
        ClientGUIWindow.close_log_file(self.can_log_file)
        self.dataWidget.CAN_thread.join()
        self.testWidget.CAN_thread.join()


if __name__ == '__main__':
    class MainWindow(QtWidgets.QMainWindow, ADCS_tester_win.Ui_MainWindow):
        def __init__(self):
            super().__init__()
            self.setupUi(self)
            self.can_usb_client_widget = ADCSClientGUI(self)
            self.gridLayout.addWidget(self.can_usb_client_widget, 0, 0, 1, 1)

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
