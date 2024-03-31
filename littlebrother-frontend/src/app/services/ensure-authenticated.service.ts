import { Injectable } from '@angular/core';
import { HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable()
export class EnsureAuthenticated  {

  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean {
    if (localStorage.getItem('token')) {
      return true;
    }
    else {
      this.router.navigateByUrl('/login');
      return false;
    }
  }

  addAuthentication(headers: HttpHeaders): HttpHeaders{
    let token : string | null = localStorage.getItem('token');

    if (token) {
      return headers.append("Authorization", `Bearer ${token}`);
    }
    else {
      this.router.navigateByUrl('/login');
      return headers;
    }
  }
}
