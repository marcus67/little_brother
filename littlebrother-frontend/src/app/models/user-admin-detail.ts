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
