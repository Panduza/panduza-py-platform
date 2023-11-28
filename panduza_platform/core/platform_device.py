import abc
import copy
from .platform_errors import InitializationError
from .itf_device import InterfacePanduzaDevice

from log.device import device_logger

# ---

def array_name(array_name, index, suffix):
    """To properly format names of grouped interfaces
    """
    return f":{array_name}_{index}:_{suffix}"

# ---

class PlatformDevice:
    """Represent a Device
    """

    def __init__(self, platform=None, client=None, group_name=None, name=None, settings = {}, keep_mounted = False) -> None:
        """Constructor

        It can be instanciated with empty settings to provide only the _PZA_DEV_config
        """
        # Custom name of the device
        self.__name = name

        self.log = device_logger("device_" + str(self.__name))

        # Settings json provided by the user with the tree.json
        self.platform = platform


        self.client = client
        self.group_name = group_name

        # Settings json provided by the user with the tree.json
        self.settings = settings

        # Interfaces linked to this device
        self.interfaces = []

        # Flag to keep this device mounted
        self.keep_mounted = keep_mounted

    # ---

    async def mount_interfaces(self):
        """Request to mount all the interfaces of the device
        """
        self.mount_interface(InterfacePanduzaDevice(name="device"))
        await self._PZA_DEV_mount_interfaces()

    # ---

    async def unmount_interfaces(self):
        """
        """
        for itf in self.interfaces:
            itf.unmount()

    # ---

    def mount_interface(self, itf):
        """Mount an interface
        """
        itf.initialize(self, self.group_name)
        itf.attach_client(self.client)
        self.platform.load_worker(itf)
        self.interfaces.append(itf)

    # ---

    def get_number_of_interfaces(self):
        """Return the number of interfaces managed by this device
        """
        return len(self.interfaces)

    # ---

    # def get_interface_defs(self):
    #     return self.__interface_defs

    # ---

    def get_config_field(self, field, default=None):
        config = self._PZA_DEV_config()
        if not field in config:
            if default == None:
                raise InitializationError(f"\"{field}\" field is not provided in the device config {config}")
            else:
                return default
        return config.get(field)

    # ---

    def get_ref(self):
        """Unique Identifier for this device model
        Different from the name that must be unique for each instance of this device
        """
        return self.get_manufacturer() + "." + self.get_model()

    # ---

    def get_name(self):
        """Unique Identifier for this device instance
        Return a function that can be overloaded by the device implementation to match specific needs
        """
        return self._PZA_DEV_unique_name_generator()

    # ---

    def get_base_name(self):
        """Base name is just the combinaison of manufacturer name and model name separated by '_'
        """
        return self.get_manufacturer() + "_" + self.get_model()

    # ---

    def get_family(self):
        return self.get_config_field("family", "unknown")

    # ---

    def get_model(self):
        return self.get_config_field("model")

    # ---

    def get_manufacturer(self):
        return self.get_config_field("manufacturer")

    # ---

    def get_settings(self):
        return copy.deepcopy(self.settings)

    # ---

    def get_settings_props(self):
        return self.get_config_field("settings_props", [])

    # ---

    async def get_hunted_instances(self):
        return await self._PZA_DEV_hunt()

    # ---

    ###########################################################################
    ###########################################################################
    #
    # TO OVERRIDE IN SUBCLASS
    #
    ###########################################################################
    ###########################################################################

    @abc.abstractmethod
    def _PZA_DEV_config(self):
        """
        """
        pass

    # ---

    @abc.abstractmethod
    async def _PZA_DEV_mount_interfaces(self):
        """
        """
        pass

    # ---

    @abc.abstractmethod
    async def _PZA_DEV_hunt(self):
        """
        """
        return []

    # ---

    @abc.abstractmethod
    def _PZA_DEV_interfaces_generator(self):
        """
        !!!! DEPRECATED !!!!
        """
        raise Exception("Function DEPRECATED !")

    # ---

    @abc.abstractmethod
    def _PZA_DEV_unique_name_generator(self):
        """Must provide a unique and determinist name for the new device

        By default this function does not support multiple instance of the same device on the smae bench.
        Because with this simple method, they will have the same name.
        """
        # name = self.settings.get("name", None)
        # print("!!!!!!!!!!!", self.settings)
        if self.__name:
            return self.__name
        else:
            return self.get_base_name() 

