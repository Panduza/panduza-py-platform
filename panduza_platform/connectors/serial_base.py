import abc

class ConnectorSerialBase(metaclass=abc.ABCMeta):
    """Base class for modbus client connectors

    It defines method to interact with the modbus client
    """

    @abc.abstractmethod
    async def read(self, n_bytes = None):
        """
        """
        pass

    @abc.abstractmethod
    async def write(self, message, time_lock_s=None):
        """
        """
        pass
