import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-nav-bar',
  templateUrl: './nav-bar.component.html',
  styleUrls: ['./nav-bar.component.css']
})
export class NavBarComponent implements OnInit {
  isLoggedIn: boolean = false;
  activeUser: string = "unknown";
  constructor(private router: Router, private auth: AuthService, ) {}

  ngOnInit(): void {
    const token = localStorage.getItem('token');
    if (token) {
      this.auth.ensureAuthenticated(token)
      .then((result) => {
        console.log(result);
        if (result.status === 'OK') {
          this.isLoggedIn = true;
          this.activeUser = result.data.username;
        } else {
          localStorage.removeItem('token');
        }
      })
      .catch((err) => {
        console.log(err);
      });
    }
  }

  onLogout(): void {
    const token = localStorage.getItem('token');
    if (token) {
      this.auth.logout(token).then((result) => {
          console.log(result);
          localStorage.removeItem('token');
          this.isLoggedIn = false;
          this.activeUser = "unknown";

          if (result.status === 'OK') {
            this.router.navigate(['/login']);
          }
        })
        .catch((err) => {
          console.log(err);
          localStorage.removeItem('token');
      });
    }
  }

}
