# head_controller v0.1

- [Desription](#description)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run](#run)
- [Commands](#commands)

## Description
This project provides sending commands to "head" device via serial port.

The "head" device is capable of executing actions based on the commands it receives through the serial port.

To send commands from a PC to the head module, ITMP messages of type CALL are used. According to the ITMP protocol specification, a command is triggered by sending a request in the following format:

```
[CALL, Request:id, Procedure:uri, Arguments]
```

## Requirements

- OS: Windows 7+
- Python 3.x.x
- Git

## Installation

1. Open PowerShell and go to the desired directory.
2. Clone this repo:
```
git clone https://github.com/aloegarten1/head_controller.git
```
3. Run "build" script (it will create virtual environment and install required libraries).
```
.\build.ps1
```

## Run

## Commands

