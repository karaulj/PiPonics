
import logging

import config_utils as ch


class IOController(object):

    def __init__(self, description_file:str):
        self._logger = self._init_logging()
        self._sensors_lookup = self._get_sensor_lookup(description_file)

    def _init_logging(self):
        logger = logging.getLogger(__name__)
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')
        s_handler.setFormatter(formatter)

        logger.addHandler(s_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def _get_sensor_lookup(self, description_file:str):
        data = ch.get_json_file_contents(description_file)
        sensor_lookup = dict()
        try:
            systems = data[ch.KEY_SYSTEMS]
        except KeyError:
            return sensor_lookup
        for system in systems:
            for container_type in ch.CONTAINER_TYPES:
                containers = system[container_type]  # worst case is empty list
                for container in containers:
                    if ch.KEY_SENSORS in container:
                        for sensor in container[ch.KEY_SENSORS]:
                            sensor_lookup[sensor[ch.KEY_UUID]] = sensor[ch.KEY_SENSOR_ID]
        return sensor_lookup
