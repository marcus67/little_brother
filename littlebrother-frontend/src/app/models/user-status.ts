// Copyright (C) 2019-24  Marcus Rickert
//
// See https://github.com/marcus67/little_brother
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import { UserStatusDetail } from '../models/user-status-detail'
import { get_duration_as_string, get_date_from_iso_string, get_date_as_string } from '../common/tools'

export class UserStatus {
  user_id?: number;
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
  user_status_details?: UserStatusDetail[];

	constructor(otherObject?: object) {
	  if (otherObject)
	    Object.assign(this, otherObject)
	}

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
