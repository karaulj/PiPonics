# PiPonics
PiPonics is a web-based framework for monitoring and controlling an aquaponics/hydroponics system using a Raspberry Pi. It includes a full-stack web server with a web UI using Angular and hosted with Apache, while the backend is implemented in Python using Flask connected to a MariaDB SQL server to store all sensor readings. 
***NOTE: PiPonics is currently designed for local hosting only. Host to the internet at your own risk.***


## System Overview
The web server presents aquaponics/hydroponics data from an SQL server and allows for system control in a simple web UI.

Hardware for aquaponics/hydroponics data collection (i.e. sensors, probes) and system actuation (i.e. lights, water pumps) can vary greatly from system to system and this web server is designed to be reusable. This abstraction is achieved through the _Data Collection Layer_ which is system-specific and can be replaced by a user implementation, provided it follows the informal interface defined in ***PLACEHOLDER***.

The default implementation for the _Data Collection Layer_ is a Python Serial/UART controller communicating with a ***PLACEHOLDER*** board based on the STM32 microcontroller, which acts as an I/O board. The firmware for this board is maintained in a separate project: ***PLACEHOLDER***.


## Configuration
All relevant settings should be specified in `settings.json`.


## Setup/Installation

### Raspberry Pi
This system has been tested on a Raspberry Pi 4.

1. Flash [Raspberry Pi OS](https://www.raspberrypi.org/software/) (formally Raspbian) to an SD card. I used the headless/lite version.
2. [Enable SSH on your Pi](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md). Instructions for a headless install can be found at the bottom of the page.
3. (Optional) If planning to use WiFi instead of ethernet, follow [Raspberry Pi WiFi Headless Setup](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md).
2. Boot up your pi and SSH in.
3. 
