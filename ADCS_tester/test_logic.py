import threading
import time

from PyQt5 import QtWidgets, QtGui
from UI import test_unit_widget
from test_classes import *


class TestWidget(QtWidgets.QFrame, test_unit_widget.Ui_testUnitFrame):
    def __init__(self, parent, interface, can_lock, dev_id, can_num):
        super().__init__(parent)
        self.setupUi(self)

        self.dev_id = dev_id
        self.can_num = can_num
        self.interface = interface

        font = QtGui.QFont()
        font.setPointSize(10)
        self.testLogTEdit.setFont(font)

        self.CAN_thread = threading.Thread(target=self.thread_func, args=(), daemon=True)
        self.CAN_lock = can_lock
        self.data_lock = threading.Lock()
        self.running_event = threading.Event()

        self.read_repeat = repeat_count
        self.data = {}

        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.update_data)
        self.testLaunchPButton.clicked.connect(self.on_test_launch_clicked)

        self.test_list = [FWTester(self.dev_id),
                          SSAddrTester(self.dev_id),
                          SSLineTester(self.dev_id),
                          CurSensTester(self.dev_id),
                          CamGNSSTester(self.dev_id)]

        self.CAN_thread.start()

        pass

    def set_can_num(self, can_num):
        self.can_num = can_num

    def update_data(self):
        # with self.data_lock:
        #     data = self.data
        # for info_label in self.info_labels:
        #     if info_label.name in data:
        #         info_label.set_data(data[info_label.name])
        pass

    def on_test_launch_clicked(self):
        self.running_event.set()
        pass

    def thread_func(self):
        while True:
            self.running_event.wait()
            for tst in self.test_list:

                with self.CAN_lock:
                    if self.interface.is_open:
                        tst.exec(self.interface, self.can_num)
                        ret, log = tst.get_result()

                        self.testLogTEdit.append(ret)
                    else:
                        print("READER: CAN not open")
                        # todo: IMPLEMENT
                        pass
                time.sleep(next_test_offset)
            self.running_event.clear()

