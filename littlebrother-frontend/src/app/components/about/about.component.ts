import { Component } from '@angular/core';
import { MetadataService } from '../../services/metadata.service'

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})

export class AboutComponent {

  metadata : any = null;

  constructor(private metadataService: MetadataService) {
    this.metadataService.loadMetadata().then((result) => {
      this.metadata = result;
    });
  }
}
