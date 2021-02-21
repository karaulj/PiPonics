import { ISensor } from './sensor';
import { IActuator } from './actuator';

export interface ICrop {
  uuid: string;
  name: string;
  system: string;
  nice_name?: number;
  sensors: ISensor[];
  actuators: IActuator[];
}
