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

  name: string;
  units: string = "";

  data: number[];
  timestamps: Date[];

  errMsg: string;

  constructor(private _sensorService: SensorService) { }

  ngOnInit(): void {
    // name
    if (this.sensorItem.hasOwnProperty("nice_name")) {
      this.name = this.sensorItem.nice_name + " ("+this.sensorItem.tank_or_crop+")";
    }
    else {
      this.name = this.sensorItem.type + " ("+this.sensorItem.tank_or_crop+")";
    }
    // units
    if (this.sensorItem.hasOwnProperty("units")) {
      this.units = this.sensorItem.units.replace("degrees", "\xB0").replace(" ", "");
    }
    this.makeSensorChart();
  }

  makeSensorChart() {
    var sensReadingSub = new Subject<ISensorReading[]>();
    this.getSensorData(sensReadingSub);
    sensReadingSub.subscribe(
      sensorDataRaw => {
        // get data
        [this.timestamps, this.data] = this.extractSensorData(sensorDataRaw);
        var canvas = <HTMLCanvasElement> document.getElementById("canvas"+this.id);
        var ctx = canvas.getContext("2d");
        // print graph
        var myChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.timestamps.splice(-13),
          datasets: [
            {
              data: this.data.splice(-13),
              //borderColor: "#3cb6ba",   //cyan
              borderColor: "rgba(60,186,94,0.5)",
              backgroundColor: "rgba(60,186,94,0.1)",
              fill: true
            }
          ]
        },
        options: {
          legend: {
            display: false
          },
          title: {
            display: true,
            fontSize: 20,
            fontFamily: "Ubuntu Mono",
            text: this.name
          },
          scales: {
            xAxes: [{
              display: true,
              scaleLabel: {
                display: true,
                fontFamily: "Ubuntu Mono",
                fontSize: 16,
                labelString: "time"
              }
            }],
            yAxes: [{
              display: true,
              ticks: {
                maxTicksLimit: 5
              },
              scaleLabel: {
                display: true,
                fontFamily: "Ubuntu Mono",
                fontSize: 16,
                labelString: this.units
              }
            }],
          }
        }
      });
      }
    )
  }

  extractSensorData(readings: ISensorReading[]) {
    let data: any[] = [];
    let timestamps: any[] = [];
    for (let reading of Object.values(readings)) {
      // time
      let time = new Date(reading.t);   // expects reading to be in UTC

      let time_s = "";
      time_s = time_s + (time.getMonth()+1)+"/"+time.getDate() + " ";
      time_s = time_s + ("0" + time.getHours()).slice(-2)+":"+("0" + time.getMinutes()).slice(-2);
      timestamps.push(time_s);

      // value
      let value = reading.v;
      data.push(value);
    }
    return [timestamps, data];
  }

  getSensorData(sub:Subject<ISensorReading[]>) {
    this._sensorService.getSensorData(this.sensorItem.uuid).subscribe(
      responseSensorData => {
        sub.next(responseSensorData);
      },
      responseError => {
        this.errMsg = responseError;
        console.log("getSensorData error occured");
        console.log(this.errMsg);
      }
    )
  }

}
