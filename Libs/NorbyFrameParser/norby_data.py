
#    модуль собирающий в себе стандартизованные функции разбора данных
#    Стандарт:
#    параметры:
#        frame - побайтовый листа данных
#    возвращает:
#        table_list - список подсписков (подсписок - ["Имя", "Значение"]) - оба поля текстовые

import threading
import struct
ADCS_status = ["UNKNOWN", "ST_IN_PROGRESS", "ST_SUCCESS_END",
                "ST_ERROR", "ST_ERROR_TIMEOUT", "ST_STOPPED"]

# замок для мультипоточного запроса разбора данных
data_lock = threading.Lock()
# раскрашивание переменных
# модули
linking_module = 6
ADCS_module_main = 4
ADCS_module_res = 5

use_new_header = True

# тип кадров
lm_beacon = 0x80
lm_tmi = 0x81
lm_full_tmi = 0x82
lm_cyclogram_result = 0x89
lm_load_param = 0x8A

ADCS_calib = 0x17
ADCS_settings = 0x18
LOG_TMI2_rec = 0x22
LOG_TMI3_rec = 0x23
LOG_TMI5_rec = 0x25
LOG_TMI6_rec = 0x26
LOG_TMI9_rec = 0x27

TMI0_pack_t = 0x00
TMI2_pack_t = 0x02
TMI3_pack_t = 0x03
TMI5_pack_t = 0x05
TMI6_pack_t = 0x06
TMI9_pack_t = 0x09

def frame_parcer(frame):
    try:
        with data_lock:
            data = []
            #
            while len(frame) < 128:
                frame.append(0xFE)
            #
            try:
                b_frame = bytes(frame)
            except Exception as error:
                print(error)
            if 0x0FF1 == val_from(frame, 0, 2):  # проверка на метку кадра

                new_header = bool(val_from(frame, 3, 1) & 0x80) | use_new_header
                id_loc_raw  = val_from(frame, 4, 2) if new_header else val_from(frame, 2, 2)
                id_loc_data = get_id_loc_data(id_loc_raw)

                if id_loc_data["dev_id"] == linking_module:
                    if id_loc_data["data_code"] == lm_beacon:
                        #
                        data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])
                        data.append(["Определитель", "0x%04X" % val_from(frame, 2, 2)])
                        data.append(["Номер кадра, шт", "%d" % val_from(frame, 4, 2)])
                        data.append(["Время кадра, с", "%d" % val_from(frame, 6, 4)])
                        #
                        data.append(["Статус МС", "0x%02X" % val_from(frame, 10, 2)])
                        data.append(["Стутус ПН", "0x%04X" % val_from(frame, 12, 2)])
                        data.append(["Темп. МС, °С", "%d" % val_from(frame, 14, 1, signed=True)])
                        data.append(["Статус пит. ПН", "0x%02X" % val_from(frame, 15, 1)])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16_calc(frame, 128)])
                    elif id_loc_data["data_code"] == lm_tmi:
                        #
                        data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])
                        data.append(["Определитель", "0x%04X" % val_from(frame, 2, 2)])
                        data.append(["Номер кадра, шт", "%d" % val_from(frame, 4, 2)])
                        data.append(["Время кадра, с", "%d" % val_from(frame, 6, 4)])
                        #
                        for i in range(6):
                            data.append(["ПН%d статус" % i, "0x%04X" % val_from(frame, (10 + i * 2), 2)])
                        for i in range(7):
                            data.append(["ПН%d напр., В" % i, "%.2f" % (val_from(frame, (22 + i * 2), 1) / (2 ** 4))])
                            data.append(["ПН%d ток, А" % i, "%.2f" % (val_from(frame, (23 + i * 2), 1) / (2 ** 4))])
                        data.append(["МС темп.,°С", "%.2f" % val_from(frame, 36, 1, signed=True)])
                        data.append(["ПН1 темп.,°С", "%.2f" % val_from(frame, 37, 1, signed=True)])
                        data.append(["ПН2 темп.,°С", "%.2f" % val_from(frame, 38, 1, signed=True)])
                        data.append(["ПН3 темп.,°С", "%.2f" % val_from(frame, 39, 1, signed=True)])
                        data.append(["ПН4 темп.,°С", "%.2f" % val_from(frame, 40, 1, signed=True)])
                        #
                        data.append(["Статус пит. ПН", "0x%02X" % val_from(frame, 41, 1)])
                        data.append(["Память ИСС, %", "%.1f" % val_from(frame, 42, 1)])
                        data.append(["Память ДКР, %", "%.1f" % val_from(frame, 43, 1)])
                        data.append(["Счетчик включений", "%d" % val_from(frame, 44, 1)])
                        data.append(["К.Р. питаиня", "0x%02X" % val_from(frame, 45, 1)])
                        data.append(["К.Р. запрет", "0x%02X" % val_from(frame, 46, 2)])
                        data.append(["Память ИСС у.ч.", "%d" % val_from(frame, 48, 2)])
                        data.append(["Память ИСС у.з.", "%d" % val_from(frame, 50, 2)])
                        data.append(["Память ИСС объем.", "%d" % val_from(frame, 52, 2)])
                        data.append(["Память ДКР у.ч.", "%d" % val_from(frame, 54, 2)])
                        data.append(["Память ДКР у.з.", "%d" % val_from(frame, 56, 2)])
                        data.append(["Память ДКР объем", "%d" % val_from(frame, 58, 2)])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16_calc(frame, 128)])
                    elif id_loc_data["data_code"] == lm_full_tmi:
                        #
                        data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])
                        data.append(["Определитель", "0x%04X" % val_from(frame, 2, 2)])
                        data.append(["Номер кадра, шт", "%d" % val_from(frame, 4, 2)])
                        data.append(["Время кадра, с", "%d" % val_from(frame, 6, 4)])
                        #
                        data.append(["LM:status", "0x%04X" % val_from(frame, 10, 2)])
                        data.append(["LM:err.flgs", "0x%04X" % val_from(frame, 12, 2)])
                        data.append(["LM:err.cnt", "%d" % val_from(frame, 14, 1)])
                        data.append(["LM:rst.cnt", "%d" % val_from(frame, 15, 1)])
                        data.append(["LM:U,V", "%.3f" % (val_from(frame, 16, 2) / 256)])
                        data.append(["LM:I,A", "%.3f" % (val_from(frame, 18, 2) / 256)])
                        data.append(["LM:T,°C", "%.3f" % (val_from(frame, 20, 2) / 256)])
                        #
                        for num, suff in enumerate(["A", "B"]):
                            name = "PL11%s" % suff
                            offs = [28, 46][num]
                            #
                            data.append(["%s:status" % name, "0x%04X" % val_from(frame, offs + 0, 2)])
                            data.append(["%s:err.flgs" % name, "0x%04X" % val_from(frame, offs + 2, 2)])
                            data.append(["%s:err.cnt" % name, "%d" % val_from(frame, offs + 4, 1)])
                            data.append(["%s:inhibits" % name, "%02X" % val_from(frame, offs + 5, 1)])
                            data.append(["%s:U,V" % name, "%.3f" % (val_from(frame, offs + 6, 2, signed=True) / 256)])
                            data.append(["%s:I,A" % name, "%.3f" % (val_from(frame, offs + 8, 2, signed=True) / 256)])
                            data.append(["%s:T,°C" % name, "%.3f" % (val_from(frame, offs + 10, 2, signed=True) / 256)])
                            #
                            stm = val_from(frame, offs + 13, 1)
                            data.append(["%s:STM_INT" % name, "0x%02X" % ((stm >> 0) & 0x01)])
                            data.append(["%s:STM_PWR_ERR" % name, "0x%02X" % ((stm >> 1) & 0x01)])
                            data.append(["%s:STM_WD" % name, "0x%02X" % ((stm >> 2) & 0x01)])
                            data.append(["%s:STM_CPU_ERR" % name, "0x%02X" % ((stm >> 3) & 0x01)])
                            #
                            iku = val_from(frame, offs + 12, 1)
                            data.append(["%s:IKU_RST_FPGA" % name, "0x%02X" % ((iku >> 0) & 0x01)])
                            data.append(["%s:IKU_RST_LEON" % name, "0x%02X" % ((iku >> 1) & 0x01)])
                        #
                        name = "PL12"
                        offs = 64
                        data.append(["%s:status" % name, "0x%04X" % val_from(frame, offs + 0, 2)])
                        data.append(["%s:err.flgs" % name, "0x%04X" % val_from(frame, offs + 2, 2)])
                        data.append(["%s:err.cnt" % name, "%d" % val_from(frame, offs + 4, 1)])
                        data.append(["%s:inhibits" % name, "%02X" % val_from(frame, offs + 5, 1)])
                        data.append(["%s:U,V" % name, "%.3f" % (val_from(frame, offs + 6, 2, signed=True) / 256)])
                        data.append(["%s:I,A" % name, "%.3f" % (val_from(frame, offs + 8, 2, signed=True) / 256)])
                        data.append(["%s:T,°C" % name, "%.3f" % (val_from(frame, offs + 10, 2, signed=True) / 256)])
                        #
                        stm = val_from(frame, offs + 13, 1)
                        data.append(["%s:TM_PWR_ERR" % name, "0x%02X" % ((stm >> 0) & 0x01)])
                        data.append(["%s:TM_CPU_OK" % name, "0x%02X" % ((stm >> 1) & 0x01)])
                        data.append(["%s:TM_INT" % name, "0x%02X" % ((stm >> 2) & 0x01)])
                        data.append(["%s:TM_ERR" % name, "0x%02X" % ((stm >> 3) & 0x01)])
                        #
                        iku = val_from(frame, offs + 12, 1)
                        data.append(["%s:IKU_nRST" % name, "0x%02X" % ((iku >> 0) & 0x01)])
                        data.append(["%s:IKU_SPI_SEL" % name, "0x%02X" % ((iku >> 1) & 0x01)])
                        #
                        name = "PL20"
                        offs = 82
                        data.append(["%s:status" % name, "0x%04X" % val_from(frame, offs + 0, 2)])
                        data.append(["%s:err.flgs" % name, "0x%04X" % val_from(frame, offs + 2, 2)])
                        data.append(["%s:err.cnt" % name, "%d" % val_from(frame, offs + 4, 1)])
                        data.append(["%s:inhibits" % name, "%02X" % val_from(frame, offs + 5, 1)])
                        data.append(["%s:U,V" % name, "%.3f" % (val_from(frame, offs + 6, 2, signed=True) / 256)])
                        data.append(["%s:I,A" % name, "%.3f" % (val_from(frame, offs + 8, 2, signed=True) / 256)])
                        data.append(["%s:T,°C" % name, "%.3f" % (val_from(frame, offs + 10, 2, signed=True) / 256)])
                        #
                        stm = val_from(frame, offs + 13, 1)
                        data.append(["%s:TM_SYS_FAIL" % name, "0x%02X" % ((stm >> 0) & 0x01)])
                        data.append(["%s:TM_I_MON" % name, "0x%02X" % ((stm >> 1) & 0x01)])
                        data.append(["%s:TM_INT" % name, "0x%02X" % ((stm >> 2) & 0x01)])
                        data.append(["%s:TM_ANA" % name, "0x%02X" % ((stm >> 3) & 0x01)])
                        #
                        iku = val_from(frame, offs + 12, 1)
                        data.append(["%s:IKU_EXT_RST" % name, "0x%02X" % ((iku >> 0) & 0x01)])
                        #
                        data.append(["PL_DCR:status", "0x%04X" % val_from(frame, 100, 2)])
                        data.append(["PL_DCR:err.flgs", "0x%04X" % val_from(frame, 102, 2)])
                        data.append(["PL_DCR:err.cnt", "%d" % val_from(frame, 104, 1)])
                        data.append(["PL_DCR:PWR_SW", "0x%02X" % val_from(frame, 105, 1)])
                        data.append(["PL_DCR:Umcu,V", "%.3f" % (val_from(frame, 106, 2, signed=True) / 256)])
                        data.append(["PL_DCR:Imcu,A", "%.3f" % (val_from(frame, 108, 2, signed=True) / 256)])
                        data.append(["PL_DCR:Umsr,V", "%.3f" % (val_from(frame, 110, 2, signed=True) / 256)])
                        data.append(["PL_DCR:Imsr,A", "%.3f" % (val_from(frame, 112, 2, signed=True) / 256)])
                        data.append(["PL_DCR:rx cnt", "%d" % val_from(frame, 114, 1)])
                        data.append(["PL_DCR:tx cnt", "%d" % val_from(frame, 115, 1)])
                        #
                        data.append(["MEM: ISS wr_ptr", "%d" % val_from(frame, 22, 2)])
                        data.append(["MEM: DCR wr_ptr", "%d" % val_from(frame, 24, 2)])
                        data.append(["MEM: ISS rd_ptr", "%d" % val_from(frame, 118, 2)])
                        data.append(["MEM: ISS vol", "%d" % val_from(frame, 120, 2)])
                        data.append(["MEM: DCR rd_ptr", "%d" % val_from(frame, 122, 2)])
                        data.append(["MEM: DCR vol", "%d" % val_from(frame, 124, 2)])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16_calc(frame, 128)])
                    elif id_loc_data["data_code"] == lm_cyclogram_result:
                        #
                        data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])
                        data.append(["Определитель", "0x%04X" % val_from(frame, 2, 2)])
                        data.append(["Номер кадра, шт", "%d" % val_from(frame, 4, 2)])
                        data.append(["Время кадра, с", "%d" % val_from(frame, 6, 4)])
                        data.append(["Кол-во кадров, шт.", "%d" % val_from(frame, 10, 2)])
                        #
                        data.append(["№ цикл.", "%d" % val_from(frame, 12, 2)])
                        data.append(["Режим", "0x%02X" % val_from(frame, 14, 1)])
                        data.append(["Статус", "0x%02X" % val_from(frame, 15, 1)])
                        #
                        for num in range(8):
                            sub_offs = num*12 + 30
                            data.append(["ТМИ%d: №" % num, "%d" % val_from(frame, 0 + sub_offs, 1)])
                            data.append([" ТМИ%d: ПН" % num, "0x%04X" % val_from(frame, 1 + sub_offs, 1)])
                            data.append([" ТМИ%d: U,В" % num, "%.2f" % (val_from(frame, 2 + sub_offs, 1)/(2**4))])
                            data.append([" ТМИ%d: I,А" % num, "%.2f" % (val_from(frame, 3 + sub_offs, 1)/(2**4))])
                            data.append([" ТМИ%d: ИКУ" % num, "0x%02X" % val_from(frame, 4 + sub_offs, 1)])
                            data.append([" ТМИ%d: СТМ" % num, "0x%02X" % val_from(frame, 5 + sub_offs, 1)])
                            data.append([" ТМИ%d: °С" % num, "%d" % val_from(frame, 6 + sub_offs, 1, signed=True)])
                            data.append([" ТМИ%d: Счетчик ош." % num, "%d" % val_from(frame, 7 + sub_offs, 1)])
                            data.append([" ТМИ%d: ПН ош." % num, "0x%04X" % val_from(frame, 8 + sub_offs, 1)])
                            data.append([" ТМИ%d: ПН ст." % num, "0x%04X" % val_from(frame, 9 + sub_offs, 1)])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16_calc(frame, 128)])
                    elif id_loc_data["data_code"] == lm_load_param:
                        #
                        data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])
                        data.append(["Определитель", "0x%04X" % val_from(frame, 2, 2)])
                        data.append(["Номер кадра, шт", "%d" % val_from(frame, 4, 2)])
                        data.append(["Время кадра, с", "%d" % val_from(frame, 6, 4)])
                        #
                        data.append(["Версия", "%d.%02d.%02d" % (val_from(frame, 10, 2),
                                                                 val_from(frame, 12, 2),
                                                                 val_from(frame, 14, 2))])
                        data.append(["К. питания", "%d" % val_from(frame, 16, 2, signed=True)])
                        data.append(["К. темп", "%d" % val_from(frame, 18, 2, signed=True)])
                        data.append(["Циклограммы", "%d" % val_from(frame, 20, 2, signed=True)])
                        data.append(["CAN", "%d" % val_from(frame, 22, 2, signed=True)])
                        data.append(["Внеш. память", "%d" % val_from(frame, 24, 2, signed=True)])
                        #
                        data.append(["CRC-16", "0x%04X" % crc16_calc(frame, 128)])
                    else:
                        #
                        data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])
                        data.append(["Определитель", "0x%04X" % val_from(frame, 2, 2)])
                        data.append(["Номер кадра, шт", "%d" % val_from(frame, 4, 2)])
                        #
                        data.append(["Неизвестный тип данных", "0"])
                elif id_loc_data["dev_id"] == ADCS_module_main or \
                        id_loc_data["dev_id"] == ADCS_module_res:
                    first_loc_flag = not bool(id_loc_raw & 0x0100)
                    data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])

                    header_offset = 2 if new_header else 0
                    # header_size = 12 if new_header else 10
                    if new_header:
                        data.append(["id_sat", "0x%04X" % val_from(frame, 2, 2)])

                    data.append(["Определитель", "0x%04X" % id_loc_raw])

                    data.append(["Номер массива/кадра", "%d" % val_from(frame, 4+header_offset, 2)])

                    data.append(["Время кадра, с", "%d" % val_from(frame, 6+header_offset, 4)])


                    if id_loc_data["data_code"] == ADCS_calib:
                        data.append(["Тип данных", "Калибровка"])
                    elif id_loc_data["data_code"] == ADCS_settings:
                        data.append(["Тип данных", "Настройки"])
                        # if first_loc:
                        #     data.append(["om.flag_scan_ports", "0x%02X" %
                        #                  val_from(frame, header_size + 0, 1)])
                        #     data.append(["om.flag_polling", "0x%02X" %
                        #                  val_from(frame, header_size + 1, 1)])
                        #     data.append(["om.ON_list", "0x%08X" %
                        #                  val_from(frame, header_size + 2, 4)])
                        #     data.append(["om.timing", "0x%08X" %
                        #                  val_from(frame, header_size + 6, 4)])
                        #     data.append(["om.req_en", "0x%08X" %
                        #                  val_from(frame, header_size + 10, 4)])
                        #     data.append(["om.reboot_delay", "0x%02X" %
                        #                  val_from(frame, header_size + 14, 2)])
                        # elif val_from(frame, 6 + header_offset, 2) == (4-2):
                        #     data.append(["i2c.gam_set.mode", "0x%02X" %
                        #                  val_from(frame, header_size + 0, 1)])
                        #     data.append(["...", "..."])
                        #     data.append(["i2c.gam_set.res8", "0x%02X" %
                        #                  val_from(frame, header_size + 9, 1)])
                        # elif val_from(frame, 6 + header_offset, 2) == (5-2):
                        #     data.append(["mt.flag_mt_par", "0x%02X" %
                        #                  val_from(frame, header_size + 0, 1)])
                        #     data.append(["mt.flag_mt_dir", "0x%02X" %
                        #                  val_from(frame, header_size + 1, 1)])
                        #     data.append(["mt.reverse_axis", "0x%02X" %
                        #                  val_from(frame, header_size + 2, 1)])
                        #     data.append(["mt.disable_axis", "0x%02X" %
                        #                  val_from(frame, header_size + 3, 1)])
                        #
                        #     data.append(["...", "..."])
                        #
                        #     data.append(["mt.power_limit", "0x%08X" %
                        #                  val_from(frame, header_size + 4, 4)])
                    elif id_loc_data["data_code"] == TMI2_pack_t or\
                            id_loc_data["data_code"] == LOG_TMI2_rec:
                        data.append(["Тип данных", "ТМИ 2"])
                        if id_loc_data["data_code"] == TMI2_pack_t or not first_loc_flag:
                            data.append(["Высота, 0.1м", "%d" %
                                         val_from(frame, 52 - 40, 4, signed=True)])
                        data.append(["Широта", "%d" % val_from(frame, 56 - 40, 4, signed=True)])
                        data.append(["Долгота", "%d" % val_from(frame, 60 - 40, 4, signed=True)])
                        data.append(["Горизонтальная скорость, 0,01м/с", "%d" %
                                     val_from(frame, 64 - 40 + 8, 4, signed=True)])
                        data.append(["Азимут скорости", "%d" %
                                     val_from(frame, 68 - 40, 4, signed=True)])
                        data.append(["Вертикальная скорость", "%d" %
                                     val_from(frame, 72 - 40, 4, signed=True)])

                        data.append(["Время по датчику ГЛОНАСС", "%d" %
                                     val_from(frame, 76 - 40, 4)])

                        gnss_val = val_from(frame, 80 - 40, 1)
                        data.append(["Валидность данных ГЛОНАСС", str(bool(gnss_val & 0x80))])
                        data.append(["Количество спутников", "%d" % (gnss_val & (~0x80))])

                        data.append(["Видимость антенны и солнца", "%d" %
                                     val_from(frame, 81 - 40, 1)])
                        data.append(["Счетчик перезапусков", "%d" %
                                     val_from(frame, 82 - 40, 4)])

                        data.append(["Модуль ускорения", "%d" % val_from(frame, 86 - 40, 2)])

                        for i in range(6):
                            data.append(["Температура контроллера ДСГ %d" % (i + 1), "%d" %
                                         val_from(frame, 134 + 1 * i - 40, 1, signed=True)])
                            data.append(["Медианная температура ДСГ %d" % (i + 1), "%d" %
                                         val_from(frame, 141 + 1 * i - 40, 1, signed=True)])

                            data.append(["Статус модуля ДСГ %d (битовая маска)" % (i + 1), "0x%02X" %
                                         val_from(frame, 150 + 1 * i - 40, 1, signed=True)])
                            data.append(["Вектор магнитной индукции ДСГ %d" % (i + 1), "(%d, %d, %d)" %
                                         (val_from(frame, 88 + 3 * i - 40, 1, signed=True),
                                          val_from(frame, 89 + 3 * i - 40, 1, signed=True),
                                          val_from(frame, 90 + 3 * i - 40, 1, signed=True))])
                            data.append(["Вектор угловой скорости ДСГ %d" % (i + 1), "(%d, %d, %d)" %
                                         (val_from(frame, 109 + 3 * i - 40, 1, signed=True),
                                          val_from(frame, 110 + 3 * i - 40, 1, signed=True),
                                          val_from(frame, 111 + 3 * i - 40, 1, signed=True))])

                        data.append(["Вектор магнитной индукции СОП", "(%d, %d, %d)" %
                                     (val_from(frame, 106 - 40, 1, signed=True),
                                      val_from(frame, 107 - 40, 1, signed=True),
                                      val_from(frame, 108 - 40, 1, signed=True))])
                        data.append(["Вектор  угловой скорости СОП", "(%d, %d, %d)" %
                                     (val_from(frame, 127 - 40, 1, signed=True),
                                      val_from(frame, 128 - 40, 1, signed=True),
                                      val_from(frame, 129 - 40, 1, signed=True))])

                        data.append(["Угол между парой векторов приоритета 1", "%d" %
                                     val_from(frame, 130 - 40, 2, signed=True)])
                        data.append(["Угол между парой векторов приоритета 2", "%d" %
                                     val_from(frame, 132 - 40, 2, signed=True)])

                        data.append(["Температура контроллера СОП", "%d" %
                                     val_from(frame, 140 - 40, 1, signed=True)])
                        data.append(["Температура модуля СОП", "%d" %
                                     val_from(frame, 147 - 40, 1, signed=True)])

                        ADCS_stat = val_from(frame, 148 - 40, 2)
                        ADCS_dev_id = (ADCS_stat >> 0) & 0x0F
                        mt_dis_axes = (ADCS_stat >> 4) & 0x3F
                        ADCS_cam =    (ADCS_stat >> 10) & 0x01
                        ADCS_gant =   (ADCS_stat >> 11) & 0x01
                        ADCS_can  =   (ADCS_stat >> 12) & 0x01
                        data.append(["Статус модуля СОП (битовая маска)", "0x%04X" % ADCS_stat])

                        data.append(["Dev_id", "%d" % ADCS_dev_id])
                        data.append(["mt->disable_axis (Z-, Z+, Y-, Y+, X-, X+)", bin(mt_dis_axes)])
                        # data.append(["Подключение камеры", str(bool(ADCS_cam))])
                        data.append(["Подключение антенны", str(bool(ADCS_gant))])
                        data.append(["Наличие ошибок CAN", str(bool(ADCS_can))])

                        data.append(["время ТМИ2 (мс)", "%d" %
                                     val_from(frame, 156 - 40, 4)])
                        # data.append(["резерв 2", "%d" %
                        #              val_from(frame, header_size + 148 - 40, 2)])

                        data.append(["Set_Orientation_Accur", "%d" %
                                     val_from(frame, 160 - 40, 1)])
                        data.append(["Stop_Rotation_Status", "%d" %
                                     val_from(frame, 161 - 40, 1)])
                        data.append(["Stop_Rotation_Accur", "%d" %
                                     val_from(frame, 162 - 40, 1)])
                        data.append(["Set_Orientation_Status", "%d" %
                                     val_from(frame, 163 - 40, 1)])
                        data.append(["Orientation_Mode", "%d" %
                                     val_from(frame, 164 - 40, 1)])

                        data.append(["Версия прошивки ТМИ2", "%d" % val_from(frame, 165-40, 1)])
                    elif id_loc_data["data_code"] == TMI3_pack_t or\
                            id_loc_data["data_code"] == LOG_TMI3_rec:
                        data.append(["Тип данных", "ТМИ 3"])
                        if id_loc_data["data_code"] == TMI3_pack_t or not first_loc_flag:
                            data.append(["оценка времени остановки", "%d" %
                                         val_from(frame, 180-168, 2)])

                        suffix = ["X+", "X-", "Y+", "Y-", "Z+", "Z-"]
                        for i, sfx in enumerate(suffix):
                            data.append(["Ток " + sfx, "%d" %
                                         val_from(frame, 182 + 2 * i - 168, 2, signed=True)])

                        for i in range(6):
                            data.append(["Вектор углов СД %d" % (i + 1), "%d" %
                                         val_from(frame, 194 + 2 * i - 168, 2)])
                            data.append(["Вектор углов ДГ %d" % (i + 1), "%d" %
                                         val_from(frame, 212 + 2 * i - 168, 2)])

                        for i in range(3):
                            data.append(["Вектор(%d) на Солнце в СК КА" % (i + 1), "%d" %
                                         val_from(frame, 206 + 2 * i - 168, 2, signed=True)])
                            data.append(["Вектор(%d) на Землю в СК КА" % (i + 1), "%d" %
                                         val_from(frame, 224 + 2 * i - 168, 2, signed=True)])

                        data.append(["время ТМИ3 (мс)", "%d" %
                                     val_from(frame, 230 - 168, 4)])
                        data.append(["резерв 5", "%d" %
                                     val_from(frame, 234 - 168, 4)])
                        data.append(["резерв 6", "%d" %
                                     val_from(frame, 238-168, 4)])
                        # data.append(["резерв 7", "%d" %
                        #              val_from(frame, 242-156, 2)])
                        data.append(["резерв 8", "%d" %
                                     val_from(frame, 242 - 168, 1)])

                        data.append(["Target 1 (X, Y, Z)", "(%d, %d, %d)" %
                                     (val_from(frame, 243 - 168, 1, signed=True),
                                      val_from(frame, 244 - 168, 1, signed=True),
                                      val_from(frame, 245 - 168, 1, signed=True))])
                        data.append(["Vector KA 1 (X, Y, Z)", "(%d, %d, %d)" %
                                     (val_from(frame, 246 - 168, 1, signed=True),
                                      val_from(frame, 247 - 168, 1, signed=True),
                                      val_from(frame, 248 - 168, 1, signed=True))])
                        data.append(["Target 2 (X, Y, Z)", "(%d, %d, %d)" %
                                     (val_from(frame, 249 - 168, 1, signed=True),
                                      val_from(frame, 250 - 168, 1, signed=True),
                                      val_from(frame, 251 - 168, 1, signed=True))])
                        data.append(["Vector KA 2 (X, Y, Z)", "(%d, %d, %d)" %
                                     (val_from(frame, 252 - 168, 1, signed=True),
                                      val_from(frame, 253 - 168, 1, signed=True),
                                      val_from(frame, 254 - 168, 1, signed=True))])

                        data.append(["Set_Rotation_Com_Status", "%d" %
                                     val_from(frame, 255 - 168, 1)])

                        data.append(["W(X, Y, Z)", "(%d, %d, %d)" %
                                     (val_from(frame, 256 - 168, 1, signed=True),
                                      val_from(frame, 257 - 168, 1, signed=True),
                                      val_from(frame, 258 - 168, 1, signed=True))])

                        try:
                            stats = [ADCS_status[val_from(frame, 285 - 168, 1)],
                                     ADCS_status[val_from(frame, 287 - 168, 1)],
                                     ADCS_status[val_from(frame, 290 - 168, 1)]]
                        except:
                            stats = [val_from(frame, 285 - 168, 1),
                                     val_from(frame, 287 - 168, 1),
                                     val_from(frame, 290 - 168, 1)]

                        data.append(["cam_photo_status", stats[0]])
                        data.append(["ss_photo_status", stats[1]])
                        data.append(["hs_photo_status", stats[1]])

                        data.append(["cam_photo_command", "0x%02X" %
                                     val_from(frame, 286 - 168, 1)])
                        data.append(["ss_photo_command", "0x%02X" %
                                     val_from(frame, 288 - 168, 2)])
                        data.append(["hs_photo_command", "0x%02X" %
                                     val_from(frame, 291 - 168, 2)])

                        data.append(["версия прошивки", "%d" %
                                     val_from(frame, 293 - 168, 1)])
                    elif id_loc_data["data_code"] == TMI5_pack_t or \
                            id_loc_data["data_code"] == LOG_TMI5_rec:
                        data.append(["Тип данных", "ТМИ 5"])
                        if id_loc_data["data_code"] == TMI5_pack_t or not first_loc_flag:
                            data.append(["Высота", "%d" %
                                         val_from(frame, 308-296, 8, to_double=True)])

                        data.append(["Широта", "%d" %
                                     val_from(frame, 316-296, 8, to_double=True)])
                        data.append(["Долгота", "%d" %
                                     val_from(frame, 324-296, 8, to_double=True)])
                        data.append(["Горизонтальная скорость", "%d" %
                                     val_from(frame, 332-296, 8, to_double=True)])
                        data.append(["Азимут горизонтальной скорости", "%d" %
                                     val_from(frame, 340-296, 8, to_double=True)])
                        data.append(["Вертикальная скорость", "%d" %
                                     val_from(frame, 348-296, 8, to_double=True)])

                        data.append(["Время ГЛОНАСС (ЧЧ:ММ:СС.МС)", "%d:%d:%d.%d" %
                                     (val_from(frame, 359-296, 1),
                                      val_from(frame, 360-296, 1),
                                      val_from(frame, 361-296, 1),
                                      val_from(frame, 362-296, 1))])

                        data.append(["Дата ГЛОНАСС (ДД.ММ.ГГ)", "%d.%d.%d" %
                                     (val_from(frame, 358-296, 1),
                                      val_from(frame, 357-296, 1),
                                      val_from(frame, 356-296, 1))])

                        gnss_val = val_from(frame, 363-296, 1)
                        data.append(["Валидность данных ГЛОНАСС", str(bool(gnss_val & 0x80))])
                        data.append(["Количество спутников", "%d" % (gnss_val & (~0x80))])

                        for i in range(6):
                            data.append(["Ускорение ДСГ %d (X, Y, Z)" % (i + 1), "(%d, %d, %d)" %
                                         (val_from(frame, 364-296 + 6 * i, 2, signed=True),
                                          val_from(frame, 366-296 + 6 * i, 2, signed=True),
                                          val_from(frame, 368-296 + 6 * i, 2, signed=True))])

                        data.append(["Ускорение СОП (X, Y, Z)", "(%d, %d, %d)" %
                                     (val_from(frame, 400-296, 2, signed=True),
                                      val_from(frame, 402-296, 2, signed=True),
                                      val_from(frame, 404-296, 2, signed=True))])

                        data.append(["Температуры СОП", "%d, %d, %d, %d" %
                                     (val_from(frame, 406-296, 1, signed=True),
                                      val_from(frame, 407-296, 1, signed=True),
                                      val_from(frame, 408-296, 1, signed=True),
                                      val_from(frame, 409-296, 1, signed=True))])

                        data.append(["Время ТМИ5 (мс)", "%d" %
                                     val_from(frame, 410-296, 4)])
                        # data.append(["ТМИ5 резерв", "%d" %
                        #              val_from(frame, 414-296, 7)])
                        data.append(["Версия прошивки", "%d" %
                                     val_from(frame, 421-296, 1)])
                    elif id_loc_data["data_code"] == TMI6_pack_t or \
                            id_loc_data["data_code"] == LOG_TMI6_rec:
                        data.append(["Тип данных", "ТМИ 6"])

                        for i in range(6):
                            if (id_loc_data["data_code"] == TMI6_pack_t or not first_loc_flag) \
                                    and i == 0:

                                data.append(["Калиброванная угловая скорость ДСГ %d" % i, "(%d, %d, %d)" %
                                             (val_from(frame, 436-424 + 6 * i, 2, signed=True),
                                              val_from(frame, 438-424 + 6 * i, 2, signed=True),
                                              val_from(frame, 440-424 + 6 * i, 2, signed=True))])
                            data.append(["Калиброванные магнитометры ДСГ %d" % i, "(%d, %d, %d)" %
                                         (val_from(frame, 478-424 + 6 * i, 2, signed=True),
                                          val_from(frame, 480-424 + 6 * i, 2, signed=True),
                                          val_from(frame, 482-424 + 6 * i, 2, signed=True))])

                            data.append(["om_ss_angle ДСГ %d" % i, "%d" %
                                         val_from(frame, 520-424 + 4 * i, 4)])

                        data.append(["Калиброванная угловая скорость СОП", "(%d, %d, %d)" %
                                     (val_from(frame, 472-424, 2, signed=True),
                                      val_from(frame, 474-424, 2, signed=True),
                                      val_from(frame, 476-424, 2, signed=True))])

                        data.append(["Калиброванные магнитометры СОП", "(%d, %d, %d)" %
                                     (val_from(frame, 514-424, 2, signed=True),
                                      val_from(frame, 516-424, 2, signed=True),
                                      val_from(frame, 518-424, 2, signed=True))])

                        data.append(["время ТМИ6 (мс)", "%d" %
                                     val_from(frame, 544-424, 4)])
                        # data.append(["ТМИ6 резерв", "%d" %
                        #              val_from(frame, 548-424, 1)])
                        data.append(["Версия прошивки", "%d" %
                                     val_from(frame, 549-424, 1)])
                    elif id_loc_data["data_code"] == TMI9_pack_t or \
                            id_loc_data["data_code"] == LOG_TMI9_rec:
                        data.append(["Тип данных", "ТМИ 9"])
                        # data.append(["ТМИ9 резерв", "%d" %
                        #              val_from(frame, , 7)])

                        data.append(["время ТМИ9 (мс)", "%d" %
                                     val_from(frame, 571-552, 4)])

                        # todo: поправить описание, добавить hs_alg_data_t  hs[6];
                        data.append(["nadir", "%d, %d, %d" %
                                     (val_from(frame, 575-552, 2),
                                      val_from(frame, 577-552, 2),
                                      val_from(frame, 579-552, 2))])

                        data.append(["sun", "%d, %d, %d" %
                                     (val_from(frame, 571-552, 2),
                                      val_from(frame, 583-552, 2),
                                      val_from(frame, 585-552, 2))])

                        data.append(["mag", "%d, %d, %d" %
                                     (val_from(frame, 587-552, 2),
                                      val_from(frame, 589-552, 2),
                                      val_from(frame, 591-552, 2))])

                        data.append(["Версия прошивки", "%d" %
                                     val_from(frame, 677-552, 1)])
                    else:
                        data.append(["Неизвестный тип данных", "0"])

                    pack_crc = val_from(frame, 126, 2)
                    calc_crc = crc16_calc(frame, 126)
                    data.append(["frame CRC-16", "0x%04X" % pack_crc])
                    data.append(["calc CRC-16", "0x%04X" % calc_crc])
                    data.append(["Статус CRC", pack_crc == calc_crc])

                else:
                    #
                    data.append(["Метка кадра", "0x%04X" % val_from(frame, 0, 2)])
                    data.append(["Определитель", "0x%04X" % val_from(frame, 2, 2)])
                    #
                    data.append(["Неизвестный определитель", "0"])
            else:
                data.append(["Данные не распознаны", "0"])
            return data
    except Exception as error:
        print(error)
        return None


def get_id_loc_data(id_loc):
    """
    разбор переменной IdLoc
    :param id_loc: переменная, содржащая IdLoc по формату описания на протокол СМКА
    :return: кортеж значений полей переменной IdLoc: номер устройства, флаги записи, код данных
    """
    device_id = (id_loc >> 12) & 0xF
    flags = (id_loc >> 8) & 0xF
    data_id = (id_loc >> 0) & 0xFF
    return {"dev_id": device_id, "flags": flags, "data_code": data_id}


def val_from(frame, offset, leng, byteorder="little", signed=False, debug=False, to_double=False):
    """
    обертка для функции сбора переменной из оффсета и длины, пишется короче и по умолчанию значения самый используемые
    :param frame: лист с данными кадра
    :param offset: оффсет переменной в байтах
    :param leng: длина переменной в байтах
    :param byteorder: порядок следования байт в срезе ('little', 'big')
    :param signed: знаковая или не знаковая переменная (True, False)
    :param to_double: имеет ли переменная тип double (True, False)
    :return: интовое значение переменной
    """
    if to_double:
        byte_arr = bytes(frame[offset + 0:offset + leng])
        retval = struct.unpack('d', byte_arr)[0]
    else:
        retval = int.from_bytes(frame[offset + 0:offset + leng], byteorder=byteorder, signed=signed)

    if debug:
        if to_double:
            print(frame[offset + 0:offset + leng], retval)
        else:
            print(frame[offset + 0:offset + leng], " %04X" %
              int.from_bytes(frame[offset + 0:offset + leng], byteorder=byteorder, signed=signed))
    return retval


# алгоритм подсчета crc16 для кадра
crc16tab = [0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
            0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
            0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
            0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
            0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
            0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
            0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
            0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
            0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
            0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
            0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
            0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
            0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
            0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
            0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
            0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
            0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
            0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
            0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
            0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
            0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
            0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
            0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
            0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
            0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
            0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
            0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
            0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
            0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
            0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
            0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
            0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0]


def crc16_calc(buf, length):
    d = 1
    crc = 0x1D0F
    for i in range(length):
        index = ((crc >> 8) ^ buf[i + d]) & 0x00FF
        crc = (crc << 8) ^ crc16tab[index]
        crc &= 0xFFFF
        d = -d
    return crc


def crc16_ccitt(buf, length):
    crc = 0xFFFF
    for i in range(length):
        index = ((crc >> 8) ^ buf[i]) & 0x00FF
        crc = (crc << 8) ^ crc16tab[index]
        crc &= 0xFFFF
    return crc

if __name__ == '__main__':
    print(crc16_calc([0xAA, 0xBB, 0xCC, 0xDD], 4))
