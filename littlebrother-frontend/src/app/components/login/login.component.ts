import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user';

@Component({
  selector: 'login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})

export class LoginComponent {

  constructor(private auth: AuthService) {}
    ngOnInit(): void {
      let sampleUser: User = {
      username: 'schule' as string,
      password: 'schule' as string
    };

    this.auth.login(sampleUser).then((result) => {
      console.log(result.json());
    })
    .catch((err) => {
      console.log(err);
    });
  }
}
