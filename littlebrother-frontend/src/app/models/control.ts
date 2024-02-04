export class Control {
  refresh_interval_in_milliseconds? : number;

	constructor(otherObject: Control) {
	  Object.assign(this, otherObject)
	}
}
