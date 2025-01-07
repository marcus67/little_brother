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

import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConfigService } from './config.service';
import { User } from '../models/user';
import { UserId } from '../models/user-id';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private REL_URL_USERS: string = '/users';
  private HEADERS: HttpHeaders = new HttpHeaders({'Content-Type': 'application/json'});
  private REL_URL_USER(userId?:number): string { return `/user/${userId}` };
  private REL_URL_POST_USER(username:string): string { return `/user/${username}` };
    

  constructor(
    private http: HttpClient,
    private configService: ConfigService) {}


  loadUsers() : Observable<object> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_USERS}`;

    return this.http.get<object>(url, { headers: this.HEADERS });
  }

  loadUser(userId: number) : Observable<object> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_USER(userId)}`;

    return this.http.get<object>(url, { headers: this.HEADERS });
  }

  updateUser(user?: User) : Observable<object> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_USER(user?.id)}`;

    return this.http.put<object>(url, JSON.stringify(user), { headers: this.HEADERS });
  };

  addUser(username: string) : Observable<UserId> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_POST_USER(username)}`;

    return this.http.post<object>(url, JSON.stringify(username), { headers: this.HEADERS });
  };
}
