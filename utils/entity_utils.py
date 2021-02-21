import json
import logging

import config_utils as ch
from http_utils import APIErrors


class StaticEntityManger:

    def __init__(self, entity_file):
        self._logger = self._init_logging()
        self._file = entity_file
        self.data = self._get_entity_data()

    def _init_logging(self):
        logger = logging.getLogger(__name__)
        s_handler = logging.StreamHandler()
        s_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')
        s_handler.setFormatter(formatter)

        logger.addHandler(s_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def _get_entity_data(self):
        return ch.get_json_file_contents(self._file)

    """ SYSTEM METHODS """

    def get_all_systems(self):
        try:
            return json.dumps(self.data[ch.KEY_SYSTEMS])
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except:
            return APIErrors.ERR_UNKNOWN

    """ TANK METHODS """

    def get_tanks_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return APIErrors.ERR_BAD_PARAM
        except:
            return APIErrors.ERR_UNKNOWN
        try:
            systems = self.data[ch.KEY_SYSTEMS]
            for system in systems:
                if system[ch.KEY_UUID] == entity_uuid:
                    return json.dumps(system[ch.KEY_TANKS])
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except:
            return APIErrors.ERR_UNKNOWN
        return None

    """ CROP METHODS """

    def get_crops_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return APIErrors.ERR_BAD_PARAM
        except:
            return APIErrors.ERR_UNKNOWN
        try:
            systems = self.data[ch.KEY_SYSTEMS]
            for system in systems:
                if system[ch.KEY_UUID] == entity_uuid:
                    return json.dumps(system[ch.KEY_CROPS])
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except:
            return APIErrors.ERR_UNKNOWN
        return None

    """ ACTUATOR METHODS """

    def get_actuators_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return APIErrors.ERR_BAD_PARAM
        except:
            return APIErrors.ERR_UNKNOWN
        try:
            systems = self.data[ch.KEY_SYSTEMS]
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        # iterate through tanks
        try:
            for system in systems:
                tanks = system[ch.KEY_TANKS]
                for tank in tanks:
                    if tank[ch.KEY_UUID] == entity_uuid:
                        return json.dumps(tank[ch.KEY_ACTUATORS])
        except KeyError:
            pass
        except:
            return APIErrors.ERR_UNKNOWN
        # iterate through crops
        try:
            for system in systems:
                crops = system[ch.KEY_CROPS]
                for crop in crops:
                    if crop[ch.KEY_UUID] == entity_uuid:
                        return json.dumps(crop[ch.KEY_ACTUATORS])
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        return None

    """ SENSOR METHODS """

    def get_sensors_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return APIErrors.ERR_BAD_PARAM
        except:
            return APIErrors.ERR_UNKNOWN
        try:
            systems = self.data[ch.KEY_SYSTEMS]
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        # iterate through tanks
        try:
            for system in systems:
                tanks = system[ch.KEY_TANKS]
                for tank in tanks:
                    if tank[ch.KEY_UUID] == entity_uuid:
                        return json.dumps(tank[ch.KEY_SENSORS])
        except KeyError:
            pass
        except:
            return APIErrors.ERR_UNKNOWN
        # iterate through crops
        try:
            for system in systems:
                crops = system[ch.KEY_CROPS]
                for crop in crops:
                    if crop[ch.KEY_UUID] == entity_uuid:
                        return json.dumps(crop[ch.KEY_SENSORS])
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        return None
    def get_sensor_item_from_uuid(self, sensor_uuid):
        try:
            sensor_uuid = str(sensor_uuid)
        except TypeError:
            return APIErrors.ERR_BAD_PARAM
        except:
            return APIErrors.ERR_UNKNOWN
        try:
            systems = self.data[ch.KEY_SYSTEMS]
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        # iterate through tanks
        try:
            for system in systems:
                tanks = system[ch.KEY_TANKS]
                for tank in tanks:
                    sensors = tank[ch.KEY_SENSORS]
                    for sensor in sensors:
                        if sensor[ch.KEY_UUID] == sensor_uuid:
                            return sensor
        except KeyError:
            pass
        except:
            return APIErrors.ERR_UNKNOWN
        # iterate through crops
        try:
            for system in systems:
                crops = system[ch.KEY_CROPS]
                for crop in crops:
                    sensors = crop[ch.KEY_SENSORS]
                    for sensor in sensors:
                        if sensor[ch.KEY_UUID] == sensor_uuid:
                            return sensor
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return APIErrors.ERR_ENTITY_NOT_EXISTS
        return None
