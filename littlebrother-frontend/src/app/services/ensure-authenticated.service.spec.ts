import { TestBed } from '@angular/core/testing';

import { EnsureAuthenticatedService } from './ensure-authenticated.service';

describe('EnsureAuthenticatedService', () => {
  let service: EnsureAuthenticatedService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EnsureAuthenticatedService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
