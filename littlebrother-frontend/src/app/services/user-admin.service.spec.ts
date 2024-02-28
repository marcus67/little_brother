import { TestBed } from '@angular/core/testing';

import { UserAdminService } from './user-admin.service';

describe('UserAdminService', () => {
  let service: UserAdminService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserAdminService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
