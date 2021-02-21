import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SystemOverviewComponent } from './system-overview/system-overview.component'

const routes: Routes = [
  { path: '', component: SystemOverviewComponent },
  { path: '**', component: SystemOverviewComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
