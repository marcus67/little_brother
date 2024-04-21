import { AfterViewChecked, Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UserAdminService } from '../../services/user-admin.service'
import { ControlService } from '../../services/control.service'
import { UserAdmin } from '../../models/user-admin'
import { unpickle } from '../../common/unpickle'
import { Control } from '../../models/control'
import { my_handlers } from '../../models/registry'

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
  styleUrls: ['./admin-details.component.css'],
})


export class AdminDetailsComponent implements OnInit, OnDestroy, AfterViewChecked {
  userAdmin: UserAdmin = new UserAdmin();
  accordionState: Map<String, Boolean> = new Map<String, Boolean>();

  private userId: number = -1;
  private intervalId?: number;
  private eventHandlersReady: boolean = false;


  constructor(private controlService: ControlService,
              private userAdminService: UserAdminService,
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

  activateRefresh(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      let control : Control = new Control(jsonEntry);

      this.intervalId = window.setInterval( () => {
         this.getUserAdminDetails();
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
        console.log("Adding event listeners to " + element.id);
      });
    }
  }

  ngOnInit(): void {
    this.getUserAdminDetails();
    this.activateRefresh();
  }

  ngOnDestroy(): void {
    this.deactivateRefresh();

    if (this.eventHandlersReady) {
      jQuery(".accordion-collapse").each( (index:number, element:any) => {
        this.eventHandlersReady = false;
        element.removeEventListener("show.bs.collapse", eventListenerShowAccordion);
        element.removeEventListener("hide.bs.collapse", eventListenerHideAccordion);
        console.log("Removing event listeners from " + element.id);
      });
    }
  }

  storeAccordionState(): void {
    jQuery(".accordion-collapse").each( (index:number, element:any) => {
      // See https://stackoverflow.com/questions/5898656/check-if-an-element-contains-a-class-in-javascript
      //this.accordionState.set(element.id, element.classList.contains("show"))
      console.log("Set status of " + element.id + " to " + element.classList.contains("show"));
      localStorage.setItem(element.id, element.classList.contains("show"));
    })
  }
}
