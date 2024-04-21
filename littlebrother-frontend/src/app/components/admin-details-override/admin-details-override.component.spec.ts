import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminDetailsOverrideComponent } from './admin-details-override.component';

describe('AdminDetailsOverrideComponent', () => {
  let component: AdminDetailsOverrideComponent;
  let fixture: ComponentFixture<AdminDetailsOverrideComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [AdminDetailsOverrideComponent]
    });
    fixture = TestBed.createComponent(AdminDetailsOverrideComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
