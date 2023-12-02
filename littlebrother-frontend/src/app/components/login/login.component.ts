import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user';

@Component({
  selector: 'login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  user: User = new User();
  constructor(private auth: AuthService) {}
  onLogin(): void {
    this.auth.login(this.user)
    .then((user) => {
      console.log(user);
    })
    .catch((err) => {
      console.log(err);
    });
  }
}
