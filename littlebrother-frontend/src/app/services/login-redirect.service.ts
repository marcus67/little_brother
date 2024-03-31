import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable()
export class LoginRedirect  {
  constructor(private auth: AuthService, private router: Router) {}
  canActivate(): boolean {
    if (localStorage.getItem('token')) {
      this.router.navigateByUrl('/status');
      return false;
    }
    else {
      return true;
    }
  }
}
