import traceback
from .platform_errors import InitializationError
from devices import PZA_DEVICES_LIST as INBUILT_DEVICES

class PlatformDeviceFactory:
    """Manage the factory of devices
    """

    # ---

    def __init__(self, parent_platform):
        """ Constructor
        """
        # The factory is composed of builders
        self.__device_templates = {}

        # store
        # {
        #   "manufacturer.model" : {
        #       "instances: []"
        #   }
        # }
        self.__device_store = {}

        self.platform = parent_platform
        self.__log = self.platform.log

    # ---

    def produce_device(self, client, group_name, config, keep_mounted = False):
        """Try to produce the device corresponding the ref
        """
        # Get ref and control it exists in the config provided by the user
        if not "ref" in config:
            raise InitializationError(f"Device \"ref\" field is not provided in the config {config}")
        ref = config["ref"]

        # Control the ref exists in the database
        if not ref in self.__device_templates:
            raise InitializationError(f"\"{ref}\" is not found in this platform")

        # 
        name = config.get("name", None)

        # Produce the device
        try:
            producted_device = self.__device_templates[ref](platform=self.platform, client=client, group_name=group_name, name=name, settings=config.get("settings", {})
                                                            , keep_mounted=keep_mounted)
            return producted_device
        except Exception as e:
            raise InitializationError(f"{traceback.format_exc()}")

    # ---

    def discover(self):
        """Find device models managers
        """
        self.__log.info(f"=")
        for dev in INBUILT_DEVICES:
            self.register_device(dev)
        self.__log.info(f"=")

    # ---

    def register_device(self, device_builder):
        """Register a new device model
        """
        builder=device_builder()
        id = builder.get_ref()
        self.__log.info(f"Register device builder: '{id}'")
        self.__device_templates[id] = device_builder
        self.__device_store[id] = {
            'settings_props': builder.get_settings_props(),
            'instances': []
        }
        # self.__log.info(f"Register device builder: '{id}' {self.__device_store[id]}")

    # ---

    def get_devices_store(self):
        return self.__device_store

    # ---

    async def hunt_start(self):
        self.__log.info(f"HUNT NEW SESSION")
        keys = self.__device_templates.keys()
        max = len(keys)
        self.__hunt_iter = iter(self.__device_templates.keys())

    # ---

    async def hunt_next(self):
        try:
            d = next(self.__hunt_iter)

            device_builder = self.__device_templates[d]()

            self.__log.info(f"HUNT FOR >> {device_builder.get_ref()}")

            instances = await device_builder.get_hunted_instances()
            self.__device_store[d]['instances'] = instances

            # self.__log.info(f">> {self.__device_templates[d]}")
            self.__log.info(f">> {self.__device_store[d]}")
    
            return True
        except StopIteration:
            return False

    # ---

