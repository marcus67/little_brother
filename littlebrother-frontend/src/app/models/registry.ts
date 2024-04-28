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