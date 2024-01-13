import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HelpersComponent } from './helpers.component';

describe('HelpersComponent', () => {
  let component: HelpersComponent;
  let fixture: ComponentFixture<HelpersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HelpersComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HelpersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
