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
}
