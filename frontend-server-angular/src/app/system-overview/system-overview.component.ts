import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { ISystem } from '../piponics-interfaces/system';
import { ITank } from '../piponics-interfaces/tank';
import { ICrop } from '../piponics-interfaces/crop';
import { ISensorReading } from '../piponics-interfaces/sensor-reading';

import { SystemService } from '../piponics-services/system-service/system.service';
import { SensorService } from '../piponics-services/sensor-service/sensor.service';

@Component({
  selector: 'app-system-overview',
  templateUrl: './system-overview.component.html',
  styleUrls: ['./system-overview.component.css']
})
export class SystemOverviewComponent implements OnInit {

  systems: ISystem[];
  errMsg: string;
  noSystemsPresent: boolean = false;
  selSystem: ISystem = null;
  sensorData: ISensorReading[];

  constructor(private _systemService: SystemService, private _sensorService: SensorService, private router: Router) { }

  ngOnInit(): void {
    this.getSystems();
    setTimeout(() => {    // wait for async request to complete
      //console.log(this.systems);
      //this.getSystemNames();
      //console.log("this.systems:", this.systems);
      if (this.systems == null) {
        this.noSystemsPresent = true;
      }
      else if (this.systems.length == 0) {
        this.noSystemsPresent = true;
      }
      else {
        this.selSystem = this.systems[0];
        this.getSystemOverview(this.selSystem.uuid);
      }
    }, 100);
  }
  getSystemOverview(systemUuid: string) {
    // get sensors from system
    for (const [key, sys] of Object.entries(this.systems)) {
      if (sys.uuid == systemUuid) {
        console.log("selected", sys.name);
      }
    }
    let sensorUuids: string[] = this.getSensorUuids();
    console.log("sensor uuids", sensorUuids);
    // get sensor data for each sensor
    for (const [key, uuid] of Object.entries(sensorUuids)) {
      console.log("curr sensor uuid",uuid);
      this.getSensorData(uuid);
      setTimeout(() => {
        console.log("sensor data",this.sensorData);
        this.sensorData = [];
        // print graph
      }, 350);
    }
  }
  getSensorUuids() {
    let sensorUuids: string[] = [];
    if (this.selSystem != null) {
      for (const [key, tank] of Object.entries(this.selSystem.tanks)) {
        if (tank.hasOwnProperty('sensors')) {
          for (const [key, sensor] of Object.entries(tank.sensors)) {
            sensorUuids.push(sensor.uuid);
          }
        }
      }
      for (const [key, crop] of Object.entries(this.selSystem.crops)) {
        if (crop.hasOwnProperty('sensors')) {
          for (const [key, sensor] of Object.entries(crop.sensors)) {
            sensorUuids.push(sensor.uuid);
          }
        }
      }
    }
    return sensorUuids;
  }

  getSensorData(uuid:string) {
    this._sensorService.getSensorData(uuid).subscribe(
      responseSensorData => {
        //console.log("sensorData ret",responseSensorData);
        this.sensorData = responseSensorData;
      },
      responseError => {
        this.errMsg = responseError;
        console.log("getSensorData error occured");
        console.log(this.errMsg);
        //this.sensorData = [];
      }
    )
  }
  getSystems() {
    this._systemService.getAllSystems().subscribe(
      responseSystemData => {
        this.systems = responseSystemData;
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
