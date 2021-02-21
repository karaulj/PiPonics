import { ITank } from './tank';
import { ICrop } from './crop';

export interface ISystem {
  uuid: string;
  name: string;
  nice_name?: number;
  tanks: ITank[];
  crops: ICrop[];
}
