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

import { get_duration_as_string, get_date_from_iso_string, get_date_as_string } from '../common/tools'

export class UserStatusDetail {
  history_label?: string;
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
   return get_duration_as_string(this.downtime_in_seconds, false);
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
