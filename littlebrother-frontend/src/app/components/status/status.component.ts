import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'status',
  templateUrl: './status.component.html',
  styleUrls: ['./status.component.css']
})
export class StatusComponent implements OnInit {
  isLoggedIn: boolean = false;
  constructor(private router: Router, private auth: AuthService, ) {}
  ngOnInit(): void {
    const token = localStorage.getItem('token');
    if (token) {
      this.auth.ensureAuthenticated(token)
      .then((result) => {
        console.log(result);
        if (result.status === 'OK') {
          this.isLoggedIn = true;
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
