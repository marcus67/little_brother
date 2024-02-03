import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { EnsureAuthenticated } from '../services/ensure-authenticated.service'

@Injectable({
  providedIn: 'root'
})
export class MetadataService {

  private BASE_URL: string = '/angular-api';
  private metaData : any = null;

  constructor(private http: HttpClient, private ensureAuthenticatedService : EnsureAuthenticated) {}


  loadMetadata() : Promise<any> {
    if (this.metaData)
      return new Promise((resolve, reject) => { resolve (this.metaData) });

    let url: string = `${this.BASE_URL}/about`;
    let headers: HttpHeaders | undefined = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    headers = this.ensureAuthenticatedService.addAuthentication(headers);
    if (headers) {
      console.log(headers.getAll('Authorization'))
      return new Promise((resolve, reject) => {
        this.http.get(url, {headers: headers}).toPromise().then(
        (result) => {
          this.metaData = result;
          resolve(result);
        }).catch( (error) => {
          reject(error)
        })
      })
    } else
      return new Promise((resolve, reject) => { (x: any) => { resolve(x) } });
  }
}
