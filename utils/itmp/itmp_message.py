import cbor2
import logging

from .utils import hdlc_byte_stuff, crc8
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any


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


class ITMPMessage(ABC):
	def __init__(self, msg_type: ITMPMessageType, id: int):
		self.logger = logging.getLogger()
		self._type = msg_type
		self._id = id

	@property
	def type(self) -> ITMPMessageType:
		return self._type

	@property
	def id(self) -> int:
		return self._id

	@abstractmethod
	def to_dict(self) -> Dict[str, Any]:
		"""Translates Message object to dict."""
		pass
	
	@abstractmethod
	def to_list(self) -> List[Any]:
		pass
	
	@classmethod
	@abstractmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'ITMPMessage':
		"""Creates Message object from dict."""
		pass

	@classmethod
	@abstractmethod
	def from_list(cls, data: List[Any]) -> 'ITMPMessage':
		"""Creates the Message object from ist."""
		pass

	def to_hdlc(self, address: int = 0x08) -> bytes:
		"""Translates ITMP message to HDLC packet."""
		payload_dict = list(self.to_dict().values())
		cbor_payload = cbor2.dumps(payload_dict)
		
		escaped_payload = self._escape(cbor_payload)
		frame = bytes([address & 0xFF]) + escaped_payload
		frame += bytes([crc8.crc8_get(frame)])
		frame = hdlc_byte_stuff.bytes2hdlc(frame)

		print(f"FRAME: {bytes(frame)}")

		return frame

	@staticmethod
	def from_hdlc(frame: bytes) -> 'ITMPMessage':
		"""Build ITMP message from HDLC packet"""
		if len(frame) < 2 or frame[-1] != 0x7E:
			raise ValueError(f"[{datetime.now()}] ERROR: Failed to unpack HDLC frame: wrong packet format.\n")
		content = frame[:-1]
		if (content[0] == 0x7E):
			content = content[1:]

		if len(content) == 0:
			raise ValueError(f"[{datetime.now()}] ERROR: HDLC frame is too short ({len(content)} bytes).")
		
		print(f"frame: {frame}")
		print(f"content: {content}")
		cbor_payload = ITMPMessage._unescape(content)
		print(f"cbor payload: {cbor_payload}")
		if (crc8.crc8_get(cbor_payload[:-1]) != cbor_payload[-1]):
			raise ValueError(f"[{datetime.now()}] ERROR: Failed to unpack HDLC frame: failed CRC ({crc8.crc8_get(cbor_payload[:-1])} != {cbor_payload[-1]})\nFrame: {frame}")
		cbor_payload = cbor_payload[1:-1]
		payload_list = cbor2.loads(cbor_payload)
		

		if not isinstance(payload_list, list) or len(payload_list) < 1:
			raise ValueError("Failed to unpack HDLC frame: CBOR payload is not a list.")

		msg_type_value = payload_list[0]
		try:
			msg_type = ITMPMessageType(msg_type_value)
		except ValueError:
			raise ValueError(f"Unknown ITMP message type: {msg_type_value}")

		for cls in ITMPMessage.__subclasses__():
			if cls._supports_type(msg_type):
				return cls.from_list(payload_list)

		raise ValueError(f"Faille to find {msg_type} class.")

	@staticmethod
	def _escape(data: bytes) -> bytes:
		"""Byte stuffing (escaping) для избежания 0x7E в данных."""
		return hdlc_byte_stuff.byte_stuff(data)

	@staticmethod
	def _unescape(data: bytes) -> bytes:
		"""Удаление byte stuffing (unescaping)."""
		return hdlc_byte_stuff.unstuff_bytes(data)

	@staticmethod
	@abstractmethod
	def _supports_type(msg_type: ITMPMessageType) -> bool:
		"""Проверяет, поддерживает ли класс данный тип сообщения."""
		pass


class ITMPCallMessage(ITMPMessage):
	def __init__(self, id: int, procedure: str, arguments: List[int]):
		super().__init__(ITMPMessageType.CALL, id)
		self.procedure = procedure
		self.arguments = arguments

	def to_list(self) -> List[Any]:
		return [self.type.value, self.id, self.procedure, self.arguments]

	def to_dict(self) -> Dict[str, Any]:
		return {
			'type': self.type.value,
			'id': self.id,
			'procedure': self.procedure,
			'arguments': self.arguments
		}

	"""Creates call message from list. Expected list format: []"""
	@classmethod
	def from_list(cls, data: List[Any]) -> 'ITMPCallMessage':
		if len(data) != 4 or data[0] != ITMPMessageType.CALL.value:
			raise ValueError(f"Wrong message for ITMP message: wrong list size (caught: {len(data)}; expected: 4).")
		return cls(data[1], data[2], data[3])

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'ITMPCallMessage':
		if 'procedure' not in data or 'arguments' not in data:
			raise ValueError("Отсутствуют поля 'procedure' или 'arguments' в данных")
		return cls(data['id'], data['procedure'], data['arguments'])

	@staticmethod
	def _supports_type(msg_type: ITMPMessageType) -> bool:
		return msg_type == ITMPMessageType.CALL


class ITMPResultMessage(ITMPMessage):
	def __init__(self, id: int, result: List[int]):
		super().__init__(ITMPMessageType.RESULT, id)
		self.result = result

	def to_list(self) -> List[Any]:
		return [self.type.value, self.id, self.result]

	def to_dict(self) -> Dict[str, Any]:
		return {
			'type': self.type.value,
			'id': self.id,
			'result': self.result
		}
	
	@classmethod
	def from_list(cls, data: List[Any]) -> 'ITMPResultMessage':
		if len(data) != 3 or data[0] != ITMPMessageType.RESULT.value:
			raise ValueError("Неверный формат списка для ITMPResultMessage")
		return cls(data[1], data[2])

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'ITMPResultMessage':
		if 'result' not in data:
			raise ValueError("Отсутствует поле 'result' в данных")
		return cls(data['id'], data['result'])

	@staticmethod
	def _supports_type(msg_type: ITMPMessageType) -> bool:
		return msg_type == ITMPMessageType.RESULT


class ITMPDescribeMessage(ITMPMessage):
	def __init__(self, id: int, topic: str):
		super().__init__(ITMPMessageType.DESCRIBE, id)
		self.topic = topic

	def to_list(self):
		return [self.type.value, self.id, self.topic]

	def to_dict(self) -> Dict[str, Any]:
		return {
			'type': self.type.value,
			'id': self.id,
			'topic': self.topic
		}

	@classmethod
	def from_list(cls, data: List[Any]) -> 'ITMPDescribeMessage':
		if len(data) != 3 or data[0] != ITMPMessageType.DESCRIBE.value:
			raise ValueError("Неверный формат списка для ITMPDescribeMessage")
		return cls(data[1], data[2])

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'ITMPDescribeMessage':
		if 'topic' not in data:
			raise ValueError("Отсутствует поле 'topic' в данных")
		return cls(data['id'], data['topic'])

	@staticmethod
	def _supports_type(msg_type: ITMPMessageType) -> bool:
		return msg_type == ITMPMessageType.DESCRIBE


class ITMPDescriptionMessage(ITMPMessage):
	def __init__(self, id: int, description: List[str]):
		super().__init__(ITMPMessageType.DESCRIPTION, id)
		self.description = description

	def to_list(self) -> List[Any]:
		return [self.type.value, self.id, self.description]

	def to_dict(self) -> Dict[str, Any]:
		return {
			'type': self.type.value,
			'id': self.id,
			'description': self.description
		}

	@classmethod
	def from_list(cls, data: List[Any]) -> 'ITMPDescriptionMessage':
		if len(data) != 3 or data[0] != ITMPMessageType.DESCRIPTION.value:
			raise ValueError("Неверный формат списка для ITMPDescriptionMessage")
		return cls(data[1], data[2])

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'ITMPDescriptionMessage':
		if 'description' not in data:
			raise ValueError("Отсутствует поле 'description' в данных")
		return cls(data['id'], data['description'])

	@staticmethod
	def _supports_type(msg_type: ITMPMessageType) -> bool:
		return msg_type == ITMPMessageType.DESCRIPTION

