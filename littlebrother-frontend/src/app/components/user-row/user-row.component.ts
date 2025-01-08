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
import { format_text_array } from 'src/app/common/tools';
import { MatSnackBar } from '@angular/material/snack-bar';
import { EventBusService } from 'src/app/services/event-bus.service';
import { EventData } from 'src/app/models/event-data';
import { EVENT_UPDATE_USER, EVENT_UPDATE_USER_LIST } from '../../common/events';
import { User } from 'src/app/models/user';
import { UserService } from 'src/app/services/user.service';
import * as bootstrap from 'src/assets/contrib/initializr/js/vendor/bootstrap.bundle.js';

@Component({
  selector: 'app-user-row',
  templateUrl: './user-row.component.html',
  styleUrls: ['./user-row.component.css']
})

export class UserRowComponent {
  _user?: User = undefined;
  _languages: Record<string, string> | undefined = {};
  @Input() userId?: number = undefined;

  // see https://angular.io/start/start-forms
  userRowForm : FormGroup = new FormGroup({});

  constructor(
    private formBuilder: FormBuilder,
    private userService: UserService,
    private saveMessageSnackBar: MatSnackBar,
    private eventBusService: EventBusService
  ) {
  }

  // See https://stackoverflow.com/questions/38571812/how-to-detect-when-an-input-value-changes-in-angular
  @Input() set user(user: User | undefined) {
    if (! this._user) {
      this._user = user;
      this.userId = user?.id;
      this.userRowForm = this.formBuilder.group({
        active: this._user?.active
      });
    }
  }

  get user(): User | undefined {
    return this._user;
  }

  @Input() set languages(languages: Record<string, string> | undefined) {
      this._languages = languages;
  }

  get languages(): Record<string, string> | undefined {
    return this._languages;
  }

  getUserSummary(user: User | undefined): string | undefined {
    if (user)
      return format_text_array(user.summary(this.languages));
    else
      return "";
  }

  removeUserFromMonitoring() : void {
    if (this.user && this.user.username) {
      this.userId = undefined;

      this.userService.removeUserFromMonitoring(this.user.username).subscribe(
        result  => {
          if ("error" in result)
            console.log(result.error);
          else {
            this.eventBusService.emit(new EventData(EVENT_UPDATE_USER_LIST));

            // See https://v16.material.angular.io/components/snack-bar/overview
            // See https://www.geeksforgeeks.org/matsnackbar-in-angular-material/
            this.saveMessageSnackBar.open('User removed from monitoring', 'OK', {
              duration: 3000
            });
          }
        }
      )
    }
  }

  openModal() {
    const modalElement = document.getElementById('confirmModal');
    if (modalElement) {
      const bootstrapModal = new bootstrap.Modal(modalElement);
      bootstrapModal.show();
    }
  }

  onActionConfirmed(confirmed: boolean) {
    if (confirmed) {
      this.removeUserFromMonitoring();
      console.log('Action confirmed!');
    } else {
      console.log('Action canceled!');
    }
  }

  updateUser() {
    if (! this.userId)
      return;

    console.log("Updating user " + this.userId + "...");

    var updated_user : User = new User();

    Object.assign(updated_user, this.user)

    updated_user.active = this.userRowForm.value["active"];

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
}
