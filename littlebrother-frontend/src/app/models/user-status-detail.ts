import { get_duration_as_string, get_date_from_iso_string, get_date_as_string } from '../common/tools'

export class UserStatusDetail {
  history_label?: String;
  duration_in_seconds?: number;
  downtime_in_seconds?: number;
  min_time_in_iso_8601?: string;
  max_time_in_iso_8601?: string;
  host_infos?: string;
  user_status_details?: UserStatusDetail[];

	constructor(otherObject?: object) {
	  if (otherObject)
	    Object.assign(this, otherObject)
	}

  duration_as_string() : string {
   return get_duration_as_string(this.duration_in_seconds);
  }

  downtime_as_string() : string {
   return get_duration_as_string(this.downtime_in_seconds);
  }

  min_time() : Date {
    return get_date_from_iso_string(this.min_time_in_iso_8601)
  }

  min_time_as_string(include_date:boolean=false): string {
    return get_date_as_string(this.min_time(), include_date);
  }

  max_time() : Date {
    return get_date_from_iso_string(this.max_time_in_iso_8601)
  }

  max_time_as_string(include_date:boolean=false): string {
    return get_date_as_string(this.max_time(), include_date);
  }
}
