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

import { APP_INITIALIZER, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { MatSnackBarModule } from '@angular/material/snack-bar'
import { HttpRefreshRequestInterceptor } from './common/auth.interceptor'

import { AppRoutingModule } from './app-routing.module';

import { AppComponent } from './app.component';
import { ControlComponent } from './components/control/control.component';
import { LoginComponent } from './components/login/login.component';
import { StatusComponent } from './components/status/status.component';
import { NavBarComponent } from './components/nav-bar/nav-bar.component';
import { HelpersComponent } from './components/helpers/helpers.component';
import { AboutComponent } from './components/about/about.component';

import { AuthService } from './services/auth.service';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { EnsureAuthenticated } from './services/ensure-authenticated.service';
import { LoginRedirect } from './services/login-redirect.service';
import { StatusDetailsComponent } from './components/status-details/status-details.component';
import { AdminComponent } from './components/admin/admin.component';
import { AdminDetailsComponent } from './components/admin-details/admin-details.component';
import { AdminDetailsOverrideComponent } from './components/admin-details-override/admin-details-override.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ConfigService } from './services/config.service';
import { SpinnerComponent } from './components/spinner/spinner.component';
import { UsersComponent } from './components/users/users.component';
import { UserRowComponent } from './components/user-row/user-row.component';

export function initializeApp(configService: ConfigService) {
  return () => configService.loadConfig();
}

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    StatusComponent,
    NavBarComponent,
    HelpersComponent,
    AboutComponent,
    ControlComponent,
    StatusDetailsComponent,
    AdminComponent,
    AdminDetailsComponent,
    // See https://stackoverflow.com/questions/39152071/cant-bind-to-formgroup-since-it-isnt-a-known-property-of-form
    AdminDetailsOverrideComponent,
    SpinnerComponent,
    UsersComponent,
    UserRowComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    BrowserAnimationsModule,
    MatSnackBarModule,
  ],
  providers: [
    AuthService,
    EnsureAuthenticated,
    LoginRedirect,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpRefreshRequestInterceptor,
      multi: true
    },
    {
      provide: APP_INITIALIZER,
      useFactory: initializeApp,
      deps: [ConfigService],
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
