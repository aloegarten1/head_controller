import json
import serial
import time

from utils import com, itmp_serial


def set_port():
	ports = com.list_serial_ports()
	if not ports:
		print("COM-port was not found.")
		return None
	if len(ports) == 1:
		return ports[0]

	print("Available COM-ports:")
	for i in range(len(ports)):
		print(f" {i}. {ports[i]}")
	
	port_id = len(ports)
	print("Choose the COM-port to use (enter the number):", end=" ")
	while (port_id >= len(port_id)) or (port_id < 0):
		try:
			port_id = int(input())
		except TypeError as e:
			print("Please, enter the COM-port id:", end=" ")
	return ports[port_id]


def poll(serial_port):
	buffer = bytes(0)
	timeout = 2 # secs
	start = time.time()
	end = time.time()
	while (not buffer) and (end - start < timeout):
		print("Listening to COM...")
		buffer = serial_port.read(1024)
		print(buffer)
		end = time.time()
	
	if (end - start > timeout):
		print("TIMEOUT!")
	
	return buffer


def process_all_messages(port: serial.Serial, script: dict):
	'''
			for message in script["script"]:
		curr_msg = script[f"msg{0}"]
		type = curr_msg["type"]
		build_func = getattr(itmp_serial, f"build_itmp_hdlc_{type}_packet")
		curr_msg.pop("type")
		appendix = {"addr": script["addr"]}
		curr_msg.update(appendix)

		frame = build_func(**curr_msg)
		print(f"Sending HDLC frame: {frame}")
		port.write(frame)
		res = poll(port)
		print(res)
	'''

	for i in range(len(script["script"])):
		curr_msg = script["script"][i]
		msg_type = curr_msg["message_type"]
		build_func = getattr(itmp_serial, f"build_itmp_hdlc_{msg_type}_packet")
		curr_msg.pop("message_type")
		appendix = {"addr": script["addr"]}
		curr_msg.update(appendix)

		frame = build_func(**curr_msg)
		print(f"Sending HDLC frame: {frame}")
		# port.write(frame)
		# res = poll(port)
		# print(res)

def main():
	print(itmp_serial.build_hdlc_from_itmp(4, [itmp_serial.ITMPMessageType.DESCRIBE, 1, ""]))
	print(itmp_serial.read_itmp_hdlc_packet(b'\x04\x83\x06\x01`\xf7~'))
	script_path = "./resources/script1.json"

	print("Head controler launched.")
	
	'''
	port_name = set_port()
	if not port_name:
		print("Head controler was finalized.")
		return
	
	port = com.open_serial_port(port_name)
	print(f"Using port: {port_name}")
	'''

	port = None

	with open(script_path, "r") as fin:
		script = json.load(fin)
	
	addr = script["addr"]
	print(f"Using address: {addr}\n")

	process_all_messages(port, script)


if __name__ == "__main__":
	main()
	