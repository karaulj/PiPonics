export interface ISensor {
  uuid: string;
  type: string;
  system: string;
  tank_or_crop: string;
  units?: string;
  nice_name?: string;
}
