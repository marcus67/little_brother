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

import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-nav-bar',
  templateUrl: './nav-bar.component.html',
})
export class NavBarComponent implements OnInit {
  isLoggedIn: boolean = false;
  activeUser: string = "unknown";
  public isAdmin: boolean = false;

  constructor(
    private router: Router,
    private auth: AuthService,
   ) {}

  ngOnInit(): void {
    if (this.auth.isLoggedIn()) {
      this.auth.ensureAuthenticated()
      .then((result) => {
        console.log(result);
        if (result.status === 'OK') {
          this.isLoggedIn = true;
          this.isAdmin = result.authorization.is_admin;
          this.activeUser = result.authorization.username;
        } else {
          this.auth.markLoggedOut();
        }
      })
      .catch((err) => {
        console.log(err);
      });
    }
  }

  onLogout(): void {
    if (this.auth.isLoggedIn()) {
      this.auth.logout().then((result) => {
          console.log(result);
          this.auth.markLoggedOut();
          this.isLoggedIn = false;
          this.isAdmin = false;
          this.activeUser = "unknown";

          if (result?.status === 'OK') {
            this.router.navigate([this.auth.getRelUrlLogin()]);
          }
        })
        .catch((err) => {
          console.log(err);
          this.auth.markLoggedOut();
      });
    }
  }
}
