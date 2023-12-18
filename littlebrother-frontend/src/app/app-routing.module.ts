import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { StatusComponent } from './components/status/status.component';
import { EnsureAuthenticated } from './services/ensure-authenticated.service';
import { LoginRedirect } from './services/login-redirect.service';


const routes: Routes = [
  { path: 'login',
    component: LoginComponent,
    canActivate: [LoginRedirect]
  },
  { path: 'status',
    component: StatusComponent,
    canActivate: [EnsureAuthenticated]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
