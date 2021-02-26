import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ActuatorService {
  hostName:string = "192.168.254.31";
  port:string = "5000";
  baseUrl:string = "http://"+this.hostName+":"+this.port;

  constructor(private http: HttpClient) { }

  postActuatorDrive(uuid:string, val:number): Observable<any> {
    let tempVar = this.http.post<any>(
      this.baseUrl+"/actuator/drive?uuid="+uuid+"&value="+val,
      null
    );
    return tempVar;
  }

}
