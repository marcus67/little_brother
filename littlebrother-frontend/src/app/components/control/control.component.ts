import { Component } from '@angular/core';
import { ControlService } from '../../services/control.service'
import { Control } from '../../models/control'

@Component({
  selector: 'app-control',
  templateUrl: './control.component.html',
  styleUrls: ['./control.component.css']
})

export class ControlComponent {
  control: Control | undefined = undefined;

  constructor(private controlService: ControlService) {
  }

  getControl(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      this.control = new Control(jsonEntry);
    });
  }

  ngOnInit(): void {
    this.getControl();
  }
}
