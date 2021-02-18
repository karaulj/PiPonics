
import logging

import config_utils as ch

import serial


SERIAL_PORT = '/dev/ttyAMA0'    # PL011 UART (not default)
BAUDRATE = 115200
TIMEOUT = 3

BUFFER_SZ = 7   # 1 command byte, 1 idx byte, 4 payload bytes, 1 end frame byte
UART_CMDS = {
    # first tx byte is command (i.e. echo, shutdown, drive actuator)
    'ECHO'  : b'\xF0',
    'DRIVE' : b'\x0F'
}
END_BYTE    = b'\xFE'

class IOController(object):

    def __init__(self, description_file:str):
        self._logger = self._init_logging()
        self._actuator_lookup = self._get_actuator_lookup(description_file)
        self._ser = None
        self._timeout = None
    def __del__(self):
        self.shutdown_uart()

    def init_uart(self, port=SERIAL_PORT, baudrate:int=BAUDRATE, timeout:int=TIMEOUT):
        # get serial device
        try:
            self._timeout = timeout
            self._ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        except ValueError:
            self._logger.error(
                "Could not open serial port (port='{}', baud={}, timeout={})".format(port, baudrate, timeout)
            )
        except serial.SerialException as se:
            self._logger.exception("Could not find or create device '{}'".format(port), exc_info=True)
    def shutdown_uart(self):
        if self._ser:
            self._ser.close()

    def _init_logging(self):
        logger = logging.getLogger(__name__)
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')
        s_handler.setFormatter(formatter)

        logger.addHandler(s_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def _get_actuator_lookup(self, description_file:str):
        data = ch.get_json_file_contents(description_file)
        lookup = dict()
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
            payload_bytes = payload.to_bytes(length=4, byteorder='little', signed=False)
        except OverflowError:
            self._logger.error("Payload '{}' is not an unsigned 32-bit integer".format(payload))
            return None
        try:
            idx_byte = idx.to_bytes(length=1, byteorder='little', signed=False)
        except OverflowError:
            self._logger.error("Idx '{}' is not an unsigned 8-bit integer".format(idx))
            return None
        command_byte = UART_CMDS[command]
        return command_byte + idx_byte + payload_bytes + END_BYTE   # 'bytes' object

    def _uart_tx(self, command:str, idx:int, tx_payload:int, expected_rx_payload:int=0) -> bool:
        self._logger.debug("tx_payload param: {}".format(tx_payload))
        uart_bytes = self._generate_uart_bytes(command=command, idx=idx, payload=tx_payload)
        if uart_bytes is None:
            return False
        # send uart frame
        try:
            self._logger.info("Sending UART frame: {}".format(uart_bytes))
            num_bytes_sent = self._ser.write(uart_bytes)
        except AttributeError:
            self._logger.error("Serial device is not set up")
            return False
        except serial.SerialTimeoutException:
            self._logger.error("Could not send frame, timeout reached")
            return False
        if num_bytes_sent != BUFFER_SZ:
            self._logger.error("Supposed to send {} bytes, sent {}".format(BUFFER_SZ, num_bytes_sent))
        # receive echo back
        rx_bytes = self._ser.read(BUFFER_SZ)
        self._logger.debug("Received UART frame: {}".format(rx_bytes))
        if rx_bytes == b'':
            self._logger.error("Waited {} seconds, received empty frame".format(self._timeout))
            return False
        # expect rx command byte = tx command byte
        rx_cmd_byte = rx_bytes[0]
        if rx_cmd_byte != UART_CMDS[command]:
            self._logger.warning("Expected {} command byte, got {}".format(command, rx_cmd_byte))
        # expect rx end byte = tx end byte
        rx_end_byte = rx_bytes[6]
        if rx_end_byte != END_BYTE:
            self._logger.warning("Expected END final byte, got {}".format(rx_end_byte))
        # compare payload to expected
        rx_payload = int.from_bytes(rx_bytes[2:5], byteorder='little', signed=False)
        if rx_payload != expected_rx_payload:
            self._logger.error("Received payload {} doesn't match expected {}".format(rx_payload, expected_rx_payload))
            return False
        else:
            return True

    def uart_tx_echo(self, echo_val:int=100):
        # idx is ignored for ECHO cmd
        return self._uart_tx(
            command='ECHO',
            idx=0,
            tx_payload=echo_val,
            expected_rx_payload=echo_val
        )

    def uart_tx_drive(self, actuator_id:int, drive_val:int=1):
        return self._uart_tx(
            command='DRIVE',
            idx=actuator_id,
            tx_payload=drive_val,
            expected_rx_payload=0   # 0 for success, other for failure
        )
