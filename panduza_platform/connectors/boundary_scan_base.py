import abc

class ConnectorBoundaryScanBase(metaclass=abc.ABCMeta):
    """Base class for boundary scan controller

    It defines method to interact with a boundary scan controller
    """

    @abc.abstractmethod
    async def async_read_number_of_devices(self):
        """
        """
        pass

    @abc.abstractmethod
    async def async_get_idcodes(self):
        """
        """
        pass

    @abc.abstractmethod
    async def async_read_pin(self, device_number, pin, direction):
        """
        """
        pass

    @abc.abstractmethod
    async def async_write_pin(self, device_number, pin, value):
        """
        """
        pass
