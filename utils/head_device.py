from .itmp import *

import math
import time
from typing import List, Any


class HeadDevice:
    def __init__(self, dev_name: str):
        self.dev = itmp_serial.ITMPSerialDevice(dev_name)
        self._next_id = 0
        self._current_pos = 0

    def _get_next_id(self) -> int:
        id_val = self._next_id
        self._next_id += 1
        return id_val

    def _send_call_and_get_result(self, procedure: str, args: List[int]) -> itmp_message.ITMPMessage:
        msg_id = 1
        call_msg = itmp_message.ITMPCallMessage(msg_id, procedure, args)
        self.dev.write(call_msg)
        result_msg = self.dev.read()
        return result_msg

    def enable(self) -> List[Any]:
        res = self._send_call_and_get_result("enable", [])
        return res.to_list()[2]

    def mot1_pos(self) -> List[Any]:
        res = self._send_call_and_get_result("mot1/pos", [])
        return res.to_list()[2]

    def mot1_go(self, pos: int, velocity: int, accs: int) -> itmp_message.ITMPMessage:
        if velocity <= 0:
            raise ValueError("Velocity must be positive.")
        if accs < 0:
            raise ValueError("Accseleration must be positive.")
 
        delta = abs(pos - self._current_pos)
        if delta == 0:
            return
        
        if accs == 0:
            move_time = delta / velocity
        else:
            t_acc = velocity / accs
            d_acc = (velocity ** 2) / (2 * accs)
            if delta <= 2 * d_acc:
                move_time = 2 * math.sqrt(delta / accs)
            else:
                move_time = 2 * t_acc + (delta - 2 * d_acc) / velocity

        move_time += 0.5

        msg_id = 1
        call_msg = itmp_message.ITMPCallMessage(msg_id, "mot1/go", [pos, velocity, accs])
        self.dev.write(call_msg)

        time.sleep(move_time)

        res = self.dev.read()
        self._current_pos = self.mot1_pos()[0]
        return res.to_list()[2]