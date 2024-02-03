import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpResponse } from '@angular/common/http';
import { EnsureAuthenticated } from '../services/ensure-authenticated.service'
import { UserStatus } from '../models/user-status'
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class UserStatusService {

  private BASE_URL: string = '/angular-api';

  constructor(private http: HttpClient, private ensureAuthenticatedService : EnsureAuthenticated) {}

  loadUserStatus() : Observable<UserStatus[]> {
    let url: string = `${this.BASE_URL}/status`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    headers = this.ensureAuthenticatedService.addAuthentication(headers);

    console.log(headers.getAll('Authorization'))

    return this.http.get<UserStatus[]>(url, {headers: headers});
  }
}
