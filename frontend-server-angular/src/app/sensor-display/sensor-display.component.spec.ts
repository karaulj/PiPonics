import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SensorDisplayComponent } from './sensor-display.component';

describe('SensorDisplayComponent', () => {
  let component: SensorDisplayComponent;
  let fixture: ComponentFixture<SensorDisplayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SensorDisplayComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SensorDisplayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
