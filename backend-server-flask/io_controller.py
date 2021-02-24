import struct
import logging
import time
import threading

import config_utils as ch
from http_utils import APIErrors

import serial


SERIAL_PORT = '/dev/ttyAMA0'    # PL011 UART (not default)
BAUDRATE = 115200
TIMEOUT = 3
BYTEORDER = 'little'
POST_FREQ = 300                 # time between sensor readings posts (seconds)
NULL_READING = 4294967296.0     # MCU max float val, no matching sensor id present

BUFFER_SZ = 6   # 1 command byte, 1 idx byte, 4 payload bytes, 1 end frame byte
UART_CMDS = {   # first tx byte is command (i.e. echo, shutdown, drive actuator)
    'ECHO'  : b'\xF0',
    'DRIVE' : b'\x0F',
    'READ'  : b'\x88'
}
END_BYTE    = b'\xFE'

class IOController(object):

    def __init__(self, sem, dal):
        self._sem = sem
        self._dal = dal
        self._logger = self._init_logging()
        self._actuator_lookup = self._get_actuator_lookup()
        self._sensor_items = self._get_sensor_items()
        self._dal = dal
        self._ser = None
        self._timeout = None
        self._read_stop_event = threading.Event()
        self._sens_read_thr = threading.Thread(
            target=self.post_readings_loop,
            args=(self._read_stop_event,)
        )
    def __del__(self):
        self.stop_read_thr()
        self.shutdown_uart()

    def start_read_thr(self):
        try:
            self._sens_read_thr.start()
        except AttributeError:
            pass
    def stop_read_thr(self):
        try:
            self._read_stop_event.set()
        except AttributeError:
            pass

    def init_uart(self, port=SERIAL_PORT, baudrate:int=BAUDRATE, timeout:int=TIMEOUT):
        # get serial device
        try:
            self._timeout = timeout
            self._ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            self._ser.reset_input_buffer()
        except ValueError:
            self._logger.error(
                "Could not open serial port (port='{}', baud={}, timeout={})".format(port, baudrate, timeout)
            )
        except serial.SerialException as se:
            self._logger.exception("Could not find or create device '{}'".format(port), exc_info=True)
    def shutdown_uart(self):
        try:
            self._ser.close()
        except AttributeError:
            pass

    def _init_logging(self):
        logger = logging.getLogger(__name__)
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')
        s_handler.setFormatter(formatter)

        logger.addHandler(s_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def _get_actuator_lookup(self):
        lookup = dict()
        # add two lookups for testing
        lookup["return0"] = 0xFF
        lookup["return1"] = 0xFE
        try:
            data = self._sem.data
        except AttributeError:
            return lookup
        try:
            systems = data[ch.KEY_SYSTEMS]
        except KeyError:
            return lookup
        for system in systems:
            for container_type in ch.CONTAINER_TYPES:
                for container in system[container_type]:    # worst case is empty list
                    try:
                        for actuator in container[ch.KEY_ACTUATORS]:
                            lookup[actuator[ch.KEY_UUID]] = actuator[ch.KEY_ACTUATOR_ID]
                    except KeyError:
                        pass
        return lookup

    def _get_sensor_items(self):
        items = []
        try:
            systems = self._sem.data[ch.KEY_SYSTEMS]
        except AttributeError:
            return items
        for system in systems:
            for container_type in ch.CONTAINER_TYPES:
                for container in system[container_type]:    # worst case is empty list
                    try:
                        items += container[ch.KEY_SENSORS]
                    except KeyError:
                        pass
        return items

    def _generate_uart_bytes(self, command:str, idx:int, payload:int):
        """Generates bytes to send via UART.

        Keyword arguments:
        command -- string denoting command to send. One of UART_CMDS.keys()
        idx     -- index (used for DRIVE cmd). Should be unsigned 8-bit int
        payload -- payload to send. Should be unsigned 32-bit int
        """
        if command not in UART_CMDS:
            self._logger.error("Invalid command passed: '{}'".format(command))
            return None
        if type(payload) != int:
            self._logger.error("Payload must be of type int, got '{}'".format(type(payload)))
            return None
        if type(idx) != int:
            self._logger.error("Idx must be of type int, got '{}'".format(type(payload)))
            return None
        try:
            payload_bytes = payload.to_bytes(length=4, byteorder=BYTEORDER, signed=False)
        except OverflowError:
            self._logger.error("Payload '{}' is not an unsigned 32-bit integer".format(payload))
            return None
        try:
            idx_byte = idx.to_bytes(length=1, byteorder=BYTEORDER, signed=False)
        except OverflowError:
            self._logger.error("Idx '{}' is not an unsigned 8-bit integer".format(idx))
            return None
        command_byte = UART_CMDS[command]
        return command_byte + idx_byte + payload_bytes   # 'bytes' object

    def _uart_tx(self, command:str, idx:int, tx_payload:int) -> int:
        """Send UART message to sensor board and get response.

        Keyword arguments:
        command -- string denoting command to send. One of UART_CMDS.keys()
        idx     -- index (used for DRIVE cmd). Should be unsigned 8-bit int
        tx_payload -- payload to send. Should be unsigned 32-bit int

        Returns:
        -1 if error occured
        4-byte return value otherwise
        """
        self._logger.debug("tx_payload param: {}".format(tx_payload))
        uart_bytes = self._generate_uart_bytes(command=command, idx=idx, payload=tx_payload)
        if uart_bytes is None:
            return -1
        # send uart frame
        try:
            self._logger.debug("Sending UART frame: {}".format(uart_bytes))
            num_bytes_sent = self._ser.write(uart_bytes)
        except AttributeError:
            self._logger.error("Serial device is not set up. Call init_uart() method")
            return -1
        except serial.SerialTimeoutException:
            self._logger.error("Could not send frame, timeout reached")
            return -1
        if num_bytes_sent != BUFFER_SZ:
            self._logger.error("Supposed to send {} bytes, sent {}".format(BUFFER_SZ, num_bytes_sent))
        # receive echo back
        rx_bytes = self._ser.read(BUFFER_SZ)
        self._logger.debug("Received UART frame: {}".format(rx_bytes))
        if rx_bytes == b'':
            self._logger.error("Waited {} seconds, received empty frame".format(self._timeout))
            return -1
        # expect rx command byte = tx command byte
        rx_cmd_byte = rx_bytes[0]
        if type(rx_cmd_byte) == int:
            rx_cmd_byte = rx_cmd_byte.to_bytes(1, byteorder=BYTEORDER)
        if rx_cmd_byte != UART_CMDS[command]:
            self._logger.warning("Expected {} command byte, got {}".format(command, rx_cmd_byte))
        """
        # expect rx end byte = tx end byte
        rx_end_byte = rx_bytes[BUFFER_SZ-1]
        if type(rx_end_byte) == int:
            rx_end_byte = rx_end_byte.to_bytes(1, byteorder=BYTEORDER)
        if rx_end_byte != END_BYTE:
            self._logger.warning("Expected END final byte, got {}".format(rx_end_byte))
        """
        # return response from sensor board
        return rx_bytes[2:BUFFER_SZ]        # bytes object

    def uart_tx_echo(self, echo_val:int=100):
        # idx is ignored for ECHO cmd
        ret_bytes = self._uart_tx(
            command='ECHO',
            idx=0,
            tx_payload=echo_val
        )
        try:
            ret_val = int.from_bytes(ret_bytes, byteorder=BYTEORDER, signed=False)
        except TypeError:
            return -1   # fail
        if ret_val != echo_val:
            self._logger.error("ECHO payload '{}' doesn't match expected '{}'".format(ret_val, echo_val))
            return -1   # fail
        else:
            return 0

    def uart_tx_drive(self, actuator_id:int, drive_val:int=1):
        ret_bytes = self._uart_tx(
            command='DRIVE',
            idx=actuator_id,
            tx_payload=drive_val
        )
        return int.from_bytes(ret_bytes, byteorder=BYTEORDER, signed=False)

    def uart_tx_read(self, sensor_id:int):
        ret_bytes = self._uart_tx(
            command='READ',
            idx=sensor_id,
            tx_payload=0
        )
        if ret_bytes == -1:
            return None
        ret_float = struct.unpack('<f', ret_bytes)  # little-endian
        if type(ret_float) == tuple:
            ret_float = ret_float[0]
        return ret_float

    def drive_actuator(self, actuator_uuid:str, drive_val:int=None):
        try:
            actuator_id = self._actuator_lookup[actuator_uuid]
        except KeyError:
            self._logger.error("No actuator id found for UUID {}".format(actuator_uuid))
            return APIErrors.ERR_BAD_ACTUATOR_PARAM
        if drive_val is None:
            return str(self.uart_tx_drive(actuator_id))
        else:
            try:
                drive_val = int(drive_val)
            except ValueError:
                return APIErrors.ERR_BAD_DRIVE_VAL_PARAM
            return str(self.uart_tx_drive(actuator_id, drive_val))

    def _get_reading(self, sensor_item:int):
        try:
            sensor_id = sensor_item[ch.KEY_SENSOR_ID]
        except KeyError:
            self._logger.error("Invalid sensor item, cannot get reading")
            return None
        return self.uart_tx_read(sensor_id)

    def post_readings_loop(self, thr_event):
        self._logger.info("Started sensor reading post thread")
        if self._dal is None:
            self._logger.error("DAL is not initialized. Exiting thread")
            return
        if not self._sensor_items:
            self._logger.info("No sensor items to gather readings for. Exiting thread")
            return
        while not thr_event.isSet():
            # post all sensor readings sequentially
            for sensor_item in self._sensor_items:
                reading = self._get_reading(sensor_item)
                #if reading is not None:
                if reading is not None and reading != NULL_READING:
                    self._dal.add_sensor_reading(sensor_item, reading)
            # wait before doing again
            time.sleep(POST_FREQ)
        self._logger.info("Exiting sensor reading post thread")
        return
