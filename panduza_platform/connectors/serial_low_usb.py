import time
import asyncio
import logging
import aioserial

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
        
        # key = kwargs["serial_port_name"]
        
        # if not (key in ConnectorSerialLowUsb.__INSTANCES):
        #     raise Exception("You need to pass through Get method to create an instance")
        # else:
        #     self.log = driver_logger(key)
        #     self.log.info(f"attached to the UART Serial Connector")


    # =============================================================================
    # PRIVATE HELPER

    # ---

    # async def __write(self, message, time_lock_s=None):
    #     """
    #     """
    #     try:
    #         # Manage time lock by waiting for the remaining duration
    #         if self._time_lock_s:
    #             elapsed = time.time() - self._time_lock_s["t0"]
    #             if elapsed < self._time_lock_s["duration"]:

    #                 wait_time = self._time_lock_s["duration"] - elapsed
    #                 self.log.debug(f"wait lock {wait_time}")
    #                 await asyncio.sleep(wait_time)
    #             self._time_lock_s = None

    #         # Start sending the message
    #         await self.aioserial_instance.write_async(message.encode())

    #         # Set the time lock if requested by the user
    #         if time_lock_s != None:
    #             self._time_lock_s = {
    #                 "duration": time_lock_s,
    #                 "t0": time.time()
    #             }

    #     except Exception as e:
    #         raise Exception('Error during writing to uart').with_traceback(e.__traceback__)

    # =============================================================================
    # OVERRIDE FROM SERIAL_BASE

    # ---

    async def read(self, n_bytes = None):
        """Read from UART using asynchronous mode
        """
        pass

    # ---

    async def write(self, message, time_lock_s=None):
        """write to UART using asynchronous mode
        """
        pass
        # async with self._mutex:
        #     try:
        #         # Manage time lock by waiting for the remaining duration
        #         if self._time_lock_s:
        #             elapsed = time.time() - self._time_lock_s["t0"]
        #             if elapsed < self._time_lock_s["duration"]:

        #                 wait_time = self._time_lock_s["duration"] - elapsed
        #                 self.log.debug(f"wait lock {wait_time}")
        #                 await asyncio.sleep(wait_time)
        #             self._time_lock_s = None

        #         # Start sending the message
        #         await self.aioserial_instance.write_async(message.encode())

        #         # Set the time lock if requested by the user
        #         if time_lock_s != None:
        #             self._time_lock_s = {
        #                 "duration": time_lock_s,
        #                 "t0": time.time()
        #             }

        #     except Exception as e:
        #         raise Exception('Error during writing to uart').with_traceback(e.__traceback__)

