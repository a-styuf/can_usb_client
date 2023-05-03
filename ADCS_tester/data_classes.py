from PyQt5 import QtWidgets, QtCore
from UI import ADCS_test_unit_widget
from defines import *

class SimpleCommunication(QtCore.QObject):
    def __init__(self, parent, **kw):
        super().__init__(parent)
        self.can_num = 0

        for key in sorted(kw):
            if key == "ifs":
                self.interface = kw.pop(key)
            elif key == "can_num":
                self.can_num = kw.pop(key)
            elif key == "dev_id":
                self.dev_id = kw.pop(key)
            elif key == "var_id":
                self.var_id = kw.pop(key)
            elif key == "offset":
                self.offset = kw.pop(key)
            elif key == "d_len":
                self.d_len = kw.pop(key)
            else:
                pass

        self.request_timer = QtCore.QTimer()
        self.time_out = 0
        self.last_data = None

    def check_id_var(self, id_var):
        res1, rtr, res2, offset, var_id, dev_id = self.interface.process_id_var(id_var)
        if dev_id == self.dev_id and \
                var_id == self.var_id and \
                offset == self.offset:
            return True
        return False

    def acquire_data(self, can_num=None):
        if can_num is None:
            can_num = self.can_num
        parameters = {"can_num": can_num,
                      "dev_id": self.dev_id,
                      "mode": "read",
                      "var_id": self.var_id,
                      "offset": self.offset,
                      "d_len": self.d_len}
        if self.interface.is_open:
            self.interface.request(**parameters)
            self.request_timer.singleShot(int(write_read_offset*1000), self.read_answer)
            self.time_out = repeat_count
        pass

    def read_answer(self):
        self.time_out -= 1
        if self.time_out > 0:
            self.request_timer.singleShot(int(read_read_offset*1000), self.read_answer)
            id_var, data = self.interface.get_last_data()
            if self.check_id_var(id_var):
                self.last_data = data

                self.time_out = 0
            else:
                self.request_timer.singleShot(int(read_read_offset*1000), self.read_answer)
        else:
            pass
        pass


class FWReader(SimpleCommunication):
    def __init__(self, parent, tmi, **kw):
        offsets = {2: 165,
                   3: 293,
                   5: 421,
                   6: 549,
                   9: 677}
        SimpleCommunication.__init__(self, parent,
                                     var_id=5, d_len=1, offset=offsets[tmi],
                                     **kw)

    def get_data(self):
        if self.last_data is None:
            return "0x%02X (%d)" % (0, 0)
        else:
            return "0x%02X (%d)" % (self.last_data[0], self.last_data[0])
        pass

# -----------------------------------


class InfoBase(QtWidgets.QFrame, ADCS_test_unit_widget.Ui_Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(parent)
        self.last_data = None
        self.name = ""
        pass

    def set_data(self, data):
        self.last_data = data
        self.update_result()
        pass

    def update_result(self):
        self.dataLabel.setText("0x%02X (%d)" % (0, 0))


class GNSSValidReader(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 327
        self.d_len = 1

        self.name = "GNSS valid"
        self.RunCB.setText("Валидность ГЛОНАСС:")
        self.dataLabel.setText("0x%02X (%d)" % (0, 0))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = int.from_bytes(self.last_data, 'little')
            self.dataLabel.setText("0x%02X (%d)" % (num, num))
        pass


class GNSSSecondsInfo(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 12
        self.d_len = 4
        # todo: распарсить в дату
        self.name = "GNSS seconds"
        self.RunCB.setText("Секунды ГЛОНАСС")
        self.dataLabel.setText("0x%02X (%d)" % (0, 0))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = int.from_bytes(self.last_data, 'little')
            self.dataLabel.setText("0x%02X (%d)" % (num, num))
        pass


class CoordInfo(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 0
        self.d_len = 12

        self.name = "GNSS coords"
        self.RunCB.setText("Высота/широта/долгота:")
        self.dataLabel.setText(("0x%02X (%d) \n" % (0, 0)) +
                               ("0x%02X (%d) \n" % (0, 0)) +
                               ("0x%02X (%d) \n" % (0, 0)) )

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText(("0x%02X (%d) \n" % (0, 0)) +
                                   ("0x%02X (%d) \n" % (0, 0)) +
                                   ("0x%02X (%d) \n" % (0, 0)))
        else:
            num = [int.from_bytes(self.last_data[0 : 4], 'little', signed=True),
                   int.from_bytes(self.last_data[4 : 8], 'little', signed=True),
                   int.from_bytes(self.last_data[8 : 12], 'little', signed=True)]

            hex = [int.from_bytes(self.last_data[0: 4], 'little'),
                   int.from_bytes(self.last_data[4: 8], 'little'),
                   int.from_bytes(self.last_data[8: 12], 'little')]

            self.dataLabel.setText(("0x%02X (%d)\n" % (hex[0], num[0])) +
                                   ("0x%02X (%d)\n" % (hex[1], num[1])) +
                                   ("0x%02X (%d)\n" % (hex[2], num[2])))
        pass


class ADCSTempInfo(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 406
        self.d_len = 4

        self.name = "ADCS_temp"
        self.RunCB.setText("Температуры СОП:")
        self.dataLabel.setText(("0x%02X (%d) \n" % (0, 0)) +
                               ("0x%02X (%d) \n" % (0, 0)) +
                               ("0x%02X (%d) \n" % (0, 0)) +
                               ("0x%02X (%d) \n" % (0, 0)) )

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = [ self.last_data[0], self.last_data[1],
                    self.last_data[2], self.last_data[3] ]
            self.dataLabel.setText(("Контроллер: 0x%02X (%d)\n" % (num[0], num[0])) +
                                   ("Темп. датчик: 0x%02X (%d)\n" % (num[1], num[1])) +
                                   ("ДУС: 0x%02X (%d)\n" % (num[2], num[2])) +
                                   ("Магнитометр: 0x%02X (%d)\n" % (num[3], num[3])))

        pass


class RebootCtr(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 82
        self.d_len = 4

        self.name = "reboot ctr"
        self.RunCB.setText("Счетчик перезагрузок:")
        self.dataLabel.setText("0x%02X (%d)" % (0, 0))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = int.from_bytes(self.last_data, 'little')
            self.dataLabel.setText("0x%02X (%d)" % (num, num))
        pass


class LocalTimeReader(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 156
        self.d_len = 4

        self.name = "ADCS ltime"
        self.RunCB.setText("Локальное время:")
        self.dataLabel.setText("0x%02X (%d)" % (0, 0))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = int.from_bytes(self.last_data, 'little')
            self.dataLabel.setText("0x%02X (%d мс)" % (num, num))
        pass


class MagReader(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 16
        self.d_len = 2

        self.name = "mag_abs"
        self.RunCB.setText("Модуль магнитного поля:")
        self.dataLabel.setText("0x%02X (%d)" % (0, 0))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = int.from_bytes(self.last_data, 'little')
            self.dataLabel.setText("0x%02X (%d)" % (num, num))
        pass


class MagVectReader(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 106
        self.d_len = 3

        self.name = "mag_vect"
        self.RunCB.setText("Вектор магнитного поля:")
        self.dataLabel.setText(("X: 0x%02X (%d)\n" % (0, 0)) +
                               ("Y: 0x%02X (%d)\n" % (0, 0)) +
                               ("Z: 0x%02X (%d)\n" % (0, 0)))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = [int(self.last_data[0]),
                   int(self.last_data[1]),
                   int(self.last_data[2])]

            self.dataLabel.setText(("X: 0x%02X (%d)\n" % (num[0], num[0])) +
                                   ("Y: 0x%02X (%d)\n" % (num[1], num[1])) +
                                   ("Z: 0x%02X (%d)\n" % (num[2], num[2])))

        pass


class AngVelReader(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 127
        self.d_len = 3

        self.name = "ang_vel"
        self.RunCB.setText("Угловые скорости:")
        self.dataLabel.setText(("X: 0x%02X (%d)\n" % (0, 0)) +
                               ("Y: 0x%02X (%d)\n" % (0, 0)) +
                               ("Z: 0x%02X (%d)\n" % (0, 0)))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = [int(self.last_data[0]),
                   int(self.last_data[1]),
                   int(self.last_data[2])]

            self.dataLabel.setText(("X: 0x%02X (%d)\n" % (num[0], num[0])) +
                                   ("Y: 0x%02X (%d)\n" % (num[1], num[1])) +
                                   ("Z: 0x%02X (%d)\n" % (num[2], num[2])))

        pass


class AccelReader(InfoBase):
    def __init__(self, parent):
        InfoBase.__init__(self, parent)
        self.var_id = 5
        self.offset = 400
        self.d_len = 6

        self.name = "accelerations"
        self.RunCB.setText("Ускорения:")
        self.dataLabel.setText(("X: 0x%02X (%d)\n" % (0, 0)) +
                               ("Y: 0x%02X (%d)\n" % (0, 0)) +
                               ("Z: 0x%02X (%d)\n" % (0, 0)))

    def update_result(self):
        if self.last_data is None:
            self.dataLabel.setText("0x%02X (%d)" % (0, 0))
        else:
            num = [int.from_bytes(self.last_data[0 : 2], 'little', signed=True),
                   int.from_bytes(self.last_data[2 : 4], 'little', signed=True),
                   int.from_bytes(self.last_data[4 : 6], 'little', signed=True)]

            hex = [int.from_bytes(self.last_data[0 : 2], 'little'),
                   int.from_bytes(self.last_data[2 : 4], 'little'),
                   int.from_bytes(self.last_data[4 : 6], 'little')]

            self.dataLabel.setText(("X: 0x%02X (%d)\n" % (hex[0], num[0])) +
                                   ("Y: 0x%02X (%d)\n" % (hex[1], num[1])) +
                                   ("Z: 0x%02X (%d)\n" % (hex[2], num[2])))

        pass

