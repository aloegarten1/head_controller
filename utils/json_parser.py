import json
import logging

from .head_device import HeadDevice

class JSONParser:
    def __init__(self, filename: str, dev: HeadDevice):
        self.filename = filename
        self.dev = dev
        self.logger = logging.getLogger()
        self.script = self._read_script(self.filename)
        print(self.script)
        self.current_id = 0
        
    def _read_script(self, filename) -> None:
        data = None
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                file.close()
        except Exception:
            self.logger.log(level=logging.FATAL, msg=f"Failed to open the JSON file: {filename}.")
            raise Exception(f"Failed to open the JSON file: {filename}. Failed to load or find.")
        
        if not ("script" in data):
            self.logger.log(level=logging.FATAL, msg=f"Failed to parse a script from the file: {filename}. Topic \"script\" was not found.")
            raise Exception(f"Failed to parse a script from the file: {filename}. Topic \"script\" was not found.")
        
        print("DATA: ", data)
        script = data["script"]
        if not isinstance(script, list):
            self.logger.log(level=logging.FATAL, msg=f"Failed to parse a script from the file: {filename}.")
            raise Exception(f"Failed to parse a script from the file: {filename}.")
        
        print("SCRIPT: ", script)
        
        return script

    def next(self) -> list:
        print(self.script)
        if self.current_id >= len(self.script):
            return []
        
        command = self.script[self.current_id]
        print("COMMAND:", command)
        self.current_id += 1
        return command
