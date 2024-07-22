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

import { Component, OnInit, OnDestroy } from '@angular/core';
import { UserStatusService } from '../../services/user-status.service'
import { ControlService } from '../../services/control.service'
import { UserStatus } from '../../models/user-status'
import { Control } from '../../models/control'
import { unpickle } from '../../common/unpickle'
import { my_handlers } from '../../models/registry'

// https://levelup.gitconnected.com/auto-refresh-or-polling-using-rxjs-timer-operator-2141016c7a53

@Component({
  selector: 'status',
  templateUrl: './status.component.html',
})


export class StatusComponent implements OnInit, OnDestroy {
  userStatus: UserStatus[] = [];
  hasDowntime: boolean = false;
  isLoading: boolean = true;
  private intervalId?: number;

  constructor(private controlService: ControlService,
              private userStatusService: UserStatusService) {
  }

  getUserStatus(): void {
    this.userStatusService.loadUserStatus().subscribe( jsonData => {
      let unpickledData = unpickle(jsonData, my_handlers)

      if (unpickledData) {
        this.userStatus = unpickledData
        this.userStatus.sort( (a:UserStatus, b:UserStatus) => {
              var upper_full_name_a = a.full_name || "";
              var upper_full_name_b = b.full_name || "";
              return  (upper_full_name_a < upper_full_name_b) ? -1 : (upper_full_name_a > upper_full_name_b) ? 1 : 0;
            }
        );

        this.hasDowntime = false;

        this.userStatus.forEach( entry => {
          if (entry.todays_downtime_in_seconds)
            this.hasDowntime = true;
          }
        );
        this.isLoading = false;
      } else {
        console.error("Cannot unpickle UserStatus entries")
      }
    });
  }

  activateRefresh(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      let control : Control = new Control(jsonEntry);

      this.intervalId = window.setInterval( () => {
         this.getUserStatus();
      }, control.refresh_interval_in_milliseconds
      )
    });
  }

  deactivateRefresh(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  ngOnInit(): void {
    this.getUserStatus();
    this.activateRefresh();
  }

  ngOnDestroy(): void {
    this.deactivateRefresh();
  }
}
