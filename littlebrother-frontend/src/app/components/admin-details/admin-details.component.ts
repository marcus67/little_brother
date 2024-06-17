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

import { AfterViewChecked, Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UserAdminService } from '../../services/user-admin.service'
import { UserStatusService } from '../../services/user-status.service'
import { ControlService } from '../../services/control.service'
import { UserAdmin } from '../../models/user-admin'
import { UserStatus } from '../../models/user-status'
import { unpickle } from '../../common/unpickle'
import { Control } from '../../models/control'
import { my_handlers } from '../../models/registry'
import { EventBusService } from 'src/app/services/event-bus.service';
import { EVENT_UPDATE_USER_ADMIN_DETAILS, EVENT_UPDATE_USER_STATUS_DETAILS } from '../../common/events';

declare var jQuery: any;

// See https://stackoverflow.com/questions/65941994/how-to-save-the-collapse-state-on-reload-bootstrap-5

function eventListenerShowAccordion (event:any) {
  console.log(event);
  console.log("Show " + event.originalTarget.id);
  localStorage.setItem(event.originalTarget.id, "true");
};

function eventListenerHideAccordion (event:any) {
  console.log(event);
  console.log("Hide " + event.originalTarget.id);
  localStorage.setItem(event.originalTarget.id, "false");
};

@Component({
  selector: 'app-admin-details',
  templateUrl: './admin-details.component.html',
})


export class AdminDetailsComponent implements OnInit, OnDestroy, AfterViewChecked {
  userAdmin: UserAdmin = new UserAdmin();
  timeExtensions: number[] = [];
  userStatus: UserStatus = new UserStatus();
  accordionState: Map<String, Boolean> = new Map<String, Boolean>();

  public userId: number = -1;
  private intervalId?: number;
  private eventHandlersReady: boolean = false;


  constructor(private controlService: ControlService,
              public userAdminService: UserAdminService,
              private userStatusService: UserStatusService,
              private eventBusServices: EventBusService,
              private route: ActivatedRoute) {
    this.userId = Number(this.route.snapshot.params['user_id']);
  }

  getAccordionState(id: string): Boolean {
    return localStorage.getItem(id) === "true";
  }

  getUserAdminDetails(): void {

    this.userAdminService.loadUserAdminDetails(this.userId).subscribe( jsonData => {
      this.storeAccordionState();
      // extract from JSON...
      this.userAdmin = unpickle(jsonData, my_handlers);
    })
  }

  getUserStatusDetails(): void {

    this.userStatusService.loadUserStatusDetails(this.userId).subscribe( jsonData => {
      this.storeAccordionState();
      // extract from JSON...
      this.userStatus = unpickle(jsonData, my_handlers);
    })
  }

  getUserAdminTimeExtensions(): void {

    this.userAdminService.loadUserAdminTimeExtensions(this.userId).subscribe( jsonData => {
      this.storeAccordionState();
      // extract from JSON...
      this.timeExtensions = unpickle(jsonData, my_handlers);
    })
  }

  activateRefresh(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      let control : Control = new Control(jsonEntry);

      this.intervalId = window.setInterval( () => {
         this.getUserStatusDetails();
         this.getUserAdminTimeExtensions();
      }, control.refresh_interval_in_milliseconds
      )
    });
  }

  deactivateRefresh(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  ngAfterViewChecked():void {
    if (! this.eventHandlersReady) {
      jQuery(".accordion-collapse").each( (index:number, element:any) => {
        this.eventHandlersReady = true;
        element.addEventListener("show.bs.collapse", eventListenerShowAccordion);
        element.addEventListener("hide.bs.collapse", eventListenerHideAccordion);
        // console.log("Adding event listeners to " + element.id);
      });
    }
  }

  ngOnInit(): void {
    this.getUserAdminDetails();
    this.getUserStatusDetails();
    this.getUserAdminTimeExtensions();
    this.activateRefresh();
    this.eventBusServices.on(EVENT_UPDATE_USER_ADMIN_DETAILS, (value: any) => {
      this.getUserAdminDetails();
    });
    this.eventBusServices.on(EVENT_UPDATE_USER_STATUS_DETAILS, (value: any) => {
      this.getUserStatusDetails();
    })
  }

  ngOnDestroy(): void {
    this.deactivateRefresh();

    if (this.eventHandlersReady) {
      jQuery(".accordion-collapse").each( (index:number, element:any) => {
        this.eventHandlersReady = false;
        element.removeEventListener("show.bs.collapse", eventListenerShowAccordion);
        element.removeEventListener("hide.bs.collapse", eventListenerHideAccordion);
        // console.log("Removing event listeners from " + element.id);
      });
    }
  }

  storeAccordionState(): void {
    jQuery(".accordion-collapse").each( (index:number, element:any) => {
      // See https://stackoverflow.com/questions/5898656/check-if-an-element-contains-a-class-in-javascript
      //this.accordionState.set(element.id, element.classList.contains("show"))
      // console.log("Set status of " + element.id + " to " + element.classList.contains("show"));
      localStorage.setItem(element.id, element.classList.contains("show"));
    })
  }

  extendTimeExtension(userId: number, deltaTimeExtension: number) {
    this.userAdminService.extendTimeExtension(userId, deltaTimeExtension).subscribe (
      result => {
        this.getUserStatusDetails();
        this.getUserAdminTimeExtensions();
      }
    )
  };
}
