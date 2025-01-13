import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {

  private config: any;
  private _isLoading: boolean = true;

  constructor(private http: HttpClient) {}

  loadConfig() {
    return this.http.get('assets/config.json')
      .toPromise()
      .then(data => {
        this.config = data;
        this._isLoading = false;
      });
  }

  get baseUrl() {
    return this.config?.baseUrl;
  }

  get isLoading() : boolean {
    return this._isLoading;
  }
}
