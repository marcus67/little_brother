import { TestBed } from '@angular/core/testing';

import { UserConfigurationService } from './user.service';

describe('UserConfigurationService', () => {
  let service: UserConfigurationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserConfigurationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
