import { UserAdminDetail } from "./user-admin-detail";
import { UserStatus } from "./user-status";

export class UserAdmin {
    user_status?: UserStatus;
    user_id?: number;
    full_name?: String;
    user_admin_details?: UserAdminDetail[];
    time_extension_periods?: number[];
    max_lookahead_in_days?: number;
  
    constructor(otherObject?: object) {
        if (otherObject)
            Object.assign(this, otherObject)
    }
}
