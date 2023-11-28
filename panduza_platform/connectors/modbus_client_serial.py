import logging
import asyncio

from pymodbus.exceptions import ConnectionException
from pymodbus.client import AsyncModbusSerialClient
from log.driver import driver_logger

from hamcrest import assert_that, equal_to, any_of, has_item

from .udev_tty import SerialPortFromUsbSetting
from .modbus_client_base import ConnectorModbusClientBase

class ConnectorModbusClientSerial(ConnectorModbusClientBase):
    """The serial modbus client connector centralize access to a given port as a modbus client
    """

    # Hold instances mutex
    __MUTEX = asyncio.Lock()

    # Contains instances
    __INSTANCES = {}

    # Local logs
    log = driver_logger("ConnectorModbusClientSerial")

    ###########################################################################
    ###########################################################################

    @staticmethod
    async def Get(**kwargs):
        """Singleton main getter

        
        :Keyword Arguments:
        * *serial_port_name* (``str``) --
            serial port name
    
        * *serial_baudrate* (``int``) --
            serial
        * *serial_bytesize* (``int``) --
            serial

        * *usb_vendor* (``str``) --
            ID_VENDOR_ID
        * *usb_model* (``str``) --
            ID_MODEL_ID
        * *usb_serial_short* (``str``) --
            ID_SERIAL_SHORT

        """
        # Log
        ConnectorModbusClientSerial.log.debug(f"Get connector for {kwargs}")

        async with ConnectorModbusClientSerial.__MUTEX:

            # Log
            ConnectorModbusClientSerial.log.debug(f"Lock acquired !")

            # Get the serial port name
            serial_port_name = None
            if "serial_port_name" in kwargs:
                serial_port_name = kwargs["serial_port_name"]
            elif "usb_vendor" in kwargs:
                serial_port_name = SerialPortFromUsbSetting(**kwargs)
                kwargs["serial_port_name"] = serial_port_name
            else:
                raise Exception("no way to identify the modbus serial port")

            # Create the new connector
            if not (serial_port_name in ConnectorModbusClientSerial.__INSTANCES):
                ConnectorModbusClientSerial.__INSTANCES[serial_port_name] = None
                try:
                    new_instance = ConnectorModbusClientSerial(**kwargs)
                    await new_instance.connect()
                    ConnectorModbusClientSerial.__INSTANCES[serial_port_name] = new_instance
                    ConnectorModbusClientSerial.log.info("connector created")
                except Exception as e:
                    ConnectorModbusClientSerial.__INSTANCES.pop(serial_port_name)
                    raise Exception('Error during initialization').with_traceback(e.__traceback__)

            # Return the previously created
            return ConnectorModbusClientSerial.__INSTANCES[serial_port_name]

    ###########################################################################
    ###########################################################################

    def __init__(self, **kwargs):
        """Constructor
        """
        # Init local mutex
        self._mutex = asyncio.Lock()
        
        key = kwargs["serial_port_name"]

        if not (key in ConnectorModbusClientSerial.__INSTANCES):
            raise Exception("You need to pass through Get method to create an instance")
        else:
            self.log = logging.getLogger(key)
            self.log.info(f"attached to the Modbus Serial Client Connector")

            # create client object
            self.client = AsyncModbusSerialClient(
                method='rtu',
                port=key, 
                baudrate=kwargs.get("serial_baudrate", 112500),
                bytesize=kwargs.get("serial_bytesize", 8),
                parity=kwargs.get("parity", 'N'),
                stopbits=kwargs.get("stopbits", 1)
            )

    # ---

    async def connect(self):
        """Start the client connection
        """

        # Connect to the Modbus device
        connected = await self.client.connect()

        # Check the connected status
        if not connected:
            ConnectorModbusClientSerial.log.info(f"Connection failed")
            raise Exception("Error cannot connect to Serial Port")

    ###########################################################################
    ###########################################################################

    async def write_register(self, address: int, value, unit: int = 1):
        async with self._mutex:
            response = await self.client.write_register(address, value, slave=unit)
            if response.isError():
                raise Exception(f'Error message: {response}')

    ###########################################################################
    ###########################################################################

    async def read_input_registers(self, address: int, size: int = 1, unit: int = 1):
        async with self._mutex:
            response = await self.client.read_input_registers(address, size, slave=unit)
            if not response.isError():
                return response.registers
            else:
                raise Exception(f'Error message: {response}')

    ###########################################################################
    ###########################################################################

    async def read_holding_registers(self, address: int, size: int = 1, unit: int = 1):
        async with self._mutex:
            response = await self.client.read_holding_registers(address=address, count=size, slave=unit)
            if not response.isError():
                return response.registers
            else:
                raise Exception(f'Error message: {response}')



    # async def read_coils(self, address: int, size: int = 1, unit: int = 1):
    #     """
    #     """
    #     with self._mutex:
    #         response = self.client.read_coils(address=address, count=size, slave=unit)
    #         if not response.isError():
    #             return response.bits
    #         else:
    #             raise Exception(f'Error message: {response}')

    # async def write_coils(self, address: int, value: bool, slave: int = 1):
    #     """
    #     """
    #     with self._mutex:
    #         response = self.client.write_coils(address=address, values=value, slave=slave)
    #         if not response.isError():
    #             return response.__dict__
    #         else:
    #             raise Exception(f'Error message: {response}')
        
    # async def write_coil(self, address: int, value: bool, slave: int = 1):
    #     """
    #     write to single coil register
    #     """
    #     with self._mutex:
    #         self.log.info("inside write")
    #         response = self.client.write_coil(address=address, value=value, slave=slave)
    #         if not response.isError():
    #             return response.value
    #         else:
    #             raise Exception(f'Error message: {response}')
        

    # def read_discrete_inputs(self, address: int, size: int = 1, unit: int = 1):
    #     """
    #     """
    #     with self._mutex:
    #         response = self.client.read_discrete_inputs(address=address, count=size, slave=unit)    
    #         if not response.isError():
    #             return response.bits[0]
    #         else:
    #             raise Exception(f'Error message: {response}')

