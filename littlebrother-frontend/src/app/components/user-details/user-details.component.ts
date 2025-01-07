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


import { Component, Input } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { EventBusService } from 'src/app/services/event-bus.service';
import { EventData } from 'src/app/models/event-data';
import { EVENT_UPDATE_USER } from '../../common/events';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import { unpickle } from 'src/app/common/unpickle';
import { my_handlers } from 'src/app/models/registry';
import { ActivatedRoute } from '@angular/router';
import { Control } from 'src/app/models/control';
import { ControlService } from 'src/app/services/control.service';

@Component({
  selector: 'app-user-details',
  templateUrl: './user-details.component.html',
  styleUrls: ['./user-details.component.css']
})

export class UserDetailsComponent {
  user?: User = undefined;
  public userId: number = -1;
  isLoading: boolean = true;
  languages: Record<string, string> | undefined = {};

  first_name: FormControl = new FormControl()
  last_name: FormControl = new FormControl()
  locale: FormControl = new FormControl()
  active: FormControl = new FormControl()

  // see https://angular.io/start/start-forms
  userDetailsForm : FormGroup = new FormGroup({
  });

  constructor(
    private formBuilder: FormBuilder,
    private userService: UserService,
    private saveMessageSnackBar: MatSnackBar,
    private eventBusService: EventBusService,
    private route: ActivatedRoute,
    private controlService: ControlService
  ) {

  }

  updateUser() {
    console.log("Updating user " + this.userId + "...");

    var updated_user : User = new User();

    Object.assign(updated_user, this.user)

    updated_user.active = this.userDetailsForm.value["active"];
    updated_user.first_name = this.userDetailsForm.value["first_name"];
    updated_user.last_name = this.userDetailsForm.value["last_name"];
    updated_user.locale = this.userDetailsForm.value["locale"];

    this.userService.updateUser(updated_user).subscribe(
        result  => {
          if ("error" in result)
            console.log(result.error);
          else {
            this.eventBusService.emit(new EventData(EVENT_UPDATE_USER));

            // See https://v16.material.angular.io/components/snack-bar/overview
            // See https://www.geeksforgeeks.org/matsnackbar-in-angular-material/
            this.saveMessageSnackBar.open('User updated', 'OK', {
              duration: 3000
            });
          }
      }
    )
  };

  getUser(): void {
    this.userId = Number(this.route.snapshot.params['user_id']);

    this.userService.loadUser(this.userId).subscribe( jsonData => {
      this.user = unpickle(jsonData, my_handlers);
      this.first_name = new FormControl(this.user?.first_name)
      this.last_name = new FormControl(this.user?.last_name)
      this.locale = new FormControl(this.user?.locale)
      this.active = new FormControl(this.user?.active)
  
      this.userDetailsForm = this.formBuilder.group({
        first_name: this.first_name,
        last_name: this.last_name,
        locale: this.locale,
        active: this.active
      });
        this.isLoading = false;
    })
  }

  getControl(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      let control : Control = new Control(jsonEntry);

      this.languages = control.languages;
    })
  }

  ngOnInit(): void {
    this.getUser();
    this.getControl();
  }

  // Convert map to array for *ngFor
  get itemsArray(): { key: string; value: string }[] {
    return Object.entries(this.languages|| {}).map(([key, value]) => ({ key, value }));
  }
}
