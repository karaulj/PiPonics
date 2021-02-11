import os
import sys
import json
import uuid
import config_helper as ch


def generate_uuid(all_uuids:list):
    new_uuid = str(uuid.uuid4())
    while new_uuid in all_uuids:
        new_uuid = str(uuid.uuid4())
    all_uuids.append(new_uuid)
    return all_uuids, new_uuid


def generate_entity_contents(json_data:dict) -> dict:
    """Return entity lookup table w/ generated UUIDs.

    Keyword arguments:
    json_data -- json object, root of config file (required).
    """
    entity_lookup = json_data

    # find systems
    try:
        systems = json_data[ch.KEY_SYSTEMS]
    except KeyError:
        print("No '{}' property found in config file".format(ch.KEY_SYSTEMS))
        systems = []

    all_uuids = []

    # iterate through systems
    for i, system in enumerate(systems):
        # get system name
        try:
            sys_name = system[ch.KEY_NAME].replace('/', '')
        except KeyError:
            sys_name = ch.get_default_system_name(i+1)
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_NAME] = sys_name
        print("Found system: '{}'".format(sys_name))
        # add uuid for system
        all_uuids, sys_uuid = generate_uuid(all_uuids)
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_UUID] = sys_uuid

        for container_type, container_type_singular in ch.CONTAINER_TYPES.items():
            # find containers (tanks or crops)
            try:
                containers = system[container_type]
            except KeyError:
                print("No '{}' property found for system '{}'".format(container_type, i+1))
                containers = []
            entity_lookup[ch.KEY_SYSTEMS][i][container_type] = containers

            # iterate through containers of type tank or crop in system
            for j, container in enumerate(containers):
                # get container name
                try:
                    container_name = "{}".format(container[ch.KEY_NAME].replace('/', ''))
                except KeyError:
                    container_name = ch.get_default_container_name(container_type, j+1)
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_NAME] = container_name
                print("Found container: '{}'".format(container_name))
                # add uuid for container
                all_uuids, container_uuid = generate_uuid(all_uuids)
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_UUID] = container_uuid
                # add system name
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SYSTEM] = sys_name

                # find actuators
                try:
                    actuators = container[ch.KEY_ACTUATORS]
                except KeyError:
                    print("No '{}' property found for container '{}'".format(ch.KEY_ACTUATORS, j+1))
                    actuators = []
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS] = actuators
                # iterate through actuators
                for k, actuator in enumerate(actuators):
                    print("Found actuator #{}".format(k+1))
                    # get actuator type
                    try:
                        actuator[ch.KEY_TYPE]
                    except KeyError:
                        print("No '{}' property found for system '{}', container '{}', actuator #{}".format(ch.KEY_TYPE, sys_name, container_name, k+1))
                        continue
                    # add uuid for actuator
                    all_uuids, actuator_uuid = generate_uuid(all_uuids)
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][ch.KEY_UUID] = actuator_uuid
                    # add system name
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][ch.KEY_SYSTEM] = sys_name
                    # add container name
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][container_type_singular] = container_name

                # find sensors
                try:
                    sensors = container[ch.KEY_SENSORS]
                except KeyError:
                    print("No '{}' property found for container '{}'".format(ch.KEY_SENSORS, j+1))
                    sensors = []
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS] = sensors
                # iterate through sensors in container
                for k, sensor in enumerate(sensors):
                    print("Found sensor #{}".format(k+1))
                    # get sensor type
                    try:
                        sensor_type = sensor[ch.KEY_TYPE].replace('/', '')
                    except KeyError:
                        print("No '{}' property found for system '{}', container '{}', sensor #{}".format(ch.KEY_TYPE, sys_name, container_name, k+1))
                        continue
                    # add uuid for sensor
                    all_uuids, sensor_uuid = generate_uuid(all_uuids)
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][ch.KEY_UUID] = sensor_uuid
                    # add sensor units
                    try:
                        entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][ch.KEY_SENSORS_UNITS] = sensor[ch.KEY_SENSORS_UNITS]
                    except KeyError:
                        entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][ch.KEY_SENSORS_UNITS] = ch.get_sensor_units(json_data, sensor_type)
                    # add system name
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][ch.KEY_SYSTEM] = sys_name
                    # add container name
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][container_type_singular] = container_name

                # delete empty sensors from list (if any)
                all_sensors = entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS]
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS] = [sensor for sensor in all_sensors if sensor != {}]
                # delete empty actuators from list (if any)
                all_actuators = entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS]
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS] = [actuator for actuator in all_actuators if actuator != {}]

    return entity_lookup


def generate_description_file(config_file:str, output_file:str=None) -> int:
    """ Generates a description json file containing uuids for all entities. Expects a config json file at /home/$CONFIG_FILE.

    Keyword arguments:
    config_file -- path to config json file (required).
    output_file -- filename of output description json. Omits writing if None (default).
    """
    json_contents = ch.get_json_file_contents(config_file)
    if json_contents is None:
        print("Internal Error: Config file json data is null. Exiting")
        sys.exit(1)

    entity_lookup = generate_entity_contents(json_contents)

    if output_file is not None:
        with open(output_file, 'w') as f:
            f.write(json.dumps(entity_lookup, indent=2))
        print("Wrote description file to '{}'".format(output_file))

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
        output_file = '/common/{}'.format(os.getenv('DESCRIPTION_FILE'))
    else:
        print("Warning: DESCRIPTION_FILE environment variable is not set.")
        output_file = None

    # run main program
    generate_description_file(config_file, output_file=output_file)
    print("description file generation finished successfully")
    sys.exit(0)
