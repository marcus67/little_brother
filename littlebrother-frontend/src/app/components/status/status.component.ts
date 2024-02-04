import { Component, OnInit } from '@angular/core';
import { NavBarComponent } from '../nav-bar/nav-bar.component'
import { UserStatusService } from '../../services/user-status.service'
//import { ControlComponent } from '../control/control.component'
import { ControlService } from '../../services/control.service'
import { UserStatus } from '../../models/user-status'
import { Control } from '../../models/control'

// https://levelup.gitconnected.com/auto-refresh-or-polling-using-rxjs-timer-operator-2141016c7a53

@Component({
  selector: 'status',
  templateUrl: './status.component.html',
  styleUrls: ['./status.component.css']
})

export class StatusComponent {
  userStatus: UserStatus[] = [];
  hasDowntime: boolean = false;
  private intervalId?: number;

  constructor(private controlService: ControlService,
              private userStatusService: UserStatusService) {
  }

  getUserStatus(): void {
    this.userStatusService.loadUserStatus().subscribe( jsonArray => {
      // extract from JSON and sort alphabetically by full name
      this.userStatus = jsonArray.map(jsonEntry => new UserStatus(jsonEntry)).sort( (a, b) => {
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
    });
  }

  activateRefresh(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      let control : Control = new Control(jsonEntry);

      console.log("refresh_interval_in_milliseconds" + control.refresh_interval_in_milliseconds);

      this.intervalId = setInterval( () => {
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
