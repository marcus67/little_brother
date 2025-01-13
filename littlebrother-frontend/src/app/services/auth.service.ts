// Copyright (C) 2019-24  Marcus Rickert
//
// See https://github.com/marcus67/little_brother
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

// See https://realpython.com/user-authentication-with-angular-4-and-flask/
import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { map } from 'rxjs'
import { Login } from '../models/login';
import { ConfigService } from './config.service';

interface ILoginResult {
  status: string,
  is_admin: boolean,
  username: string,
  user_id: number
}

interface ILogoutResult {
  status: string,
  error_details: string
}

@Injectable()
export class AuthService {
  private LOCAL_STORAGE_KEY_LOGGED_IN = "logged_in";
  private LOCAL_STORAGE_KEY_IS_ADMIN = "is_admin";
  private LOCAL_STORAGE_KEY_ACTIVE_USER_ID = "active_user_id";
  private REL_URL_DEFAULT_REDIRECT: string = '/status';
  private REL_URL_LOGIN: string = '/login';
  private REL_URL_LOGOUT: string = '/logout';
  private REL_URL_REFRESH: string = '/refresh';
  private REL_URL_LOGIN_STATUS: string = '/login-status';
  private HEADERS: HttpHeaders = new HttpHeaders({'Content-Type': 'application/json'});
  private redirect: string | undefined = undefined;

  constructor(private http: HttpClient,
              private configService: ConfigService
  ) {}

  login(user : Login): Promise<ILoginResult | undefined> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_LOGIN}`;

    return this.http.post<ILoginResult>(url, user, {headers: this.HEADERS}).pipe(
      map( result => {
        localStorage.setItem(this.LOCAL_STORAGE_KEY_LOGGED_IN, "true")
        localStorage.setItem(this.LOCAL_STORAGE_KEY_IS_ADMIN, result.is_admin.toString())
        localStorage.setItem(this.LOCAL_STORAGE_KEY_ACTIVE_USER_ID, result.user_id.toString())
        return result;
      })
    ).toPromise();
  }

  setRedirect(redirect: string) {
    this.redirect = redirect;
  }

  getDefaultRedirect(): string {
    return this.REL_URL_DEFAULT_REDIRECT;
  }

  getRedirect(): string {
    if (this.redirect) {
      let temp:string = this.redirect;
      this.redirect = undefined;
      return temp;
    } else {
      return this.REL_URL_DEFAULT_REDIRECT;
    }
  }

  getRelUrlLogin():string {
    return this.REL_URL_LOGIN;
  }

  isLoggedIn():boolean {
    return localStorage.getItem(this.LOCAL_STORAGE_KEY_LOGGED_IN) != null
  }

  markLoggedOut() {
    localStorage.removeItem(this.LOCAL_STORAGE_KEY_LOGGED_IN)
  }

  getActiveUserId() : number {
    return Number(localStorage.getItem(this.LOCAL_STORAGE_KEY_ACTIVE_USER_ID));
  }

  refreshToken() {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_REFRESH}`;
    return this.http.post(url, { }, { headers: this.HEADERS});
  }

  ensureAuthenticated(): Promise<any> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_LOGIN_STATUS}`;
    return new Promise((resolve, reject) => {
      this.http.get(url, {headers: this.HEADERS}).toPromise().then(
      (result) => {
          resolve(result);
      }).catch( (error) => {
          this.markLoggedOut();
          reject(error)
      })
    })
  }

  logout(): Promise<ILogoutResult | undefined> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_LOGOUT}`;

    return this.http.post<ILogoutResult>(url, null, {}).pipe(
      map( result => {
        this.markLoggedOut();
        return result;
      })
    ).toPromise();
  }

  get isLoading() : boolean {
    return this.configService.isLoading;
  }
}
