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
  message: string = "";

  constructor(private router: Router, private auth: AuthService) {}
  onLogin(): void {
    this.auth.login(this.user)
    .then((result) => {
      localStorage.setItem('token', result.auth_token);
      this.message = ""
      this.router.navigateByUrl('/status');
    })
    .catch((err) => {
      console.log(err);
      this.message = err.error.error_details;
    });
  }

}
