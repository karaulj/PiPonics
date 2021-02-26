import { Component, OnInit, Input } from '@angular/core';

import { ActuatorService } from '../piponics-services/actuator-service/actuator.service';
import { IActuator } from '../piponics-interfaces/actuator';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-actuator-control',
  templateUrl: './actuator-control.component.html',
  styleUrls: ['./actuator-control.component.css']
})
export class ActuatorControlComponent implements OnInit {
  @Input() actuatorItem: IActuator;
  // common attributes
  driveVal: number;
  name: string;
  errMsg: string;
  // 'value' drive_with type
  rangeMax: number = 100;
  // 'switch' drive_with type
  switchOn: boolean;

  constructor(private _actuatorService: ActuatorService) { }

  ngOnInit(): void {
    // name
    if (this.actuatorItem.hasOwnProperty("nice_name")) {
      this.name = this.actuatorItem.nice_name + " ("+this.actuatorItem.tank_or_crop+")";
    }
    else {
      this.name = this.actuatorItem.type + " ("+this.actuatorItem.tank_or_crop+")";
    }
    // waterpump on by default
    if (this.actuatorItem.drive_with == "switch" && this.actuatorItem.type == "waterpump") {
      this.switchOn = true;
    }
    else {
      this.switchOn = false;
    }
  }

  submitValue() {
    let val:number = parseInt((<HTMLInputElement>document.getElementById('drVal')).value);
    if (val < 0 || val > this.rangeMax) {
      (<HTMLInputElement>document.getElementById('drVal')).value = "0";
    } else {
      this.driveVal = val;
      this.postActuatorDrive();
    }
  }

  flipSwitch() {
    this.switchOn = !this.switchOn;
    if (this.switchOn) {
      this.driveVal = 1;
    }
    else {
      this.driveVal = 0;
    }
    this.postActuatorDrive();
  }

  postActuatorDrive() {
    this._actuatorService.postActuatorDrive(this.actuatorItem.uuid, this.driveVal).subscribe(
      responseActuatorDrive => {
        console.log("actuatorDrive response:", responseActuatorDrive);
      },
      responseError => {
        this.errMsg = responseError;
        console.log("driveActuator error occured");
        console.log(this.errMsg);
      }
    )
  }

}
