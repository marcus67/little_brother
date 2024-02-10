import { Component, OnInit } from '@angular/core';
import { HttpResponse } from '@angular/common/http';
import { NavBarComponent } from '../nav-bar/nav-bar.component'
import { UserStatusService } from '../../services/user-status.service'
//import { ControlComponent } from '../control/control.component'
import { ControlService } from '../../services/control.service'
import { UserStatus } from '../../models/user-status'
import { Control } from '../../models/control'
//import { decode } from 'jsonpickle/js'

const jsonpickle = require('jsonpickle')

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
    this.userStatusService.loadUserStatus().subscribe( jsonData => {
      //let someDummyObject : UserStatus = new UserStatus()
      let jsonDataAsString: string = JSON.stringify(jsonData)
      // extract from JSON...
      this.userStatus = jsonpickle.decode(jsonDataAsString, my_handlers)
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

      console.log("refresh_interval_in_milliseconds" + control.refresh_interval_in_milliseconds);

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

export const my_handlers = {
  'little_brother.transport.UserStatusTO.UserStatusTO': {
      restore: (obj:any) => new UserStatus(obj),
  },
};
