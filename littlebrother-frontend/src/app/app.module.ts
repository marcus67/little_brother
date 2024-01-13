import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';

import { AppComponent } from './app.component';
import { LoginComponent } from './components/login/login.component';
import { StatusComponent } from './components/status/status.component';
import { NavBarComponent } from './components/nav-bar/nav-bar.component';
import { HelpersComponent } from './components/helpers/helpers.component';
import { AboutComponent } from './components/about/about.component';

import { AuthService } from './services/auth.service';
import { FormsModule } from '@angular/forms';
import { EnsureAuthenticated } from './services/ensure-authenticated.service';
import { LoginRedirect } from './services/login-redirect.service';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    StatusComponent,
    NavBarComponent,
    HelpersComponent,
    AboutComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    AppRoutingModule,
    FormsModule
  ],
  providers: [
    AuthService,
    EnsureAuthenticated,
    LoginRedirect
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
