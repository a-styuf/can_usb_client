import threading
import time

from UI import data_unit_widget
from defines import *
from data_classes import *


class DataWidget(QtWidgets.QFrame, data_unit_widget.Ui_dataUnitFrame):
    cb_clicked = QtCore.pyqtSignal(bool)

    def __init__(self, parent, interface, can_lock, dev_id, can_num):
        super().__init__(parent)
        self.setupUi(self)

        self.dev_id = dev_id
        self.can_num = can_num
        self.interface = interface

        self.CAN_thread = threading.Thread(target=self.thread_func, args=(), daemon=True)
        self.CAN_lock = can_lock
        self.data_lock = threading.Lock()
        self.running_event = threading.Event()

        self.read_repeat = repeat_count
        self.data = {}

        self.info_labels = [GNSSValidReader(self.GNSSValidrame),
                            GNSSSecondsInfo(self.GNSSTimeFrame),
                            CoordInfo(self.GNSSCoordFrame),
                            ADCSTempInfo(self.TempFrame),
                            RebootCtr(self.RebootCtrFrame),
                            LocalTimeReader(self.LTimeFrame),
                            MagReader(self.MagAbsFrame),
                            MagVectReader(self.MagVecFrame),
                            AngVelReader(self.AngVelFrame),
                            AccelReader(self.AccelFrame)]

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)

        self.infoCB.clicked.connect(self.on_cb_clicked)

        self.CAN_thread.start()

        pass

    def set_id_dev(self, dev_id):
        self.dev_id = dev_id

    def set_can_num(self, can_num):
        self.can_num = can_num

    def update_data(self):
        with self.data_lock:
            data = self.data
        for info_label in self.info_labels:
            if info_label.name in data:
                info_label.set_data(data[info_label.name])

    def launch(self):
        # self.data_reader.start()
        self.running_event.set()
        self.timer.start(int(data_timer_interval*1000))

    def stop(self):
        # self.data_reader.stop()
        self.running_event.clear()
        self.timer.stop()
        pass

    def on_cb_clicked(self):
        self.cb_clicked.emit(self.infoCB.isChecked())
        if self.infoCB.isChecked():
            self.launch()
        else:
            self.stop()
        pass

    def thread_func(self):
        while True:
            self.running_event.wait()

            # for name, addr in self.addresses.items():
            for lbl in self.info_labels:
                if lbl.RunCB.isChecked():
                    with self.CAN_lock:
                        name = lbl.name
                        addr = address(lbl.var_id, lbl.offset, lbl.d_len)
                        if self.interface.is_open:

                            parameters = {"can_num": self.can_num,
                                          "dev_id": self.dev_id,
                                          "mode": "read",
                                          "var_id": addr.var_id,
                                          "offset": addr.offset,
                                          "d_len": addr.d_len}
                            self.interface.request(**parameters)
                            time.sleep(write_read_offset)

                            while True:
                                if self.read_repeat <= 0:
                                    print("READER: self.read_repeat <= 0")
                                    # Err. todo: IMPLEMENT
                                    break
                                    pass
                                self.read_repeat -= 1
                                id_var, data = self.interface.get_last_data()
                                if check_id_var(id_var, addr, self.dev_id):
                                    with self.data_lock:
                                        self.data[name] = data
                                    self.read_repeat = repeat_count
                                    break
                                time.sleep(read_read_offset)
                        else:
                            print("READER: CAN not open")
                            # todo: IMPLEMENT
                            pass
                    time.sleep(next_addr_offset)

