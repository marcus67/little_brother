import { Component, Input } from '@angular/core';
import { RuleSet } from '../../models/rule-set'

@Component({
  selector: 'app-admin-details-override',
  templateUrl: './admin-details-override.component.html',
  styleUrls: ['./admin-details-override.component.css'],
})
export class AdminDetailsOverrideComponent {
  @Input() override?: RuleSet = new RuleSet();
}
