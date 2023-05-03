from collections import namedtuple
from usb_can_bridge import MyUSBCANDevice

address = namedtuple('Address', ['var_id', 'offset', 'd_len'])

repeat_count = 10
write_read_offset = 0.05
read_read_offset = 0.01
next_addr_offset = 0.07
next_test_offset = next_addr_offset

data_timer_interval = 0.5
update_timer_interval = 1
unit_dev_id = 4

tmi_nums = [2, 3, 5, 6, 9]
tmi_offs = [40, 168, 296, 424, 552]


def check_id_var(id_var, addr):
    res1, rtr, res2, offset, var_id, dev_id = MyUSBCANDevice.process_id_var(id_var)
    if dev_id == 4 and var_id == addr.var_id and offset == addr.offset:
        return True
    return False
