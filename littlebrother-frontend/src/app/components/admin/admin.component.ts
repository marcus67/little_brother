import { Component, OnInit, OnDestroy } from '@angular/core';
import { HttpResponse } from '@angular/common/http';
import { NavBarComponent } from '../nav-bar/nav-bar.component'
import { UserStatusService } from '../../services/user-status.service'
import { ControlService } from '../../services/control.service'
import { UserStatus } from '../../models/user-status'
import { Control } from '../../models/control'
import { unpickle } from '../../common/unpickle'
import { my_handlers } from '../../models/registry'
import { MapType } from '@angular/compiler';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})

export class AdminComponent {
  userStatus: UserStatus[] = [];
  hasDowntime: boolean = false;
  private intervalId?: number;

  constructor(private controlService: ControlService,
              private userStatusService: UserStatusService) {
  }

  getUserStatus(): void {
    this.userStatusService.loadUserStatus().subscribe( jsonData => {
      this.userStatus = unpickle(jsonData, my_handlers)
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
