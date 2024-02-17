import { Component, OnInit } from '@angular/core';
import { HttpResponse } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { NavBarComponent } from '../nav-bar/nav-bar.component'
import { UserStatusService } from '../../services/user-status.service'
import { ControlService } from '../../services/control.service'
import { UserStatus } from '../../models/user-status'
import { UserStatusDetail } from '../../models/user-status-detail'
import { unpickle } from '../../common/unpickle'
import { Control } from '../../models/control'
import { my_handlers } from '../../models/registry'

@Component({
  selector: 'app-status-details',
  templateUrl: './status-details.component.html',
  styleUrls: ['./status-details.component.css']
})

export class StatusDetailsComponent {
  userStatus: UserStatus = new UserStatus();
  private userId: number = -1;
  private intervalId?: number;

  constructor(private controlService: ControlService,
              private userStatusService: UserStatusService,
              private route: ActivatedRoute) {
    this.userId = Number(this.route.snapshot.params['user_id']);
  }

  getUserStatus(): void {
    this.userStatusService.loadUserStatusDetails(this.userId).subscribe( jsonData => {
      // extract from JSON...
      this.userStatus = unpickle(jsonData, my_handlers)
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
