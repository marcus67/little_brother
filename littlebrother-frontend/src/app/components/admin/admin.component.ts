import { Component, OnInit, OnDestroy } from '@angular/core';
import { UserAdminService } from '../../services/user-admin.service'
import { ControlService } from '../../services/control.service'
import { UserAdmin } from '../../models/user-admin'
import { Control } from '../../models/control'
import { unpickle } from '../../common/unpickle'
import { my_handlers } from '../../models/registry'

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})

export class AdminComponent {
  userAdmin: UserAdmin[] = [];
  hasDowntime: boolean = false;
  private intervalId?: number;

  constructor(private controlService: ControlService,
              private userAdminService: UserAdminService) {
  }

  getuserAdmin(): void {
    this.userAdminService.loadUserAdmin().subscribe( jsonData => {
      let unpickledData = unpickle(jsonData, my_handlers)

      if (unpickledData) {
        this.userAdmin = unpickledData
        this.userAdmin.sort( (a:UserAdmin, b:UserAdmin) => {
              var upper_full_name_a = a.user_status?.full_name || "";
              var upper_full_name_b = b.user_status?.full_name || "";
              return  (upper_full_name_a < upper_full_name_b) ? -1 : (upper_full_name_a > upper_full_name_b) ? 1 : 0;
            }
        );

        this.hasDowntime = false;

        this.userAdmin.forEach( entry => {
          if (entry.user_status?.todays_downtime_in_seconds)
            this.hasDowntime = true;
          }
        );
      } else {
        console.error("Cannot unpickle UserAdmin entries")
      }
    });
  }

  activateRefresh(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      let control : Control = new Control(jsonEntry);

      this.intervalId = window.setInterval( () => {
         this.getuserAdmin();
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
    this.getuserAdmin();
    this.activateRefresh();
  }

  ngOnDestroy(): void {
    this.deactivateRefresh();
  }
}
