import { Component, OnInit } from '@angular/core';

import { ISystem } from '../piponics-interfaces/system';
import { ISensor } from '../piponics-interfaces/sensor';
import { IActuator } from '../piponics-interfaces/actuator';
import { SystemService } from '../piponics-services/system-service/system.service';

//import { SensorDisplayComponent } from '../sensor-display/sensor-display.component';
import { Chart } from 'chart.js';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-system-overview',
  templateUrl: './system-overview.component.html',
  styleUrls: ['./system-overview.component.css']
})
export class SystemOverviewComponent implements OnInit {

  systems: ISystem[];
  errMsg: string;
  noSystemsPresent: boolean;
  selSystem: ISystem = null;
  sensorItems: ISensor[];
  actuatorItems: IActuator[];

  constructor(private _systemService: SystemService) { }

  ngOnInit(): void {
    var sysSubject = new Subject<ISystem[]>();
    this.getSystems(sysSubject);
    sysSubject.subscribe(
      data => {
        this.systems = data;
        if (this.systems == null) {
          this.noSystemsPresent = true;
        }
        else if (this.systems.length == 0) {
          this.noSystemsPresent = true;
        }
        else {
          this.noSystemsPresent = false;
          this.getSystemOverview(this.systems[0].uuid);
        }
      }
    )
  }

  getSystemOverview(systemUuid: string) {
    // select system
    for (let sys of Object.values(this.systems)) {
      if (sys.uuid == systemUuid) {
        this.selSystem = sys;
        console.log("selected", sys.name);
      }
    }
    this.getSensorItems();
    this.getActuatorItems();
  }

  getSensorItems() {
    if (this.selSystem != null) {
      this.sensorItems = [];
      // iterate over tanks
      for (let tank of Object.values(this.selSystem.tanks)) {
        if (tank.hasOwnProperty('sensors')) {
          for (let sensor of Object.values(tank.sensors)) {
            this.sensorItems.push(sensor);
          }
        }
      }
      // iterate over crops
      for (let crop of Object.values(this.selSystem.crops)) {
        if (crop.hasOwnProperty('sensors')) {
          for (let sensor of Object.values(crop.sensors)) {
            this.sensorItems.push(sensor);
          }
        }
      }
    }
  }

  getActuatorItems() {
    if (this.selSystem != null) {
      this.actuatorItems = [];
      // iterate over tanks
      for (let tank of Object.values(this.selSystem.tanks)) {
        if (tank.hasOwnProperty('actuators')) {
          for (let actuator of Object.values(tank.actuators)) {
            this.actuatorItems.push(actuator);
          }
        }
      }
      // iterate over crops
      for (let crop of Object.values(this.selSystem.crops)) {
        if (crop.hasOwnProperty('actuators')) {
          for (let actuator of Object.values(crop.actuators)) {
            this.actuatorItems.push(actuator);
          }
        }
      }
      console.log("actuators", this.actuatorItems);
    }
  }

  getSystems(sub:Subject<ISystem[]>) {
    this._systemService.getAllSystems().subscribe(
      responseSystemData => {
        //this.systems = responseSystemData;
        sub.next(responseSystemData);
        //console.log(this.systems[0]);
      },
      responseError => {
        this.systems = null;
        this.errMsg = responseError;
        console.log("getSystems error occured");
        console.log(this.errMsg);
      }
    )
    ///console.log("ran getSystems");
  }
}
