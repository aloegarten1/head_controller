import cbor2
from serial import Serial

from . import hdlc_byte_stuff

from . import crc8
from enum import Enum

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


def build_hdlc_from_itmp(addr: int, packet: list):
	if (not isinstance(packet[0], ITMPMessageType)):
		raise ValueError
	
	packet[0] = packet[0].value
	serialized = bytes([addr]) + cbor2.dumps(packet)
	crc = crc8.crc8_get(serialized)
	serialized += bytes([crc])

	return hdlc_byte_stuff.bytes2hdlc(serialized)


def build_itmp_hdlc_call_packet(addr: int, message: int, procedure: str, args: list) -> bytes:
	packet = [ITMPMessageType.CALL, message, procedure, args]
	return build_hdlc_from_itmp(addr, packet)


def build_itmp_hdlc_describe_packet(addr: int, message: int, topic: str) -> bytes: 
	packet = [ITMPMessageType.DESCRIBE, message, topic]
	return build_hdlc_from_itmp(addr, packet)


def read_itmp_hdlc_packet(packet: bytes) -> list:
	if not (hex(packet[-1]) != 0x7E):
		print("SOS")
		return []
	
	unstuffed = hdlc_byte_stuff.unstuff_bytes(packet[:-1])
	if (crc8.crc8_get(unstuffed[:-1]) != unstuffed[-1]):
		raise RuntimeError(f"CRC8 failed.\nPacket: {packet}\nUnstuffed: {unstuffed}\nCRC8: {unstuffed[-1]}, expected: {crc8.crc8_get(unstuffed[:-1])}")
	
	itmp_packet = cbor2.loads(unstuffed[1:-1])
	return itmp_packet

def print_itmp_description_message(message: list):
	print(f'Topic: "{"\n".join(message[2])}"')


def print_itmp_result_message(message: list):
	print(f'Result: {message[2]}')


def print_itmp_message(message: bytes):
	decoded = read_itmp_hdlc_packet(message)
	if (len(message) == 0):
		return

	if (message[0] >= ITMPMessageType.MAX_TYPE.value):
		return

	print(f"Message type: {ITMPMessageType(decoded[0]).name}")
	print(f"Message id: {decoded[1]}")
	globals()[f"print_itmp_{ITMPMessageType(decoded[0]).name.lower()}_message"](decoded)
