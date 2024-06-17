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
import { EnsureAuthenticated } from '../services/ensure-authenticated.service'
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class MetadataService {

  private metaData : any = null;
  private REL_URL_ABOUT: string = "/about";

  constructor(
    private http: HttpClient, 
    private ensureAuthenticatedService : EnsureAuthenticated,
    private configService: ConfigService) {}

  loadMetadata() : Promise<any> {
    if (this.metaData)
      return new Promise((resolve, reject) => { resolve (this.metaData) });

    let url: string = `${this.configService.baseUrl}${this.REL_URL_ABOUT}`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return new Promise((resolve, reject) => {
      this.http.get(url, {headers: headers}).toPromise().then(
      (result) => {
        this.metaData = result;
        resolve(result);
      }).catch( (error) => {
        reject(error)
      })
    })
  }
}
