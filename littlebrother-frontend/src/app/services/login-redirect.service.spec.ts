import { TestBed } from '@angular/core/testing';

import { LoginRedirectService } from './login-redirect.service';

describe('LoginRedirectService', () => {
  let service: LoginRedirectService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LoginRedirectService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
