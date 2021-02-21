import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';

import { ISensorReading } from 'src/app/piponics-interfaces/sensor-reading';

@Injectable({
  providedIn: 'root'
})
export class SensorService {
  hostName:string = "192.168.254.31";
  port:string = "5000";
  baseUrl:string = "http://"+this.hostName+":"+this.port;

  constructor(private http: HttpClient) { }

  getSensorData(uuid:string): Observable<ISensorReading[]> {
    let tempVar = this.http.get<ISensorReading[]>(this.baseUrl+"/sensor/data?uuid="+uuid);
    return tempVar;
  }

}
