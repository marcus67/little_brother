import { get_duration_as_string, get_date_from_iso_string, get_date_as_string } from '../common/tools'

export class UserStatus {
  full_name?: String;
	context_label?: String;
	todays_activity_duration_in_seconds?: number;
	max_time_per_day_in_seconds?: number;
	todays_downtime_in_seconds?: number;
	free_play?: boolean;
	activity_permitted?: boolean;
	previous_activity_start_time_in_iso_8601?: string;
	previous_activity_end_time_in_iso_8601?: string;
	current_activity_start_time_in_iso_8601?: string;
	current_activity_duration_in_seconds?: number;
	current_activity_downtime_in_seconds?: number;
	reasons?: string[];

	constructor(otherObject?: object) {
	  if (otherObject)
	    Object.assign(this, otherObject)
	}

//   constructor(
//     full_name?: String,
//     context_label?: String,
//     todays_activity_duration_in_seconds?: number,
//     max_time_per_day_in_seconds?: number,
//     todays_downtime_in_seconds?: number,
//     free_play?: boolean,
//     activity_permitted?: boolean,
//     previous_activity_start_time_in_iso_8601?: string,
//     previous_activity_end_time_in_iso_8601?: string,
//     current_activity_start_time_in_iso_8601?: string,
//     current_activity_duration_in_seconds?: number,
//     current_activity_downtime_in_seconds?: number,
//     reasons?: string[]
//   ) {
//     this.full_name = full_name;
//     this.context_label = context_label;
//     this.todays_activity_duration_in_seconds = todays_activity_duration_in_seconds;
//     this.max_time_per_day_in_seconds = max_time_per_day_in_seconds;
//     this.todays_downtime_in_seconds = todays_downtime_in_seconds;
//     this.free_play = free_play;
//     this.activity_permitted = activity_permitted;
//     this.previous_activity_start_time_in_iso_8601 = previous_activity_start_time_in_iso_8601;
//     this.previous_activity_end_time_in_iso_8601 = previous_activity_end_time_in_iso_8601;
//     this.current_activity_start_time_in_iso_8601 = current_activity_start_time_in_iso_8601;
//     this.current_activity_duration_in_seconds = current_activity_duration_in_seconds;
//     this.current_activity_downtime_in_seconds = current_activity_downtime_in_seconds;
//     this.reasons = reasons;
//   }

  todays_activity_duration() : string {
   return get_duration_as_string(this.todays_activity_duration_in_seconds);
  }

  todays_downtime() : string {
   return get_duration_as_string(this.todays_downtime_in_seconds);
  }

  max_time_per_day() : string {
   return get_duration_as_string(this.max_time_per_day_in_seconds);
  }

  current_activity_duration() : string {
   return get_duration_as_string(this.current_activity_duration_in_seconds);
  }

  current_activity_downtime() : string {
   return get_duration_as_string(this.current_activity_downtime_in_seconds);
  }


  current_activity_start_time() : Date {
    return get_date_from_iso_string(this.current_activity_start_time_in_iso_8601)
  }

  current_activity_start_time_as_string(): string {
    return get_date_as_string(this.current_activity_start_time());
  }

  previous_activity_start_time() : Date {
    return get_date_from_iso_string(this.previous_activity_start_time_in_iso_8601)
  }

  previous_activity_start_time_as_string(): string {
    return get_date_as_string(this.previous_activity_start_time());
  }

  previous_activity_end_time() : Date {
    return get_date_from_iso_string(this.previous_activity_end_time_in_iso_8601)
  }

  previous_activity_end_time_as_string(): string {
    return get_date_as_string(this.previous_activity_end_time());
  }
}
