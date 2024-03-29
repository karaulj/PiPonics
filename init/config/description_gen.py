import os, sys
import logging
import json
import uuid

import config_utils as ch


logger = logging.getLogger(__name__)


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
        logger.warning("No '{}' property found in config file".format(ch.KEY_SYSTEMS))
        systems = []

    all_uuids = []

    # iterate through systems
    for i, system in enumerate(systems):
        # system-specific actuator/sensor count
        actuator_cnt = 0
        actuator_ids = []
        sensor_cnt = 0
        sensor_ids = []
        # get system name
        try:
            sys_name = system[ch.KEY_NAME].replace('/', '')
        except KeyError:
            sys_name = ch.get_default_system_name(i+1)
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_NAME] = sys_name
        logger.debug("Found system: '{}'".format(sys_name))
        # add uuid for system
        all_uuids, sys_uuid = generate_uuid(all_uuids)
        entity_lookup[ch.KEY_SYSTEMS][i][ch.KEY_UUID] = sys_uuid

        for container_type, container_type_singular in ch.CONTAINER_TYPES.items():
            # find containers (tanks or crops)
            try:
                containers = system[container_type]
            except KeyError:
                logger.warning("No '{}' property found for system '{}'".format(container_type, i+1))
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
                logger.debug("Found container: '{}'".format(container_name))
                # add uuid for container
                all_uuids, container_uuid = generate_uuid(all_uuids)
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_UUID] = container_uuid
                # add system name
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SYSTEM] = sys_name

                # find actuators
                try:
                    actuators = container[ch.KEY_ACTUATORS]
                except KeyError:
                    logger.warning("No '{}' property found for container '{}'".format(ch.KEY_ACTUATORS, j+1))
                    actuators = []
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS] = actuators
                # iterate through actuators
                for k, actuator in enumerate(actuators):
                    logger.debug("Found actuator #{}".format(k+1))
                    # get actuator type
                    try:
                        actuator_type = actuator[ch.KEY_TYPE]
                    except KeyError:
                        logger.warning("No '{}' property found for system '{}', container '{}', actuator #{}".format(ch.KEY_TYPE, sys_name, container_name, k+1))
                        continue
                    # get actuator drive type
                    try:
                        actuator[ch.KEY_ACTUATOR_DRIVE_TYPE]
                    except KeyError:
                        logger.warning("No '{}' property found for system '{}', container '{}', actuator #{}".format(ch.KEY_ACTUATOR_DRIVE_TYPE, sys_name, container_name, k+1))
                        continue
                    # add uuid for actuator
                    all_uuids, actuator_uuid = generate_uuid(all_uuids)
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][ch.KEY_UUID] = actuator_uuid
                    # add system name
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][ch.KEY_SYSTEM] = sys_name
                    # add container name
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][ch.KEY_TANK_OR_CROP] = container_name
                    # add actuator id
                    try:
                        actuator_id = entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][ch.KEY_ACTUATOR_ID]
                        if actuator_id in actuator_ids:
                            logger.error("Repeated actuator ID '{}' found for system '{}', container '{}', actuator '{}'".format(actuator_id, sys_name, container_name, actuator_type))
                    except KeyError:
                        while actuator_cnt in actuator_ids:
                            actuator_cnt += 1
                        actuator_id = actuator_cnt
                        entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_ACTUATORS][k][ch.KEY_ACTUATOR_ID] = actuator_id
                        actuator_cnt += 1
                    actuator_ids.append(actuator_id)

                # find sensors
                try:
                    sensors = container[ch.KEY_SENSORS]
                except KeyError:
                    logger.warning("No '{}' property found for container '{}'".format(ch.KEY_SENSORS, j+1))
                    sensors = []
                entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS] = sensors
                # iterate through sensors in container
                for k, sensor in enumerate(sensors):
                    logger.debug("Found sensor #{}".format(k+1))
                    # get sensor type
                    try:
                        sensor_type = sensor[ch.KEY_TYPE].replace('/', '')
                    except KeyError:
                        logger.warning("No '{}' property found for system '{}', container '{}', sensor #{}".format(ch.KEY_TYPE, sys_name, container_name, k+1))
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
                    entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][ch.KEY_TANK_OR_CROP] = container_name
                    # add sensor id
                    try:
                        sensor_id = entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][ch.KEY_SENSOR_ID]
                        if sensor_id in sensor_ids:
                            logger.error("Repeated sensor ID '{}' found for system '{}', container '{}', sensor '{}'".format(sensor_id, sys_name, container_name, sensor_type))
                    except KeyError:
                        while sensor_cnt in sensor_ids:
                            sensor_cnt += 1
                        sensor_id = sensor_cnt
                        entity_lookup[ch.KEY_SYSTEMS][i][container_type][j][ch.KEY_SENSORS][k][ch.KEY_SENSOR_ID] = sensor_id
                        sensor_cnt += 1
                    sensor_ids.append(sensor_id)

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
        logger.error("Internal Config file json data is null. Exiting")
        sys.exit(1)

    entity_lookup = generate_entity_contents(json_contents)

    if output_file is not None:
        with open(output_file, 'w') as f:
            f.write(json.dumps(entity_lookup, indent=2))
        logger.info("Wrote description file to '{}'".format(output_file))

    return 0


def _init_logging():
    s_handler = logging.StreamHandler()
    s_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s] %(message)s')
    s_handler.setFormatter(formatter)

    logger.addHandler(s_handler)
    logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    _init_logging
    logger.info("Starting description file generation")

    # get config file
    if os.getenv('CONFIG_FILE') != '':
        config_file = '/home/{}'.format(os.getenv('CONFIG_FILE'))
    else:
        logger.error("CONFIG_FILE environment variable is not set.")
        sys.exit(1)
    # get description file
    if os.getenv('DESCRIPTION_FILE') != '':
        output_file = '/common/{}'.format(os.getenv('DESCRIPTION_FILE'))
    else:
        logger.warning("DESCRIPTION_FILE environment variable is not set.")
        output_file = None

    # run main program
    generate_description_file(config_file, output_file=output_file)
    logger.info("description file generation finished successfully")
    sys.exit(0)
