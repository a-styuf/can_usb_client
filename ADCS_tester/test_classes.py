import time
from defines import *

boldHtml = "<b>"
alertHtml = "<font color=\"Red\">"
notifyHtml = "<font color=\"DeepPink\">"
passedHtml = "<font color=\"Green\">"
endHtml = "</font><br>"
endBoldHtml = "</b>"


class TesterBase:
    def __init__(self, dev_id):
        self.dev_id = dev_id
        self.last_data = []
        self.name = "NoNameSet"
        self.read_repeat = repeat_count

    def exec(self, interface, can_num):
        parameters = {"can_num": can_num,
                      "dev_id": self.dev_id,
                      "mode": "read",
                      "var_id": self.address.var_id,
                      "offset": self.address.offset,
                      "d_len": self.address.d_len}

        interface.request(**parameters)
        time.sleep(write_read_offset)

        while True:
            if self.read_repeat <= 0:
                print("READER: self.read_repeat <= 0")
                # Err. todo: IMPLEMENT
                break
                pass
            self.read_repeat -= 1
            id_var, data = interface.get_last_data()
            if check_id_var(id_var, self.address):
                self.last_data = data
                self.read_repeat = repeat_count
                break
            time.sleep(read_read_offset)

        pass

    def get_result(self):
        return self.name + " test not implemented, data is " + str(self.last_data), ""


class FWTester(TesterBase):

    def __init__(self, dev_id):
        TesterBase.__init__(self, dev_id)

        self.offsets = [155, 271, 387, 503, 619]
        self.tmi_lst = [2, 3, 5, 6, 9]

        self.addresses = [address(5, offset, 1) for offset in self.offsets]
        self.name = "FW test"
        pass

    def exec(self, interface, can_num):
        for addr in self.addresses:
            parameters = {"can_num": can_num,
                          "dev_id": self.dev_id,
                          "mode": "read",
                          "var_id": addr.var_id,
                          "offset": addr.offset,
                          "d_len": addr.d_len}

            interface.request(**parameters)

            time.sleep(write_read_offset)

            while True:
                if self.read_repeat <= 0:
                    print("READER: self.read_repeat <= 0")
                    # Err. todo: IMPLEMENT
                    break
                    pass
                self.read_repeat -= 1
                id_var, data = interface.get_last_data()
                if check_id_var(id_var, addr, self.dev_id):
                    self.last_data.append(data[0])
                    self.read_repeat = repeat_count
                    break
                time.sleep(read_read_offset)

            time.sleep(next_addr_offset)
            pass

    def get_result(self):

        ret = ""
        err = False

        for elem in self.last_data:
            if elem != self.last_data[0]:
                err = True

        if err:
            ret = boldHtml + alertHtml + \
                  self.name + " error: " + \
                  "Версия прошивки отличается в различных ТМИ: " + str(self.last_data) + \
                  endBoldHtml + endHtml
        else:
            ret = passedHtml + \
                  self.name + " passed: " + \
                  "Все версии прошивки в ТМИ идентичны." + \
                  endHtml

        self.last_data = []
        return ret, ""


class SSAddrTester(TesterBase):

    def __init__(self, dev_id):
        TesterBase.__init__(self, dev_id)
        self.address = address(7, 17, 6)
        self.name = "SS address test"
        pass

    def get_result(self):

        ret = ""
        err = False
        checked = []
        for elem in self.last_data:
            if elem not in [1, 2, 3, 4, 5, 6] or elem in checked:
                err = True
            else:
                checked.append(elem)

        if err:
            ret = boldHtml + alertHtml + \
                  self.name + " error: " + \
                  "Некоторые датчики имеют некорректный адрес: " + str(self.last_data) + \
                  endBoldHtml + endHtml
        else:
            ret = passedHtml + \
                  self.name + " passed: " + \
                  "Адреса датчиков: " + str(self.last_data) + \
                  endHtml

        self.last_data = []
        return ret, ""


class SSLineTester(TesterBase):

    def __init__(self, dev_id):
        TesterBase.__init__(self, dev_id)
        self.address = address(5, 33, 6)
        self.name = "SS line test"
        pass

    def get_result(self):

        ret = ""
        err = False

        for elem in self.last_data:
            if elem != 0x0F:
                err = True

        if err:
            ret = boldHtml + alertHtml + \
                  self.name + " error: " + \
                  "Ошибка одной или нескольких линий связи (должны быть 0x0F): " + str(self.last_data) + \
                  endBoldHtml + endHtml
        else:
            ret = passedHtml + \
                  self.name + " passed: " + \
                  "Линии связи: " + str(self.last_data) + \
                  endHtml

        self.last_data = []
        return ret, ""


class CurSensTester(TesterBase):

    def __init__(self, dev_id):
        TesterBase.__init__(self, dev_id)
        self.address = address(5, 158, 12)
        self.name = "Curent sensor test"
        pass

    def get_result(self):

        values = [int.from_bytes(self.last_data[0:2], 'little'),
                  int.from_bytes(self.last_data[2:4], 'little'),
                  int.from_bytes(self.last_data[4:6], 'little'),
                  int.from_bytes(self.last_data[6:8], 'little'),
                  int.from_bytes(self.last_data[8:10], 'little'),
                  int.from_bytes(self.last_data[10:12], 'little')]

        ret = ""
        err = False

        for elem in values:
            if elem == 0 or elem == 1:
                err = True

        if err:
            ret = boldHtml + alertHtml + \
                  self.name + " error: " + \
                  "Ошибка датчиков тока (должны быть не 0 и не 1): " + str(self.last_data) + \
                  endBoldHtml + endHtml
        else:
            ret = passedHtml + \
                  self.name + " passed: " + \
                  "" + str(self.last_data) + \
                  endHtml

        self.last_data = []
        return ret, ""


class CamGNSSTester(TesterBase):

    def __init__(self, dev_id):
        TesterBase.__init__(self, dev_id)
        self.address = address(5, 31, 2)
        self.name = "Cam GNSS connection test"
        pass

    # def get_result(self):
    #     ret = ""
    #     cam_con = bool(self.last_data[1] & 0x04)
    #     GNSS_con = bool(self.last_data[1] & 0x08)
    #
    #     ret = boldHtml + notifyHtml + \
    #           self.name + " state: " + \
    #           "Подключение каемеры: " + str(cam_con) + \
    #           " Подключение  антенны: " + str(cam_con) + \
    #           endBoldHtml + endHtml
    #
    #     self.last_data = []
    #     return ret, ""
