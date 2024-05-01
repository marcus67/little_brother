import { Component, Input } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { RuleSet } from '../../models/rule-set'
import { UserAdminService } from 'src/app/services/user-admin.service';
import { get_duration_in_seconds_from_string, get_iso_8601_from_time_string } from 'src/app/common/tools';
import { AdminDetailsComponent } from '../admin-details/admin-details.component';

@Component({
  selector: 'app-admin-details-override',
  templateUrl: './admin-details-override.component.html',
  styleUrls: ['./admin-details-override.component.css'],
})
export class AdminDetailsOverrideComponent {
  _override?: RuleSet = undefined;
  @Input() userId?: number = undefined;
  @Input() referenceDateInIso8601?: string = undefined;
  @Input() adminDetails?: AdminDetailsComponent = undefined;

  // See https://stackoverflow.com/questions/38571812/how-to-detect-when-an-input-value-changes-in-angular
  @Input() set override(override: RuleSet | undefined) {
    if (! this._override) {
      this._override = override;
      this.adminOverrideForm = this.formBuilder.group({
        min_time_of_day: this._override?.min_time_of_day_as_string(),
        max_time_of_day: this._override?.max_time_of_day_as_string(),
        max_time_per_day: this._override?.max_time_per_day_as_string(),
        min_break: this._override?.min_break_as_string(),
        max_activity_duration: this._override?.max_activity_duration_as_string(),
        free_play: this._override?.free_play
      });  
    }
  }

  get override(): RuleSet | undefined {
    return this._override;
  }

  // see https://angular.io/start/start-forms
  adminOverrideForm : FormGroup = new FormGroup({});

  constructor(
    private formBuilder: FormBuilder,
    private userAdminService: UserAdminService
  ) {
  }

  updateRuleOverride() {
    console.log("Updating rule override for user " + this.userId + " and date " + this.referenceDateInIso8601 + "...");

    var ruleset : RuleSet = new RuleSet();
    ruleset.min_time_of_day_in_iso_8601 = get_iso_8601_from_time_string(this.adminOverrideForm.value["min_time_of_day"]);
    ruleset.max_time_of_day_in_iso_8601 = get_iso_8601_from_time_string(this.adminOverrideForm.value["max_time_of_day"]);
    ruleset.max_time_per_day_in_seconds = get_duration_in_seconds_from_string(this.adminOverrideForm.value["max_time_per_day"]);
    ruleset.min_break_in_seconds = get_duration_in_seconds_from_string(this.adminOverrideForm.value["min_break"]);
    ruleset.max_activity_duration_in_seconds = get_duration_in_seconds_from_string(this.adminOverrideForm.value["max_activity_duration"]);
    ruleset.free_play = this.adminOverrideForm.value["free_play"];

    this.userAdminService.updateRuleOverride(this.userId, this.referenceDateInIso8601, ruleset).subscribe(
        result  => {
          if ("error" in result)
            console.log(result.error);
          else {
            this.adminDetails?.getUserAdminDetails();
            this.adminDetails?.getUserStatusDetails();
          }
      }
    )
  };
}
