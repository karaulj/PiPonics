import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { ISystem } from '../piponics-interfaces/system';
import { ISensorReading } from '../piponics-interfaces/sensor-reading';

import { SystemService } from '../piponics-services/system-service/system.service';
import { SensorService } from '../piponics-services/sensor-service/sensor.service';

import { Subject } from 'rxjs';

import { Chart } from 'chart.js';

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

  charts: Chart[] = [];

  constructor(private _systemService: SystemService, private _sensorService: SensorService, private router: Router) { }

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
          this.selSystem = this.systems[0];
          this.getSystemOverview(this.selSystem.uuid);
        }
      }
    )
    console.log("next line");

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
      console.log("curr sensor key",key);
      var sensReadingSub = new Subject<ISensorReading[]>();
      this.getSensorData(uuid, sensReadingSub);
      sensReadingSub.subscribe(
        data => {
          console.log("sdata", data);
          // print graph
          var chart: any = new Chart(key, {
          type: 'line',
          data: {
            labels: ['v', '2021'],
            datasets: [
              {
                data: [1,2 ],
                borderColor: "#3cba9f",
                fill: false
              }
            ]
          },
          options: {
            legend: {
              display: false
            },
            scales: {
              xAxes: [{
                display: true
              }],
              yAxes: [{
                display: true
              }],
            }
          }
        });
        this.charts.push(chart);
        }
      )
    }
  }
  getSensorUuids() {
    let sensorUuids: string[] = [];
    if (this.selSystem != null) {
      // iterate over tanks
      for (const [key, tank] of Object.entries(this.selSystem.tanks)) {
        if (tank.hasOwnProperty('sensors')) {
          for (const [key, sensor] of Object.entries(tank.sensors)) {
            sensorUuids.push(sensor.uuid);
          }
        }
      }
      // iterate over crops
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

  getSensorData(uuid:string, sub:Subject<ISensorReading[]>) {
    this._sensorService.getSensorData(uuid).subscribe(
      responseSensorData => {
        //console.log("sensorData ret",responseSensorData);
        sub.next(responseSensorData);
        //this.sensorData = responseSensorData;
      },
      responseError => {
        this.errMsg = responseError;
        console.log("getSensorData error occured");
        console.log(this.errMsg);
        //this.sensorData = [];
      }
    )
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
