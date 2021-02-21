import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';

import { ISystem } from 'src/app/piponics-interfaces/system';

@Injectable({
  providedIn: 'root'
})
export class SystemService {
  //systems: ISystem[];
  hostName:string = "192.168.254.31";
  port:string = "5000";
  baseUrl:string = "http://"+this.hostName+":"+this.port;

  constructor(private http: HttpClient) { }

  getAllSystems(): Observable<ISystem[]> {
    let tempVar = this.http.get<ISystem[]>(this.baseUrl+"/system/all");
    return tempVar;
  }

}
