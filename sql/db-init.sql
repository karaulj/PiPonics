--DROP DATABASE IF EXISTS ponics;
DROP SCHEMA IF EXISTS ponics;
CREATE SCHEMA ponics;

CREATE TABLE ponics.sensor_data (
  timestamp timestamp without time zone,
  sensor_id VARCHAR(255)
)
