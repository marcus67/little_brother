import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar'

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
    AdminDetailsOverrideComponent
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
    LoginRedirect
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
