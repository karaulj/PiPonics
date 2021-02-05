import json
import config_helper as ch

ERR_UNKNOWN = 0
ERR_ENTITY_NOT_EXISTS = -1
ERR_BAD_PARAM = -2


class StaticEntityManger:

    def __init__(self, entity_file):
        self._file = entity_file
        self._data = self._get_entity_data()

    def _get_entity_data(self):
        return ch.get_json_file_contents(self._file)

    """ SYSTEM METHODS """

    def get_all_systems(self):
        try:
            return json.dumps(self._data[ch.KEY_SYSTEMS])
        except KeyError:
            return ERR_ENTITY_NOT_EXISTS
        except:
            return ERR_UNKNOWN

    """ TANK METHODS """

    def get_tanks_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return ERR_BAD_PARAM
        except:
            return ERR_UNKNOWN
        try:
            systems = self._data[ch.KEY_SYSTEMS]
            for system in systems:
                if system[ch.KEY_UUID] == entity_uuid:
                    return json.dumps(system[ch.KEY_TANKS])
            return ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return ERR_ENTITY_NOT_EXISTS
        except:
            return ERR_UNKNOWN
        return None

    """ CROP METHODS """

    def get_crops_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return ERR_BAD_PARAM
        except:
            return ERR_UNKNOWN
        try:
            systems = self._data[ch.KEY_SYSTEMS]
            for system in systems:
                if system[ch.KEY_UUID] == entity_uuid:
                    return json.dumps(system[ch.KEY_CROPS])
            return ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return ERR_ENTITY_NOT_EXISTS
        except:
            return ERR_UNKNOWN
        return None

    """ ACTUATOR METHODS """

    def get_actuators_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return ERR_BAD_PARAM
        except:
            return ERR_UNKNOWN
        try:
            systems = self._data[ch.KEY_SYSTEMS]
        except KeyError:
            return ERR_ENTITY_NOT_EXISTS
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
            return ERR_UNKNOWN
        # iterate through crops
        try:
            for system in systems:
                crops = system[ch.KEY_CROPS]
                for crop in crops:
                    if crop[ch.KEY_UUID] == entity_uuid:
                        return json.dumps(crop[ch.KEY_ACTUATORS])
            return ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return ERR_ENTITY_NOT_EXISTS
        return None

    """ SENSOR METHODS """

    def get_sensors_from_uuid(self, entity_uuid):
        try:
            entity_uuid = str(entity_uuid)
        except TypeError:
            return ERR_BAD_PARAM
        except:
            return ERR_UNKNOWN
        try:
            systems = self._data[ch.KEY_SYSTEMS]
        except KeyError:
            return ERR_ENTITY_NOT_EXISTS
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
            return ERR_UNKNOWN
        # iterate through crops
        try:
            for system in systems:
                crops = system[ch.KEY_CROPS]
                for crop in crops:
                    if crop[ch.KEY_UUID] == entity_uuid:
                        return json.dumps(crop[ch.KEY_SENSORS])
            return ERR_ENTITY_NOT_EXISTS
        except KeyError:
            return ERR_ENTITY_NOT_EXISTS
        return None
