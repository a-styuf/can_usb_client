'''
    модуль собирающий в себе стандартизованные функции разбора данных
    Стандарт:
    параметры:
        frame - в виде листа с данными
    возвращает:
        table_list - список подсписков (подсписок - ["Имя", "Значение"])
'''

import crc16
from ctypes import c_int8, c_int16, c_int32
import threading

# замок для мультипоточного запроса разбора данных
data_lock = threading.Lock()
# раскрашивание переменных
# модули
linking_module = 6
lm_beacon = 0x80
lm_tmi = 0x81
lm_full_tmi = 0x82
lm_cyclogram_result = 0x89


def frame_parcer(frame):
    try:
        with data_lock:
            data = []
            while len(frame) < 64:
                frame.append(0xFEFE)
                pass
            if 0x0FF1 == _rev16(frame[0]):  # проверка на метку кадра
                if get_id_loc_data(_rev16(frame[1]))[0] == linking_module:
                    if get_id_loc_data(_rev16(frame[1]))[2] == lm_beacon:
                        #
                        data.append(["Метка кадра", "0x%04X" % _rev16(frame[0])])
                        data.append(["Определитель", "0x%04X" % _rev16(frame[1])])
                        data.append(["Номер кадра, шт", "%d" % _rev16(frame[2])])
                        data.append(["Время кадра, с", "%d" % _rev32(frame[3], frame[4])])
                        #
                        data.append(["Статус МС", "0x%02X" % _rev16(frame[5])])
                        data.append(["Стутус ПН", "0x%04X" % _rev16(frame[6])])
                        data.append(["Статус пит. ПН", "0x%02X" % ((frame[7] >> 0) & 0xFF)])
                        data.append(["Темп. МС, °С", "%d" % c_int8(((frame[7] >> 8) & 0xFF)).value])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 64)])
                    elif get_id_loc_data(_rev16(frame[1]))[2] == lm_tmi:
                        #
                        data.append(["Метка кадра", "0x%04X" % _rev16(frame[0])])
                        data.append(["Определитель", "0x%04X" % _rev16(frame[1])])
                        data.append(["Номер кадра, шт", "%d" % _rev16(frame[2])])
                        data.append(["Время кадра, с", "%d" % _rev32(frame[3], frame[4])])
                        #
                        for i in range(6):
                            data.append(["ПН%d статус" % i, "0x%04X" % _rev16(frame[5+i])])
                        for i in range(7):
                            data.append(["ПН%d напр., В" % i, "%.2f" % (((frame[11+i] >> 8) & 0xFF)/(2**4))])
                            data.append(["ПН%d ток, А" % i, "%.2f" % (((frame[11+i] >> 0) & 0xFF)/(2**4))])
                        data.append(["МС темп.,°С", "%.2f" % ((frame[18] >> 8) & 0xFF)])
                        data.append(["ПН1 темп.,°С", "%.2f" % ((frame[18] >> 0) & 0xFF)])
                        data.append(["ПН2 темп.,°С", "%.2f" % ((frame[19] >> 8) & 0xFF)])
                        data.append(["ПН3 темп.,°С", "%.2f" % ((frame[19] >> 0) & 0xFF)])
                        data.append(["ПН4 темп.,°С", "%.2f" % ((frame[20] >> 8) & 0xFF)])
                        #
                        data.append(["Статус пит. ПН", "0x%02X" % ((frame[20] >> 0) & 0xFF)])
                        data.append(["Память ИСС, %", "%.1f" % (100*((frame[21] >> 8) & 0xFF)/256)])
                        data.append(["Память ДКР, %", "%.1f" % (100*((frame[21] >> 0) & 0xFF)/256)])
                        data.append(["Счетчик включений", "%d" % ((frame[22] >> 8) & 0xFF)])
                        data.append(["Выравнивание", "0x%02X" % ((frame[22] >> 0) & 0xFF)])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 63)])
                    elif get_id_loc_data(_rev16(frame[1]))[2] == lm_full_tmi:
                        #
                        data.append(["Метка кадра", "0x%04X" % _rev16(frame[0])])
                        data.append(["Определитель", "0x%04X" % _rev16(frame[1])])
                        data.append(["Номер кадра, шт", "%d" % _rev16(frame[2])])
                        data.append(["Время кадра, с", "%d" % _rev32(frame[3], frame[4])])
                        #
                        data.append(["LM:status", "0x%04X" % _rev16(frame[5])])
                        data.append(["LM:err.flgs", "0x%04X" % _rev16(frame[6])])
                        data.append(["LM:err.cnt", "%d" % ((frame[7] >> 8) & 0xFF)])
                        data.append(["LM:rst.cnt", "%d" % ((frame[7] >> 0) & 0xFF)])
                        data.append(["LM:U,V", "%.3f" % (_rev16(frame[8])/256)])
                        data.append(["LM:I,A", "%.3f" % (_rev16(frame[9])/256)])
                        temp = c_int16(_rev16(frame[10])).value
                        data.append(["LM:T,°C", "%.3f" % (temp/256)])
                        #
                        for num, suff in enumerate(["A", "B"]):
                            name = "PL11%s" % suff
                            offs = [14, 23][num]
                            #
                            data.append(["%s:status" % name, "0x%04X" % _rev16(frame[offs+0])])
                            data.append(["%s:err.flgs" % name, "0x%04X" % _rev16(frame[offs+1])])
                            data.append(["%s:err.cnt" % name, "%d" % ((frame[offs+2] >> 8) & 0xFF)])
                            data.append(["%s:inhibits" % name, "%02X" % ((frame[offs+2] >> 0) & 0xFF)])
                            data.append(["%s:U,V" % name, "%.3f" % (_rev16(frame[offs+3]) / 256)])
                            data.append(["%s:I,A" % name, "%.3f" % (_rev16(frame[offs+4]) / 256)])
                            data.append(["%s:T,°C" % name, "%.3f" % (c_int16(_rev16(frame[offs+5])).value / 256)])
                            #
                            STM = (frame[offs+6] >> 0) & 0xFF
                            data.append(["%s:STM_INT" % name, "0x%02X" % ((STM>>0) & 0x01)])
                            data.append(["%s:STM_PWR_ERR" % name, "0x%02X" % ((STM>>1) & 0x01)])
                            data.append(["%s:STM_WD" % name, "0x%02X" % ((STM>>2) & 0x01)])
                            data.append(["%s:STM_CPU_ERR" % name, "0x%02X" % ((STM>>3) & 0x01)])
                            #
                            IKU = (frame[offs+6] >> 8) & 0xFF
                            data.append(["%s:IKU_RST_FPGA" % name, "0x%02X" % ((IKU >> 0) & 0x01)])
                            data.append(["%s:IKU_RST_LEON" % name, "0x%02X" % ((IKU >> 1) & 0x01)])
                        #
                        data.append(["PL_DCR:status", "0x%04X" % _rev16(frame[50])])
                        data.append(["PL_DCR:err.flgs", "0x%04X" % _rev16(frame[51])])
                        data.append(["PL_DCR:err.cnt", "%d" % ((frame[52] >> 8) & 0xFF)])
                        data.append(["PL_DCR:PWR_SW", "0x%02X" % ((frame[52] >> 0) & 0xFF)])
                        data.append(["PL_DCR:Umcu,V", "%.3f" % (_rev16(frame[53]) / 256)])
                        data.append(["PL_DCR:Imcu,A", "%.3f" % (_rev16(frame[54]) / 256)])
                        data.append(["PL_DCR:Umsr,V", "%.3f" % (_rev16(frame[55]) / 256)])
                        data.append(["PL_DCR:Imsr,A", "%.3f" % (_rev16(frame[56]) / 256)])
                        data.append(["PL_DCR:rx cnt", "%d" % ((frame[57] >> 8) & 0xFF)])
                        data.append(["PL_DCR:tx cnt", "%d" % ((frame[58] >> 0) & 0xFF)])
                        #
                        data.append(["LM: MEM ISS vol, fr", "%d" % _rev16(frame[11])])
                        data.append(["LM: MEM DCR vol, fr", "%d" % _rev16(frame[12])])
                        data.append(["MEM: ISS wr_ptr", "%d" % _rev32(frame[59], frame[60])])
                        data.append(["MEM: DCR wr_ptr", "%d" % _rev32(frame[61], frame[62])])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 63)])
                    elif get_id_loc_data(_rev16(frame[1]))[2] == lm_cyclogram_result:
                        #
                        data.append(["Метка кадра", "0x%04X" % _rev16(frame[0])])
                        data.append(["Определитель", "0x%04X" % _rev16(frame[1])])
                        data.append(["Номер кадра, шт", "%d" % _rev16(frame[2])])
                        data.append(["Время кадра, с", "%d" % _rev32(frame[3], frame[4])])
                        data.append(["Кол-во кадров, шт.", "%d" % _rev16(frame[5])])
                        #
                        data.append(["№ цикл.", "%d" % _rev16(frame[6])])
                        data.append(["Режим", "0x%02X" % ((frame[7] >> 8) & 0xFF)])
                        data.append(["Статус", "0x%02X" % ((frame[7] >> 0) & 0xFF)])
                        #
                        for num in range(8):
                            data.append(["ТМИ%d: №" % num, "%d" % ((frame[15+num*6] >> 8) & 0xFF)])
                            data.append(["ТМИ%d: ПН" % num, "0x%04X" % ((frame[15+num*6] >> 0) & 0xFF)])
                            data.append(["ТМИ%d: U,В" % num, "%.2f" % (((frame[16+num*6] >> 8) & 0xFF)/(2**4))])
                            data.append(["ТМИ%d: I,А" % num, "%.2f" % (((frame[16+num*6] >> 0) & 0xFF)/(2**4))])
                            data.append(["ТМИ%d: ИКУ" % num, "0x%02X" % ((frame[17+num*6] >> 8) & 0xFF)])
                            data.append(["ТМИ%d: СТМ" % num, "0x%02X" % ((frame[17+num*6] >> 0) & 0xFF)])
                            data.append(["ТМИ%d: °С" % num, "%d" % c_int8(((frame[18+num*6] >> 8) & 0xFF)).value])
                            data.append(["ТМИ%d: Счетчик ош." % num, "%d" % ((frame[18+num*6] >> 0) & 0xFF)])
                            data.append(["ТМИ%d: ПН ош." % num, "0x%04X" % (frame[19+num*6])])
                            data.append(["ТМИ%d: ПН ст." % num, "0x%04X" % (frame[20+num*6])])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16.calc(frame, 63)])
                    else:
                        #
                        data.append(["Метка кадра", "0x%04X" % _rev16(frame[0])])
                        data.append(["Определитель", "0x%04X" % _rev16(frame[1])])
                        data.append(["Номер кадра, шт", "%d" % _rev16(frame[2])])
                        #
                        data.append(["Неизвестный тип данных", "0"])
                else:
                    data.append(["Неизвестный определитель", "0"])
            else:
                data.append(["Данные не распознаны", "0"])
            return data
    except Exception as error:
        print(error)
        return None


def get_id_loc_data(id_loc):
    device_id = (id_loc >> 12) & 0xF
    flags = (id_loc >> 8) & 0xF
    data_id = (id_loc >> 0) & 0xFF
    return device_id, flags, data_id


def _rev16(var):
    return ((var & 0xFF00) >> 8) + ((var & 0xFF) << 8)


def _rev32(var1, var2):
    return ((((var2 & 0xFF00) >> 8) + ((var2 & 0xFF) << 8)) << 16) + ((var1 & 0xFF00) >> 8) + ((var1 & 0xFF) << 8)


