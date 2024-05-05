import { Component, Input } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { RuleSet } from '../../models/rule-set'
import { UserAdminService } from 'src/app/services/user-admin.service';
import { get_duration_in_seconds_from_string, get_iso_8601_from_time_string } from 'src/app/common/tools';
import { AdminDetailsComponent } from '../admin-details/admin-details.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { timeValidationPattern, timeDurationPattern } from 'src/app/common/tools';

@Component({
  selector: 'app-admin-details-override',
  templateUrl: './admin-details-override.component.html',
  styleUrls: ['./admin-details-override.component.css'],
})
export class AdminDetailsOverrideComponent {
  _override?: RuleSet = undefined;
  min_time_of_day: FormControl = new FormControl()
  max_time_of_day: FormControl = new FormControl()
  max_time_per_day: FormControl = new FormControl()
  min_break: FormControl = new FormControl()
  max_activity_duration: FormControl = new FormControl()
  @Input() userId?: number = undefined;
  @Input() referenceDateInIso8601?: string = undefined;
  @Input() adminDetails?: AdminDetailsComponent = undefined;

  // See https://stackoverflow.com/questions/38571812/how-to-detect-when-an-input-value-changes-in-angular
  @Input() set override(override: RuleSet | undefined) {
    if (! this._override) {
      this._override = override;
      this.min_time_of_day = new FormControl(
        this._override?.min_time_of_day_as_string(),
        Validators.pattern(timeValidationPattern)
      )
      this.max_time_of_day = new FormControl(
        this._override?.max_time_of_day_as_string(),
        Validators.pattern(timeValidationPattern)
      )
      this.max_time_per_day = new FormControl(
        this._override?.max_time_per_day_as_string(),
        Validators.pattern(timeDurationPattern)
      )
      this.min_break = new FormControl(
        this._override?.min_break_as_string(),
        Validators.pattern(timeDurationPattern)
      )
      this.max_activity_duration = new FormControl(
        this._override?.max_activity_duration_as_string(),
        Validators.pattern(timeDurationPattern)
      )
      this.adminOverrideForm = this.formBuilder.group({
        min_time_of_day: this.min_time_of_day,
        max_time_of_day: this.max_time_of_day,
        max_time_per_day: this.max_time_per_day,
        min_break: this.min_break,
        max_activity_duration: this.max_activity_duration,
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
    private userAdminService: UserAdminService,
    private saveMessageSnackBar: MatSnackBar
  ) {
  }

  updateRuleOverride() {
    if (this.adminOverrideForm.invalid || this.adminOverrideForm.pristine) {
      console.log("Skipping rule override update since form is pristine or invalid!");
      return;
    } 

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
            // See https://v16.material.angular.io/components/snack-bar/overview
            // See https://www.geeksforgeeks.org/matsnackbar-in-angular-material/
            this.saveMessageSnackBar.open('Override saved', 'OK', {
              duration: 3000
            });
          }
      }
    )
  };
}
