// See https://realpython.com/user-authentication-with-angular-4-and-flask/
import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { User } from '../models/user';
//import 'rxjs/add/operator/toPromise';

@Injectable()
export class AuthService {
  private BASE_URL: string = '/angular-api';
  private headers: HttpHeaders = new HttpHeaders({'Content-Type': 'application/json'});

  constructor(private http: HttpClient) {}
  login(user : User): Promise<any> {
    let url: string = `${this.BASE_URL}/login`;
    return this.http.post(url, user, {headers: this.headers}).toPromise();
  }
}
