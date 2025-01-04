import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserConfigurationComponent } from './users.component';

describe('UsersComponent', () => {
  let component: UserConfigurationComponent;
  let fixture: ComponentFixture<UserConfigurationComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [UserConfigurationComponent]
    });
    fixture = TestBed.createComponent(UserConfigurationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
