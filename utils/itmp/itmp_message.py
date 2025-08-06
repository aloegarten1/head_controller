from enum import Enum

import cbor2

class ITMPMessageType(Enum):
	# Connection
	CONNECT = 0
	CONNECTED = 1
	DISCONNECT = 4

	# Error
	ERROR = 5

	# Description
	DESCRIBE = 6
	DESCRIPTION = 7

	# RPC
	CALL = 8

	# Result (Response)
	RESULT = 9

	# RPC Extended
	ARGUMENTS = 10
	PROGRESS = 11
	CANCEL = 12

	# PubSub
	EVENT = 13
	PUBLISH = 14
	SUBSCRIBE = 16
	UNSUBSCRIBE = 18
	
	MAX_TYPE = 19


class ITMPMessage:
    def __init__(self, msg_type: ITMPMessageType, msg_id: int):
        self.msg_type = msg_type
        self.msg_id = msg_id

    def get_id(self) -> int:
        return self.msg_id
    
    def get_type(self) -> ITMPMessageType:
        return self.msg_type
    
    def sreialize(self) -> bytes:
        return bytes([])

class ITMPCallMessage(ITMPMessage):
    def __init__(self, msg_type: ITMPMessageType, msg_id: int, procedure: str, args: list):
        super().__init__(msg_type, msg_id)
        self.procedure = procedure
        self.args = args
    
    def get_procedure(self) -> str:
        return self.procedure
    
    def get_args(self) -> list:
        return self.args
    
    def to_hdlc(self) -> bytes:
        return