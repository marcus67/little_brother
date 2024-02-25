import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { StatusComponent } from './components/status/status.component';
import { AdminComponent } from './components/admin/admin.component';
import { StatusDetailsComponent } from './components/status-details/status-details.component';
import { AdminDetailsComponent } from './components/admin-details/admin-details.component';
import { AboutComponent } from './components/about/about.component';
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
  },
  { path: 'status/:user_id',
    component: StatusDetailsComponent,
    canActivate: [EnsureAuthenticated]
  },
  { path: 'admin',
    component: AdminComponent,
    canActivate: [EnsureAuthenticated]
  },
  { path: 'admin/:user_id',
    component: AdminDetailsComponent,
    canActivate: [EnsureAuthenticated]
  },
  { path: 'about',
    component: AboutComponent,
    canActivate: [EnsureAuthenticated]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
