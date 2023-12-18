import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user';

@Component({
  selector: 'login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  user: User = new User();
  constructor(private router: Router, private auth: AuthService) {}
  onLogin(): void {
    this.auth.login(this.user)
    .then((result) => {
      localStorage.setItem('token', result.auth_token);
      console.log(result);
      this.router.navigateByUrl('/status');
    })
    .catch((err) => {
      console.log(err);
    });
  }

}
