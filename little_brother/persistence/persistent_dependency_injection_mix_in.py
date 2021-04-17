from little_brother import dependency_injection
from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_admin_event_entity_manager import AdminEventEntityManager
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.persistent_process_info_entity_manager import ProcessInfoEntityManager
from little_brother.persistence.persistent_rule_override_entity_manager import RuleOverrideEntityManager
from little_brother.persistence.persistent_rule_set_entity_manager import RuleSetEntityManager
from little_brother.persistence.persistent_time_extension_entity_manager import TimeExtensionEntityManager
from little_brother.persistence.persistent_user_2_device_entity_manager import User2DeviceEntityManager
from little_brother.persistence.persistent_user_entity_manager import UserEntityManager


class PersistenceDependencyInjectionMixIn():

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Dependency injection
        self._persistence: Persistence = None
        self._device_entity_manager: DeviceEntityManager = None
        self._user_entity_manager: UserEntityManager = None
        self._process_info_entity_manager: ProcessInfoEntityManager = None
        self._admin_event_entity_manager: AdminEventEntityManager = None
        self._rule_set_entity_manager: RuleSetEntityManager = None
        self._rule_override_entity_manager: RuleOverrideEntityManager = None
        self._device_entity_manager: DeviceEntityManager = None
        self._user_2_device_entity_manager: User2DeviceEntityManager = None
        self._time_extension_entity_manager: TimeExtensionEntityManager = None

    @property
    def persistence(self):

        if self._persistence is None:
            self._persistence = dependency_injection.container[Persistence]

        return self._persistence

    @property
    def time_extension_entity_manager(self) -> TimeExtensionEntityManager:

        if self._time_extension_entity_manager is None:
            self._time_extension_entity_manager = dependency_injection.container[TimeExtensionEntityManager]

        return self._time_extension_entity_manager

    @property
    def user_entity_manager(self) -> UserEntityManager:

        if self._user_entity_manager is None:
            self._user_entity_manager = dependency_injection.container[UserEntityManager]
        return self._user_entity_manager

    @property
    def device_entity_manager(self) -> DeviceEntityManager:

        if self._device_entity_manager is None:
            self._device_entity_manager = dependency_injection.container[DeviceEntityManager]

        return self._device_entity_manager

    @property
    def process_info_entity_manager(self) -> ProcessInfoEntityManager:

        if self._process_info_entity_manager is None:
            self._process_info_entity_manager = dependency_injection.container[ProcessInfoEntityManager]

        return self._process_info_entity_manager

    @property
    def admin_event_entity_manager(self) -> AdminEventEntityManager:

        if self._admin_event_entity_manager is None:
            self._admin_event_entity_manager = dependency_injection.container[AdminEventEntityManager]

        return self._admin_event_entity_manager

    @property
    def rule_set_entity_manager(self) -> RuleSetEntityManager:

        if self._rule_set_entity_manager is None:
            self._rule_set_entity_manager = dependency_injection.container[RuleSetEntityManager]

        return self._rule_set_entity_manager

    @property
    def rule_override_entity_manager(self) -> RuleOverrideEntityManager:

        if self._rule_override_entity_manager is None:
            self._rule_override_entity_manager = dependency_injection.container[RuleOverrideEntityManager]

        return self._rule_override_entity_manager

    @property
    def user_2_device_entity_manager(self) -> User2DeviceEntityManager:

        if self._user_2_device_entity_manager is None:
            self._user_2_device_entity_manager = dependency_injection.container[User2DeviceEntityManager]

        return self._user_2_device_entity_manager
