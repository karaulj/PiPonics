export interface IActuator {
  uuid: string;
  type: string;
  system: string;
  tank_or_crop: string;
  nice_name?: string;
}
