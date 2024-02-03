// See https://realpython.com/user-authentication-with-angular-4-and-flask/
import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { User } from '../models/user';
import { Router } from '@angular/router';
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

  ensureAuthenticated(token: string): Promise<any> {
    let url: string = `${this.BASE_URL}/login-status`;
    let headers: HttpHeaders = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    });
    return new Promise((resolve, reject) => {
      this.http.get(url, {headers: headers}).toPromise().then(
      (result) => {
          resolve(result);
      }).catch( (error) => {
          localStorage.removeItem('token');
          reject(error)
      })
    })
  }

  logout(token: string): Promise<any> {
    let url: string = `${this.BASE_URL}/logout`;
    let headers: HttpHeaders = new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    });
    return this.http.post(url, null, {headers: headers}).toPromise();
  }
}

