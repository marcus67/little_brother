import { Component, EventEmitter, Input, Output } from '@angular/core';
import * as bootstrap from 'src/assets/contrib/initializr/js/vendor/bootstrap.bundle.js';

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  styleUrls: ['./confirm-dialog.component.css'],
})
export class ConfirmDialogComponent {
  @Output() confirmed = new EventEmitter<boolean>();
  @Input() message : string = "";

  onConfirm() {
    this.confirmed.emit(true);
    const modalElement = document.getElementById('confirmModal');

    if (modalElement) {
      const bootstrapModal = bootstrap.Modal.getInstance(modalElement);
      bootstrapModal?.hide();
    }
  }
}
