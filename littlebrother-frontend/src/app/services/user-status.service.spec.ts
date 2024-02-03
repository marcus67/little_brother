import { TestBed } from '@angular/core/testing';

import { UserStatusService } from './user-status.service';

describe('UserStatusService', () => {
  let service: UserStatusService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserStatusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
