import time
import asyncio
import logging
import aioserial

import usb


from .serial_base import ConnectorSerialBase
from panduza_platform.log.driver import driver_logger

from .udev_tty import SerialPortFromUsbSetting

class ConnectorSerialLowUsb(ConnectorSerialBase):
    """
    """

    # Hold instances mutex
    __MUTEX = asyncio.Lock()

    # Contains instances
    __INSTANCES = {}

    # Local logs
    log = driver_logger("ConnectorSerialLowUsb")

    ###########################################################################
    ###########################################################################

    @staticmethod
    async def Get(**kwargs):
        """Singleton main getter

        :Keyword Arguments:
        * *usb_vendor* (``str``) --
            ID_VENDOR_ID
        * *usb_model* (``str``) --
            ID_MODEL_ID

        """
        # Log
        ConnectorSerialLowUsb.log.debug(f"Get connector for {kwargs}")

        async with ConnectorSerialLowUsb.__MUTEX:

            # Log
            ConnectorSerialLowUsb.log.debug(f"Lock acquired !")

            if "usb_vendor" in kwargs:
                usb_vendor = kwargs["usb_vendor"]
            if "usb_model" in kwargs:
                usb_model = kwargs["usb_model"]
                
            usb_serial_short=""
            if "usb_serial_short" in kwargs:
                usb_serial_short = kwargs["usb_serial_short"]

            instance_name = str(f"{usb_vendor}_{usb_model}_{usb_serial_short}")

            # Create the new connector
            if not (instance_name in ConnectorSerialLowUsb.__INSTANCES):
                ConnectorSerialLowUsb.__INSTANCES[instance_name] = None
                try:
                    new_instance = ConnectorSerialLowUsb(**kwargs)
                    await new_instance.connect()
                    
                    ConnectorSerialLowUsb.__INSTANCES[instance_name] = new_instance
                    ConnectorSerialLowUsb.log.info("connector created")
                except Exception as e:
                    ConnectorSerialLowUsb.__INSTANCES.pop(instance_name)
                    raise Exception('Error during initialization').with_traceback(e.__traceback__)
            else:
                ConnectorSerialLowUsb.log.info("connector already created, use existing instance")

            # Return the previously created
            return ConnectorSerialLowUsb.__INSTANCES[instance_name]

    ###########################################################################
    ###########################################################################

    def __init__(self, **kwargs):
        """Constructor
        """

        # Init local mutex
        self._mutex = asyncio.Lock()

        # Init command mutex
        self._cmd_mutex = asyncio.Lock()

        dev = usb.core.find(idVendor=Ftdi.DEFAULT_VENDOR, idProduct=0x90d9)
        if dev is None:
            raise ValueError('Device not found')
        print(dev)
        dev.reset()
        dev.set_configuration()

        # Must be found through dev
        self.packet_size = 32

        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        # print(intf)

        # Take first output/input endpoint avaiable

        self.ep_out = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

        self.ep_in = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)



    # =============================================================================
    # OVERRIDE FROM SERIAL_BASE

    # ---

    async def read(self, n_bytes = None):
        """Read from UART using asynchronous mode
        """
        async with self._mutex:
            data_array_b = self.ep_in.read(self.packet_size)
            bytes_object = data_array_b.tobytes()
            return bytes_object

    # ---

    async def write(self, message, time_lock_s=None):
        """write to UART using asynchronous mode
        """

        async with self._mutex:
            try:
                # write the data
                cmd = message.encode()
                packet_to_send = cmd + b'\x00' * (self.packet_size - len(cmd))
                self.ep_out.write(packet_to_send)

            except Exception as e:
                raise Exception('Error during writing to uart').with_traceback(e.__traceback__)

