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

import { UserStatus } from '../models/user-status'
import { UserStatusDetail } from '../models/user-status-detail'
import { UserAdmin } from '../models/user-admin'
import { UserAdminDetail } from '../models/user-admin-detail'
import { RuleSet } from '../models/rule-set'

export const my_handlers: Map<string, Function> = new Map();
my_handlers.set("little_brother.transport.user_status_to.UserStatusTO",
    (obj:any) => new UserStatus(obj)
)
my_handlers.set("little_brother.transport.user_status_detail_to.UserStatusDetailTO",
    (obj:any) => new UserStatusDetail(obj)
)
my_handlers.set("little_brother.transport.user_admin_to.UserAdminTO",
    (obj:any) => new UserAdmin(obj)
)
my_handlers.set("little_brother.transport.user_admin_detail_to.UserAdminDetailTO",
    (obj:any) => new UserAdminDetail(obj)
)
my_handlers.set("little_brother.transport.rule_set_to.RuleSetTO",
    (obj:any) => new RuleSet(obj)
)
