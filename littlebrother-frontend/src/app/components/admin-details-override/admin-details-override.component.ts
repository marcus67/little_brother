import { Component, Input } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { RuleSet } from '../../models/rule-set'

@Component({
  selector: 'app-admin-details-override',
  templateUrl: './admin-details-override.component.html',
  styleUrls: ['./admin-details-override.component.css'],
})
export class AdminDetailsOverrideComponent {
  _override?: RuleSet = undefined;

  // See https://stackoverflow.com/questions/38571812/how-to-detect-when-an-input-value-changes-in-angular
  @Input() set override(override: RuleSet | undefined) {
    if (! this._override) {
      this._override = override;
      this.adminOverrideForm = this.formBuilder.group({
        min_time_of_day_as_string: this._override?.min_time_of_day_as_string(),
        max_time_of_day_as_string: this._override?.max_time_of_day_as_string(),
        max_time_per_day_as_string: this._override?.max_time_per_day_as_string(),
        min_break_as_string: this._override?.min_break_as_string(),
        max_activity_duration_as_string: this._override?.max_activity_duration_as_string(),
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
  ) {
  }
}
