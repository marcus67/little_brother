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
  // The redirect from '' to 'status' is required to kickstart the initial page load which starts on index.html!
  // Note that in mode `ng serve` this mapping seems to exist implicitly. Only for production an explicit mapping
  // is required!
  { path: '', redirectTo: 'status', pathMatch: 'full' },
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
