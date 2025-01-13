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

import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { Login } from '../../models/login';

@Component({
  selector: 'login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  user: Login = new Login();
  message: string = "";

  constructor(private router: Router, private auth: AuthService) {

  }

  onLogin(): void {
    if (this.user.username == '') {
      this.user.username = undefined;
    }
    if (this.user.password == '') {
      this.user.password = undefined;
    }

    this.auth.login(this.user)
    .then((result) => {
      this.message = ""
      this.router.navigateByUrl(this.auth.getRedirect());
    })
    .catch((err) => {
      console.log(err);
      if (err.status == 504) {
        this.message = "Cannot reach backend!";
      } else {
        this.message = err.error.error_details;
      }
    });
  }

  get isLoading() : boolean {
    return this.auth.isLoading;
  }
}
