import { TestBed } from '@angular/core/testing';

import { ActuatorService } from './actuator.service';

describe('ActuatorService', () => {
  let service: ActuatorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ActuatorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
