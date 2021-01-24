--DROP DATABASE IF EXISTS ponics;
DROP SCHEMA IF EXISTS sensor_data;
CREATE SCHEMA sensor_data;

CREATE TABLE sensor_data.sensor_template (
  timestamp timestamp without time zone,
  sensor_id VARCHAR(255)
)
