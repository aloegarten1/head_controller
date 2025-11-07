from .itmp import *

import logging
import math
import time
import pywintypes
from typing import List, Any


class HeadDevice:
    def __init__(self, dev_name: str):
        self.logger = logging.getLogger(__name__)
        try:
            self.dev = itmp_serial.ITMPSerialDevice(dev_name)
        except pywintypes.error:
            self.logger.log(logging.FATAL, msg="Failed to connect the head device.")
            raise Exception("Failed to connect the head device.")
        self.logger.log(level=logging.INFO, msg="Head device was connected successfully.")
        self._next_id = 0
        self._current_pos = 0

    def _get_next_id(self) -> int:
        id_val = self._next_id
        self._next_id += 1
        return id_val

    def _send_call_and_get_result(self, procedure: str, args: List[int]) -> itmp_message.ITMPMessage:
        print(f"PROC: {procedure} // ARGS: {args}")
        msg_id = 1
        call_msg = itmp_message.ITMPCallMessage(msg_id, procedure, args)
        self.dev.write(call_msg)
        result_msg = self.dev.read()

        return result_msg

    def adc_p(self) -> List[Any]:
        res = self._send_call_and_get_result("adc/p", [])
        return res.to_list()[2]

    def enable(self) -> List[Any]:
        res = self._send_call_and_get_result("enable", [])
        return res.to_list()[2]

    def mot1_pos(self) -> List[Any]:
        res = self._send_call_and_get_result("mot1/pos", [])
        return res.to_list()[2]

    def pwm(self, pwm_id: int, val: int) -> List[Any]:
        res = self._send_call_and_get_result(f"pwm{pwm_id}", [val])
        print(f"pwm{pwm_id}")
        return res.to_list()[2]
    
    def set_valves(self, valve1: int, valve2: int) -> List[Any]:
        to_send = (12, (valve1 * 2 + valve2) * 4)
        res = self._send_call_and_get_result("gpio", to_send)
        return res.to_list()

    def descr(self, topic) -> dict:
        msg_id = 1
        describe_msg = itmp_message.ITMPDescribeMessage(msg_id, topic)
        self.dev.write(describe_msg)
        result_msg = self.dev.read()
        return result_msg.to_dict()

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

        move_time += 0.08

        msg_id = 1
        call_msg = itmp_message.ITMPCallMessage(msg_id, "mot1/go", [pos, velocity, accs])
        self.dev.write(call_msg)

        time.sleep(move_time)

        res = self.dev.read()
        self._current_pos = pos

        return res.to_list()[2]