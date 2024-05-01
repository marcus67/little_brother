import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpResponse } from '@angular/common/http';
import { EnsureAuthenticated } from '../services/ensure-authenticated.service'
import { Observable } from 'rxjs';
import { RuleSet } from '../models/rule-set';

@Injectable({
  providedIn: 'root'
})
export class UserAdminService {

  private BASE_URL: string = '/angular-api';

  constructor(private http: HttpClient, private ensureAuthenticatedService : EnsureAuthenticated) {}

  loadUserAdmin() : Observable<object> {
    let url: string = `${this.BASE_URL}/admin`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    headers = this.ensureAuthenticatedService.addAuthentication(headers);

    console.log(headers.getAll('Authorization'))

    return this.http.get<object>(url, {headers: headers});
  }

  loadUserAdminDetails(userId: number) : Observable<object> {
    let url: string = `${this.BASE_URL}/admin-details/${userId}`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    headers = this.ensureAuthenticatedService.addAuthentication(headers);

    console.log(headers.getAll('Authorization'))

    return this.http.get<object>(url, {headers: headers});
  }

  loadUserAdminTimeExtensions(userId: number) : Observable<object> {
    let url: string = `${this.BASE_URL}/admin-time-extensions/${userId}`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    headers = this.ensureAuthenticatedService.addAuthentication(headers);

    console.log(headers.getAll('Authorization'))

    return this.http.get<object>(url, {headers: headers});
  }

  extendTimeExtension(userId: number, deltaTimeExtension: number) : Observable<object>  {
    let url: string = `${this.BASE_URL}/admin-time-extensions/${userId}/${deltaTimeExtension}`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    headers = this.ensureAuthenticatedService.addAuthentication(headers);

    console.log(headers.getAll('Authorization'))

    return this.http.post<object>(url, null, {headers: headers});
  };

  updateRuleOverride(userId?: number, reference_date_in_iso_8601?: string, ruleset?: RuleSet) : Observable<object> {
    let url: string = `${this.BASE_URL}/admin-rule-overrides/${userId}/${reference_date_in_iso_8601}`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    headers = this.ensureAuthenticatedService.addAuthentication(headers);

    console.log(headers.getAll('Authorization'))

    return this.http.post<object>(url, JSON.stringify(ruleset), {headers: headers});
  };

}
