# PiPonics
A full-stack web server for controlling and monitoring an aquaponics/hydroponics system for the Raspberry Pi, containerized with Docker. The frontend is built using Angular and hosted with Apache, the backend is implemented in Python connected to a MariaDB SQL server to store all sensor readings. 


## System Overview
The web server presents aquaponics/hydroponics data from an SQL server and allows for system control in a simple web UI.

Hardware for aquaponics/hydroponics data collection (i.e. sensors, probes) and system actuation (i.e. lights, water pumps) can vary greatly from system to system and this web server is designed to be reusable. This abstraction is achieved through the _Data Collection Layer_ which is system-specific and can be replaced by a user implementation, provided it follows the informal interface defined in ***PLACEHOLDER***.

The default implementation for the _Data Collection Layer_ is a Python Serial/UART controller communicating with a ***PLACEHOLDER*** board based on the STM32 microcontroller, which acts as an I/O board.

## Configuration
All relevant settings should be specified in `settings.json`.

I have implemented a data collection solution for my purposes using a ***PLACEHOLDER*** board based on the STM32 microcontroller for sensor data collection and system control which communicates with the Raspberry Pi using UART. 


## Raspberry Pi OS Setup/Installation
This system has been tested on a Raspberry Pi 4.

1. Flash [Raspberry Pi OS](https://www.raspberrypi.org/software/) (formally Raspbian) to an SD card. I used the headless/lite version.
2. [Enable SSH on your Pi](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md).
3. (Optional) If planning to use WiFi instead of ethernet, follow [Raspberry Pi WiFi Headless Setup](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md).
2. Boot up your pi and SSH in.
3. 
