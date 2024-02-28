import { RuleSet } from "./rule-set"

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
}
