import norby_data
from UI import EF_RW_widget
from PyQt5 import QtCore, QtWidgets
import time
from defines import *
from norby_data import frame_parcer

status = ["UNKNOWN", "ST_IN_PROGRESS", "ST_SUCCESS_END",
          "ST_ERROR", "ST_ERROR_TIMEOUT", "ST_STOPPED"]
EF_STATUS = ["", "EF_IN_PROGRESS", "EF_SUCCESS_END", "EF_ERROR"]

settings_cmd = { 0x00 : "unknown",
                 0x01 : "rd mag",
                 0x02 : "rd gyr",
                 0x03 : "rd acc",
                 0x04 : "rd set",
                 0x11 : "wr mag",
                 0x12 : "wr gyr",
                 0x13 : "wr acc",
                 0x14 : "wr set"}


class TMIWidget(QtWidgets.QFrame, EF_RW_widget.Ui_EF_RW_Frame):

    def __init__(self, parent, interface, can_lock, dev_id, can_num):
        super().__init__(parent)
        self.setupUi(self)

        self.interface = interface
        self.can_lock = can_lock
        self.dev_id = dev_id
        self.can_num = can_num

        self.data = []
        self.table_data = [["Нет данных", ""]]

        self.launchPB.clicked.connect(self.on_launch_pb_clicked)
        self.statusRdPB.clicked.connect(self.on_get_status_pb_clicked)
        self.dataRdPB.clicked.connect(self.on_get_rd_data_pb_clicked)
        self.addrLE.returnPressed.connect(self.on_get_rd_data_pb_clicked)

        self.MoSetWrite.clicked.connect(self.on_mo_write)
        self.I2CSetWrite.clicked.connect(self.on_i2c_write)
        self.MTSetWrite.clicked.connect(self.on_mt_write)

        self.SettingsSavePB.clicked.connect(self.on_settings_save)

        self.CalibMagWrite.clicked.connect(self.on_mag_write)
        self.CalibGyroWrite.clicked.connect(self.on_gyro_write)
        self.CalibAccWrite.clicked.connect(self.on_acc_write)

        self.MagCalibSavePB.clicked.connect(self.on_mag_save)
        self.GyroCalibSavePB.clicked.connect(self.on_gyro_save)
        self.AccCalibSavePB.clicked.connect(self.on_acc_save)

        self.SetStatusPB.clicked.connect(self.on_set_get_status)

        self.MagCalRdPB.clicked.connect(self.on_mag_rd)
        self.GyrCalRDPB.clicked.connect(self.on_gyr_rd)
        self.AccCalRdPB.clicked.connect(self.on_acc_rd)
        self.MoSetRdPB.clicked.connect(self.on_MO_rd)
        self.I2CSetRdPb.clicked.connect(self.on_i2c_rd)
        self.MTSetRdPb.clicked.connect(self.on_MT_rd)

        self.rdTMIPB.clicked.connect(self.on_get_tmi_data_pb_clicked)

        self.read_repeat = repeat_count

    def on_launch_pb_clicked(self):
        parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 4, "offset": 78,
                      "d_len": 6, "data": [tmi_nums[int(self.TMINumCB.currentIndex())], 0,
                                           self.blockBegSBox.value(), self.blockLenSBox.value(),
                                           (self.delaySBox.value() >> 0) & 0xFF,
                                           (self.delaySBox.value() >> 8) & 0xFF]}

        if self.interface.is_open:
            with self.can_lock:
                self.interface.request(**parameters)

    def on_get_status_pb_clicked(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read", "var_id": 4,
                              "offset": 79, "d_len": 1}
                self.interface.request(**parameters)

                self.read_data(address(4, 79, 1))
                self.status_lbl.setText(status[int(self.data[0])])
            #
            # else:
            #     print("TMI: CAN not open")
            #     # todo: IMPLEMENT
            #     pass

    def on_get_rd_data_pb_clicked(self):
        with self.can_lock:
            if self.interface.is_open:

                addr = int(self.addrLE.text(), 16)
                data = [0x8B, (addr >> 0) & 0xFF,
                        (addr >> 8) & 0xFF, (addr >> 16) & 0xFF]
                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 8,
                              "offset": 0, "d_len": 4, "data": data}
                self.interface.request(**parameters)
                time.sleep(0.1)

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read", "var_id": 8,
                              "offset": 4, "d_len": 128}
                self.interface.request(**parameters)
                time.sleep(0.5)
                self.read_data(address(8, 4, 128))

                self.insert_data(self.data)
                self.table_data = frame_parcer(self.data)
                self.set_data_table()

    def on_get_tmi_data_pb_clicked(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read", "var_id": 5,
                              "offset": tmi_offs[int(self.rdTMINumCB.currentIndex())], "d_len": 128}
                self.interface.request(**parameters)
                time.sleep(0.5)
                self.read_data(address(5, tmi_offs[int(self.rdTMINumCB.currentIndex())], 128))

                self.insert_data(self.data)
                self.table_data = frame_parcer(self.data)
                self.set_data_table()

    def read_data(self, addr):
        while True:
            if self.read_repeat <= 0:
                print("READER: self.read_repeat <= 0")
                # Err. todo: IMPLEMENT
                break

            self.read_repeat -= 1
            id_var, data = self.interface.get_last_data()
            if check_id_var(id_var, addr):
                self.read_repeat = repeat_count
                self.data = data
                break
            time.sleep(read_read_offset)

    def insert_data(self, data):
        for row in range(self.dataTable.rowCount()):
            for column in range(self.dataTable.columnCount()):
                try:
                    table_item = QtWidgets.QTableWidgetItem("%02X" % data[row*(self.dataTable.columnCount()) + column])
                except (IndexError, TypeError):
                    table_item = QtWidgets.QTableWidgetItem(" ")
                self.dataTable.setItem(row, column, table_item)

    def set_data_table(self):
        if self.table_data is None:
            return

        self.dataTWidget.setRowCount(len(self.table_data))
        for row in range(len(self.table_data)):
            for column in range(self.dataTWidget.columnCount()):
                try:
                    table_item = QtWidgets.QTableWidgetItem(self.table_data[row][column])
                    self.dataTWidget.setItem(row, column, table_item)

                except IndexError:
                    pass


    def on_mo_write(self):
        with self.can_lock:
            if self.interface.is_open:
                try:
                    data = int(self.MOSetLEdit.text(), 16)
                    parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 7,
                                  "offset": 14,
                                  "d_len": 2, "data": [(data >> 0) & 0xFF, (data >> 8) & 0xFF]}

                    self.interface.request(**parameters)

                except Exception as error:
                    print(error)

    def on_i2c_write(self):
        with self.can_lock:
            if self.interface.is_open:
                try:
                    data = int(self.I2CSetLEdit.text(), 16)
                    parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 10,
                                  "offset": 9, "d_len": 1, "data": [(data >> 0) & 0xFF]}

                    self.interface.request(**parameters)

                except Exception as error:
                    print(error)

    def on_mt_write(self):
        with self.can_lock:
            if self.interface.is_open:
                try:
                    data = int(self.MTSetLEdit.text(), 16)
                    parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 9,
                                  "offset": 96, "d_len": 4,
                                  "data": [(data >> 0) & 0xFF,
                                           (data >> 8) & 0xFF,
                                           (data >> 16) & 0xFF,
                                           (data >> 24) & 0xFF]}

                    self.interface.request(**parameters)

                except Exception as error:
                    print(error)

    def on_set_get_status(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read", "var_id": 4,
                              "offset": 75, "d_len": 2}
                self.interface.request(**parameters)

                self.read_data(address(4, 75, 2))
                self.SetStatusLbl.setText(settings_cmd[self.data[1]] + " : " + EF_STATUS[int(self.data[0])])

    def on_settings_save(self):
        with self.can_lock:
            if self.interface.is_open:
                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 4,
                              "offset": 75, "d_len": 1,
                              "data": [0x14]}

                self.interface.request(**parameters)



    def on_mag_write(self):
        with self.can_lock:
            if self.interface.is_open:
                try:
                    data = int(self.MagCalibLEdit.text(), 16)
                    parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 11,
                                  "offset": 0,
                                  "d_len": 4, "data": [(data >> 0) & 0xFF,
                                                       (data >> 8) & 0xFF,
                                                       (data >> 16) & 0xFF,
                                                       (data >> 24) & 0xFF]}

                    self.interface.request(**parameters)

                except Exception as error:
                    print(error)

    def on_gyro_write(self):
        with self.can_lock:
            if self.interface.is_open:
                try:
                    data = int(self.GyroCalibLEdit.text(), 16)
                    parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 11,
                                  "offset": 576,
                                  "d_len": 4, "data": [(data >> 0) & 0xFF,
                                                       (data >> 8) & 0xFF,
                                                       (data >> 16) & 0xFF,
                                                       (data >> 24) & 0xFF]}
                    self.interface.request(**parameters)

                except Exception as error:
                    print(error)

    def on_acc_write(self):
        with self.can_lock:
            if self.interface.is_open:
                try:
                    data = int(self.AccCalibLEdit.text(), 16)
                    parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 11,
                                  "offset": 1152,
                                  "d_len": 4, "data": [(data >> 0) & 0xFF,
                                                       (data >> 8) & 0xFF,
                                                       (data >> 16) & 0xFF,
                                                       (data >> 24) & 0xFF]}
                    self.interface.request(**parameters)

                except Exception as error:
                    print(error)

    def on_mag_save(self):
        with self.can_lock:
            if self.interface.is_open:
                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 4,
                              "offset": 75, "d_len": 1,
                              "data": [0x11]}

                self.interface.request(**parameters)

    def on_gyro_save(self):
        with self.can_lock:
            if self.interface.is_open:
                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 4,
                              "offset": 75, "d_len": 1,
                              "data": [0x12]}

                self.interface.request(**parameters)

    def on_acc_save(self):
        with self.can_lock:
            if self.interface.is_open:
                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "write", "var_id": 4,
                              "offset": 75, "d_len": 1,
                              "data": [0x13]}

                self.interface.request(**parameters)

    def on_mag_rd(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read",
                              "var_id": 11, "offset": 0, "d_len": 4}
                self.interface.request(**parameters)

                self.read_data(address(11, 0, 4))
                data = int.from_bytes(self.data, byteorder="little")
                self.MagCurr.setText("0x%08X" % data)

    def on_gyr_rd(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read",
                              "var_id": 11, "offset": 576, "d_len": 4}
                self.interface.request(**parameters)

                self.read_data(address(11, 576, 4))
                data = int.from_bytes(self.data, byteorder="little")
                self.GyrCurr.setText("0x%08X" % data)

    def on_acc_rd(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read",
                              "var_id": 11, "offset": 1152, "d_len": 4}
                self.interface.request(**parameters)

                self.read_data(address(11, 1152, 4))
                data = int.from_bytes(self.data, byteorder="little")
                self.AccCurr.setText("0x%08X" % data)

    def on_MO_rd(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read",
                              "var_id": 7, "offset": 14, "d_len": 2}
                self.interface.request(**parameters)

                self.read_data(address(7, 14, 2))
                data = int.from_bytes(self.data, byteorder="little")
                self.MOCurr.setText("0x%04X" % data)

    def on_i2c_rd(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read",
                              "var_id": 10, "offset": 9, "d_len": 1}
                self.interface.request(**parameters)

                self.read_data(address(10, 9, 1))
                data = int.from_bytes(self.data, byteorder="little")
                self.I2CCurr.setText("0x%02X" % data)

    def on_MT_rd(self):
        with self.can_lock:
            if self.interface.is_open:

                parameters = {"can_num": self.can_num, "dev_id": self.dev_id, "mode": "read",
                              "var_id": 9, "offset": 96, "d_len": 4}
                self.interface.request(**parameters)

                self.read_data(address(9, 96, 4))
                data = int.from_bytes(self.data, byteorder="little")
                self.MtCurr.setText("0x%08X" % data)
