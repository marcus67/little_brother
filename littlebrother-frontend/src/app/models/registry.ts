import { UserStatus } from '../models/user-status'
import { UserStatusDetail } from '../models/user-status-detail'

export const my_handlers: Map<string, Function> = new Map();
my_handlers.set("little_brother.transport.user_status_to.UserStatusTO", (obj:any) => new UserStatus(obj))
my_handlers.set("little_brother.transport.user_status_detail_to.UserStatusDetailTO", (obj:any) => new UserStatusDetail(obj))
