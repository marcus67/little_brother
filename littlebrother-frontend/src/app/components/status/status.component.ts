import { Component, OnInit } from '@angular/core';
import { NavBarComponent } from '../nav-bar/nav-bar.component'
import { UserStatusService } from '../../services/user-status.service'
import { UserStatus } from '../../models/user-status'

@Component({
  selector: 'status',
  templateUrl: './status.component.html',
  styleUrls: ['./status.component.css']
})
export class StatusComponent {
  userStatus: UserStatus[] = [];
  hasDowntime: boolean = false;

  constructor(private userStatusService: UserStatusService) {
  }

  getUserStatus(): void {
    this.userStatusService.loadUserStatus().subscribe( jsonArray => {
      this.userStatus = jsonArray.map(jsonEntry => new UserStatus(jsonEntry));
      this.hasDowntime = false;

      this.userStatus.forEach( entry => {
        if (entry.todays_downtime_in_seconds)
           this.hasDowntime = true;
        }
      );
    });

  }

  ngOnInit(): void {
    this.getUserStatus();
  }
}
