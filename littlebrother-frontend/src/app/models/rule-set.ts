import { get_duration_as_string, get_date_from_iso_string, get_date_as_string } from '../common/tools'

export class RuleSet {

    label?: string
    min_time_of_day_in_iso_8601?: string
    max_time_of_day_in_iso_8601?: string
    max_time_per_day_in_seconds?: number
    min_break_in_seconds?: number
    max_activity_duration_in_seconds?: number
    free_play?: boolean


    constructor(otherObject?: object) {
        if (otherObject)
            Object.assign(this, otherObject)
    }

    min_time_of_day() : Date {
        return get_date_from_iso_string(this.min_time_of_day_in_iso_8601)
      }
    
    
    min_time_of_day_as_string(include_date:boolean=false): string {
        return get_date_as_string(this.min_time_of_day(), include_date);
    }

    max_time_of_day() : Date {
        return get_date_from_iso_string(this.max_time_of_day_in_iso_8601)
      }
    
    
    max_time_of_day_as_string(include_date:boolean=false): string {
        return get_date_as_string(this.max_time_of_day(), include_date);
    }

    max_time_per_day_as_string() : string {
        return get_duration_as_string(this.max_time_per_day_in_seconds);
    }

    min_break_as_string() : string {
        return get_duration_as_string(this.min_break_in_seconds);
    }

    max_activity_duration_as_string() : string {
        return get_duration_as_string(this.max_activity_duration_in_seconds);
    }
}
