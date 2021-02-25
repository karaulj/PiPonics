import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActuatorControlComponent } from './actuator-control.component';

describe('ActuatorControlComponent', () => {
  let component: ActuatorControlComponent;
  let fixture: ComponentFixture<ActuatorControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ActuatorControlComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ActuatorControlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
