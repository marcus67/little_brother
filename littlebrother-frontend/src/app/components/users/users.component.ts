import { Component, OnInit } from '@angular/core';
import { User } from '../../models/user';
import { UserService } from '../../services/user.service';
import { ControlService } from '../../services/control.service'
import { unpickle } from '../../common/unpickle'
import { my_handlers } from '../../models/registry'
import { Control } from 'src/app/models/control';
import { format_text_array } from 'src/app/common/tools'; 

@Component({
  selector: 'app-users',
  templateUrl: './users.component.html'
})
export class UsersComponent implements OnInit {
  users: User[] = [];
  isLoading: boolean = true;
  selectedUnconfiguredUser: string = "";
  languages: Record<string, string> | undefined = {};

  constructor(
    private userService: UserService,
    private controlService: ControlService
  ) {
  }

  getUsers(): void {
    this.userService.loadUsers().subscribe( jsonData => {
      let unpickledData = unpickle(jsonData, my_handlers)

      if (unpickledData) {
        this.users = unpickledData
        this.users.sort( (a:User, b:User) => {
              var upper_full_name_a = a.full_name() || "";
              var upper_full_name_b = b.full_name() || "";
              return  (upper_full_name_a < upper_full_name_b) ? -1 : (upper_full_name_a > upper_full_name_b) ? 1 : 0;
            }
        );

        this.isLoading = false;
      } else {
        console.error("Cannot unpickle User entries")
      }
    });
  }

  getUserSummary(user: User): string | undefined {
    return format_text_array(user.summary(this.languages));
  }


  getControl(): void {
    this.controlService.loadControl().subscribe( jsonEntry => {
      let control : Control = new Control(jsonEntry);

      this.languages = control.languages;
    })
  }

  getUnconfiguredUsers() : (string | undefined) [] {
    return Array.from(this.users.filter( user => ! user.configured), (user, i) => user.username).sort();
  }

  addUnconfiguredUser() {
  }

  ngOnInit(): void {
    this.getUsers();
    this.getControl();
  }
}
