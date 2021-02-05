import os
import sys
import json
import uuid
import config_helper as ch


def get_sensor_units(json_data:dict, sensor_type:str) -> str:
    try:
        sensor_list = json_data[ch.KEY_METADATA][ch.KEY_METADATA_SENSORS]
        for sensor in sensor_list:
            if sensor[ch.KEY_METADATA_SENSORS_TYPE] == sensor_type:
                return sensor[ch.KEY_METADATA_SENSORS_UNITS]
        return None
    except:
        return None


def generate_uuid(all_uuids:list):
    new_uuid = str(uuid.uuid4())
    while new_uuid in all_uuids:
        new_uuid = str(uuid.uuid4())
    all_uuids.append(new_uuid)
    return all_uuids, new_uuid


def generate_entity_contents(json_data:dict, entity_lookup:dict=None) -> dict:
    """Return entity lookup table w/ generated UUIDs.

    Keyword arguments:
    json_data -- json object, root of config file (required).
    entity_lookup -- dictionary to write setup description to (typically copy of json_data).
    """

    # find systems
    try:
        systems = json_data[ch.KEY_SYSTEMS]
    except KeyError:
        print("No '{}' property found in config file".format(ch.KEY_SYSTEMS))
        return entity_lookup   # return data if no systems found

    all_uuids = []

    # iterate through systems
    for i, system in enumerate(systems):
        # get system name
        try:
            sys_name = system[ch.KEY_SYSTEMS_NAME].replace('/', '')
        except KeyError:
            sys_name = ch.get_default_system_name(i+1)
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_SYSTEMS_NAME] = sys_name
        print("Found system: '{}'".format(sys_name))
        # add uuid for system
        all_uuids, sys_uuid = generate_uuid(all_uuids)
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_UUID] = sys_uuid

        # find tanks
        try:
            tanks = system[ch.KEY_TANKS]
        except KeyError:
            print("No '{}' property found for system '{}'".format(ch.KEY_TANKS, i+1))
            tanks = []
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS] = tanks

        # iterate through tanks in system
        for j, tank in enumerate(tanks):
            # get tank name
            try:
                tank_name = "{}".format(tank[ch.KEY_TANKS_NAME].replace('/', ''))
            except KeyError:
                tank_name = ch.get_default_tank_name(j+1)
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_TANKS_NAME] = tank_name
            print("Found tank: '{}'".format(tank_name))
            # add uuid for tank
            all_uuids, tank_uuid = generate_uuid(all_uuids)
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_UUID] = tank_uuid
            # add system name
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_SYSTEM] = sys_name

            # find actuators
            try:
                actuators = tank[ch.KEY_ACTUATORS]
            except KeyError:
                print("No '{}' property found for tank '{}'".format(ch.KEY_ACTUATORS, j+1))
                actuators = []
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_ACTUATORS] = actuators
            # iterate through actuators
            for k in range(len(actuators)):
                print("Found actuator #{}".format(k+1))
                # add uuid for actuator
                all_uuids, actuator_uuid = generate_uuid(all_uuids)
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_ACTUATORS][k][ch.KEY_UUID] = actuator_uuid
                # add system name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_ACTUATORS][k][ch.KEY_SYSTEM] = sys_name
                # add tank name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_ACTUATORS][k][ch.KEY_TANK] = tank_name

            # find sensors
            try:
                sensors = tank[ch.KEY_SENSORS]
            except KeyError:
                print("No '{}' property found for tank '{}'".format(ch.KEY_SENSORS, j+1))
                sensors = []
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_SENSORS] = sensors
            # iterate through sensors in tank
            for k, sensor in enumerate(sensors):
                print("Found sensor #{}".format(k+1))
                # get sensor type
                try:
                    sensor_type = sensor[ch.KEY_SENSORS_TYPE].replace('/', '')
                except KeyError:
                    print("No '{}' property found for system '{}', tank '{}', sensor #{}".format(ch.KEY_SENSORS_TYPE, sys_name, tank_name, k+1))
                    continue
                # add uuid for sensor
                all_uuids, sensor_uuid = generate_uuid(all_uuids)
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_SENSORS][k][ch.KEY_UUID] = sensor_uuid
                # add sensor units
                try:
                    entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_SENSORS][k][ch.KEY_SENSORS_UNITS] = sensor[ch.KEY_SENSORS_UNITS]
                except KeyError:
                    entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_SENSORS][k][ch.KEY_SENSORS_UNITS] = get_sensor_units(json_data, sensor_type)
                # add system name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_SENSORS][k][ch.KEY_SYSTEM] = sys_name
                # add tank name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_TANKS][j][ch.KEY_SENSORS][k][ch.KEY_TANK] = tank_name


        # find crops
        try:
            crops = system[ch.KEY_CROPS]
        except KeyError:
            print("No '{}' property found for system '{}'".format(ch.KEY_CROPS, i+1))
            crops = []
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS] = crops

        # iterate through crops in system
        for j, crop in enumerate(crops):
            # get crop name
            try:
                crop_name = "{}".format(crop[ch.KEY_CROPS_NAME].replace('/', ''))
            except KeyError:
                crop_name = ch.get_default_crop_name(j+1)
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_CROPS_NAME] = crop_name
            print("Found crop: '{}'".format(crop_name))
            # add uuid for crop
            all_uuids, crop_uuid = generate_uuid(all_uuids)
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_UUID] = crop_uuid
            # add system name
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_SYSTEM] = sys_name

            # find actuators
            try:
                actuators = crop[ch.KEY_ACTUATORS]
            except KeyError:
                print("No '{}' property found for crop '{}'".format(ch.KEY_ACTUATORS, j+1))
                actuators = []
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_ACTUATORS] = actuators
            # iterate through actuators
            for k in range(len(actuators)):
                print("Found actuator #{}".format(k+1))
                # add uuid for actuator
                all_uuids, actuator_uuid = generate_uuid(all_uuids)
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_ACTUATORS][k][ch.KEY_UUID] = actuator_uuid
                # add system name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_ACTUATORS][k][ch.KEY_SYSTEM] = sys_name
                # add crop name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_ACTUATORS][k][ch.KEY_CROP] = crop_name

            # find sensors
            try:
                sensors = crop[ch.KEY_SENSORS]
            except KeyError:
                print("No '{}' property found for crop '{}'".format(ch.KEY_SENSORS, j+1))
                sensors = []
            entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_SENSORS] = sensors
            # iterate through sensors in crop
            for k, sensor in enumerate(sensors):
                print("Found sensor #{}".format(k+1))
                # get sensor type
                try:
                    sensor_type = sensor[ch.KEY_SENSORS_TYPE].replace('/', '')
                except KeyError:
                    print("No '{}' property found for system '{}', tank '{}', sensor #{}".format(ch.KEY_SENSORS_TYPE, sys_name, tank_name, k+1))
                    continue
                # add uuid for sensor
                all_uuids, sensor_uuid = generate_uuid(all_uuids)
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_SENSORS][k][ch.KEY_UUID] = sensor_uuid
                # add sensor units
                try:
                    entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_SENSORS][k][ch.KEY_SENSORS_UNITS] = sensor[ch.KEY_SENSORS_UNITS]
                except KeyError:
                    entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_SENSORS][k][ch.KEY_SENSORS_UNITS] = get_sensor_units(json_data, sensor_type)
                # add system name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_SENSORS][k][ch.KEY_SYSTEM] = sys_name
                # add crop name
                entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_CROPS][j][ch.KEY_SENSORS][k][ch.KEY_CROP] = crop_name

    return entity_lookup


def main(config_file:str, entity_file:str=None) -> int:
    """ Generates a description json file containing uuids for all entities. Expects a config json file at /home/$CONFIG_FILE.

    Keyword arguments:
    config_file -- path to config json file (required).
    entity_file -- filename of output description json. Omits writing if None (default).
    """
    json_contents = ch.get_json_file_contents(config_file)
    if json_contents is None:
        print("Internal Error: Config file json data is null. Exiting")
        sys.exit(1)

    entity_lookup = generate_entity_contents(json_contents, entity_lookup=json_contents)

    if entity_file is not None:
        with open(entity_file, 'w') as f:
            f.write(json.dumps(entity_lookup, indent=2))
        print("Wrote description file to '{}'".format(entity_file))

    return 0


if __name__ == "__main__":
    print("Starting description file generation")

    # get config file
    if os.getenv('CONFIG_FILE') != '':
        config_file = '/home/{}'.format(os.getenv('CONFIG_FILE'))
    else:
        print("Error: CONFIG_FILE environment variable is not set.")
        sys.exit(1)
    # get description file
    if os.getenv('DESCRIPTION_FILE') != '':
        entity_file = '/common/{}'.format(os.getenv('DESCRIPTION_FILE'))
    else:
        entity_file = None

    # run main program
    main(config_file, entity_file=entity_file)  # write changes to config file
    print("description file generation finished successfully")
    sys.exit(0)
