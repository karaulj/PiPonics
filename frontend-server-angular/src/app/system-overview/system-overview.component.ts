import { Component, OnInit } from '@angular/core';

import { ISystem } from '../piponics-interfaces/system';
import { ISensor } from '../piponics-interfaces/sensor';
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
  sensorUuids: string[];
  sensorItems: ISensor[];

  constructor(private _systemService: SystemService) { }

  ngOnInit(): void {
    var sysSubject = new Subject<ISystem[]>();
    this.getSystems(sysSubject);
    sysSubject.subscribe(
      data => {
        this.systems = data;
        console.log("systems", this.systems);
        if (this.systems == null) {
          this.noSystemsPresent = true;
        }
        else if (this.systems.length == 0) {
          this.noSystemsPresent = true;
        }
        else {
          console.log("else", this.systems);
          this.selSystem = this.systems[0];
          this.getSystemOverview(this.selSystem.uuid);
        }
      }
    )
    console.log("next line");
  }

  getSystemOverview(systemUuid: string) {
    //console.log(document.getElementById("testcanvas").getContext("2d"));
    // get sensors from system
    for (const [key, sys] of Object.entries(this.systems)) {
      if (sys.uuid == systemUuid) {
        console.log("selected", sys.name);
      }
    }
    //this.getSensorUuids();
    this.getSensorItems();
    //console.log("sensor uuids", this.sensorUuids);
    // print sensor graphs
  }

  getSensorItems() {
    if (this.selSystem != null) {
      this.sensorItems = [];
      // iterate over tanks
      for (const [key, tank] of Object.entries(this.selSystem.tanks)) {
        if (tank.hasOwnProperty('sensors')) {
          for (const [key, sensor] of Object.entries(tank.sensors)) {
            this.sensorItems.push(sensor);
          }
        }
      }
      // iterate over crops
      for (const [key, crop] of Object.entries(this.selSystem.crops)) {
        if (crop.hasOwnProperty('sensors')) {
          for (const [key, sensor] of Object.entries(crop.sensors)) {
            this.sensorItems.push(sensor);
          }
        }
      }
    }
  }

  getSensorUuids() {
    if (this.selSystem != null) {
      this.sensorUuids = [];
      // iterate over tanks
      for (const [key, tank] of Object.entries(this.selSystem.tanks)) {
        if (tank.hasOwnProperty('sensors')) {
          for (const [key, sensor] of Object.entries(tank.sensors)) {
            this.sensorUuids.push(sensor.uuid);
          }
        }
      }
      // iterate over crops
      for (const [key, crop] of Object.entries(this.selSystem.crops)) {
        if (crop.hasOwnProperty('sensors')) {
          for (const [key, sensor] of Object.entries(crop.sensors)) {
            this.sensorUuids.push(sensor.uuid);
          }
        }
      }
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
