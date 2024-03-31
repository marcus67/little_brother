import { RuleSet } from "./rule-set"
// See https://date-fns.org/
import { format } from 'date-fns'
import { get_duration_as_string, get_date_from_iso_string, get_date_as_string } from '../common/tools'

export class UserAdminDetail {

    date_in_iso_8601?: string
    long_format?: string
    short_format?: string
    rule_set?: RuleSet
    override?: RuleSet
    effective_rule_set?: RuleSet


    constructor(otherObject?: object) {
        if (otherObject)
            Object.assign(this, otherObject)
    }

    date(): Date {
        return get_date_from_iso_string(this.date_in_iso_8601)

    }

    date_in_short_format(): string {
        return format(this.date(), this.short_format || "EEE");
    }

    date_in_long_format(): string {
        return format(this.date(), this.long_format || "EEE");
    }

}
