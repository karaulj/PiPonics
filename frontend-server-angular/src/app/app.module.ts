import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { SystemOverviewComponent } from './system-overview/system-overview.component';
import { SensorDisplayComponent } from './sensor-display/sensor-display.component';
import { ActuatorControlComponent } from './actuator-control/actuator-control.component';
//import { routing } from './app.routing';


@NgModule({
  declarations: [
    AppComponent,
    SystemOverviewComponent,
    SensorDisplayComponent,
    ActuatorControlComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule, ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
