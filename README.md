# head_controller v0.1

- [Desription](#description)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run](#run)
- [Commands](#commands)

## Description
This project provides sending ITMP-messages to "head" device via serial port.

The "head" device is capable of executing actions based on the commands it receives through the serial port.

To send commands from a PC to the head module, ITMP messages of type CALL are used. According to the ITMP protocol specification, a command is triggered by sending a request in the following format:

```
{
    "message_type": 8,
    "message": <message_number>,
    "procedure": <procedure_name>,
    "arguments": [<arguments list>]
}
```

This message must be sent via the serial port to initiate the desired action on the head module.



## Requirements

## Installation

## Run

## Commands

