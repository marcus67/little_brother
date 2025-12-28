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

import { Component } from '@angular/core';
import { ControlService } from '../../services/control.service'
import { Control } from '../../models/control'

@Component({
  selector: 'app-control',
  // See https://stackoverflow.com/questions/34673979/differences-of-using-component-template-vs-templateurl
  template: ``,
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
