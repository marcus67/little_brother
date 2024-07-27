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
import { HttpHeaders, HttpClient, HttpResponse } from '@angular/common/http';
//import { EnsureAuthenticated } from '../services/ensure-authenticated.service'
import { Observable } from 'rxjs';
import { RuleSet } from '../models/rule-set';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class UserAdminService {

  private REL_URL_ADMIN: string = '/admin';
  private REL_URL_ADMIN_DETAILS(userId:number): string { return `/admin-details/${userId}` };
  private REL_URL_ADMIN_TIME_EXTENSIONS(userId:number): string { return `/admin-time-extensions/${userId}` };
  private REL_URL_ADMIN_DELTA_TIME_EXTENSIONS(userId:number,
    deltaTimeExtension: number): string { return `/admin-time-extensions/${userId}/${deltaTimeExtension}` };
  private REL_URL_ADMIN_UPDATE_RULE_OVERRIDE(userId?:number,
    reference_date_in_iso_8601?: string): string { return `/admin-rule-overrides/${userId}/${reference_date_in_iso_8601}` };
  private HEADERS: HttpHeaders = new HttpHeaders({'Content-Type': 'application/json'});

  constructor(
    private http: HttpClient, 
//    private ensureAuthenticatedService : EnsureAuthenticated,
    private configService: ConfigService) {}

  loadUserAdmin() : Observable<object> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_ADMIN}`;

    return this.http.get<object>(url,  { headers: this.HEADERS });
  }

  loadUserAdminDetails(userId: number) : Observable<object> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_ADMIN_DETAILS(userId)}`;

    return this.http.get<object>(url,  { headers: this.HEADERS });
  }

  loadUserAdminTimeExtensions(userId: number) : Observable<object> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_ADMIN_TIME_EXTENSIONS(userId)}`;

    return this.http.get<object>(url,  { headers: this.HEADERS });
  }

  extendTimeExtension(userId: number, deltaTimeExtension: number) : Observable<object>  {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_ADMIN_DELTA_TIME_EXTENSIONS(userId, deltaTimeExtension)}`;

    return this.http.post<object>(url, null,  { headers: this.HEADERS });
  };

  updateRuleOverride(userId?: number, reference_date_in_iso_8601?: string, ruleset?: RuleSet) : Observable<object> {
    let url: string = `${this.configService.baseUrl}${this.REL_URL_ADMIN_UPDATE_RULE_OVERRIDE(userId, reference_date_in_iso_8601)}`;

    return this.http.post<object>(url, JSON.stringify(ruleset), { headers: this.HEADERS });
  };
}
