import { Component, OnInit, Input } from '@angular/core';

import { SensorService } from '../piponics-services/sensor-service/sensor.service';
import { ISensorReading } from '../piponics-interfaces/sensor-reading';
import { ISensor } from '../piponics-interfaces/sensor';
import { Subject } from 'rxjs';
import { Chart } from 'chart.js';

@Component({
  selector: 'app-sensor-display',
  templateUrl: './sensor-display.component.html',
  styleUrls: ['./sensor-display.component.css']
})
export class SensorDisplayComponent implements OnInit {
  @Input() id: string;
  @Input() sensorItem: ISensor;

  errMsg: string;

  chart: Chart;

  constructor(private _sensorService: SensorService) { }

  ngOnInit(): void {
    console.log(this.sensorItem);
    //this.getSensorData();
    this.makeSensorChart();
  }

  makeSensorChart() {
    var sensReadingSub = new Subject<ISensorReading[]>();
    this.getSensorData(sensReadingSub);
    sensReadingSub.subscribe(
      data => {
        console.log("sdata", data);
        console.log("sdata_i", this.id);
        var canvas = <HTMLCanvasElement> document.getElementById("canvas"+this.id);
        var ctx = canvas.getContext("2d");
        // print graph
        var myChart = new Chart(ctx, {
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
      console.log("finshed graph");
      }
    )
  }

  getSensorData(sub:Subject<ISensorReading[]>) {
    this._sensorService.getSensorData(this.sensorItem.uuid).subscribe(
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

}
