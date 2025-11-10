from utils import head_device, json_parser
from enum import Enum
import logging


class AppMode(Enum):
    DEFAULT  = 0
    SCRIPT   = 1
    HARDCODE = 2
    REPL     = 3


class HeadLogic:
    def __init__(self, dev_name: str, mode: AppMode = AppMode.DEFAULT):
        self._dev = head_device.HeadDevice(dev_name=dev_name)
        self.mode = mode
        self.state = None
        self.is_running = False

        self.callback = None
        self.set_mode(self.mode)
        self.logger = logging.getLogger()
        self.filename = ""
    
    def start(self):
        self.is_running = True
        self.callback()

    def finalize(self):
        self.is_running = False

    def set_script(self, filename: str):
        self.filename = filename

    def set_mode(self, mode: AppMode) -> None:
        modes = {
            AppMode.DEFAULT: self.hardcode,
            AppMode.SCRIPT: self.script,
            AppMode.HARDCODE: self.hardcode,
            AppMode.REPL: self.repl,
        }

        self.callback = modes[mode]
    
    ''' Executing commands hardcoded in this method. '''
    def hardcode(self):
        self._dev.enable()
        self._dev.mot1_go(1000, 700, 0)
        for i in range(2):
            self._dev.mot1_go(800, 2000, 0)
            self._dev.mot1_go(1000, 2000, 0)
        self._dev.mot1_go(0, 2000, 0)

    ''' Executing commands from JSON file. '''
    def script(self) -> None:
        parser = json_parser.JSONParser(self.filename, self._dev)
        command = [0]
        while 1:
            command = parser.next()
            if len(command) == 0:
                break
            
            delay = self._dev.calc_delay(command)
            self._dev.send_call(
                procedure=command[0],
                args=command[1],
                delay=delay
            )

    ''' Executing command from argument. '''
    def repl(self, command: str):
        pass
