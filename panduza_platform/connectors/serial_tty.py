import time
import asyncio
import logging
import aioserial
# import serial_asyncio

from .serial_base import ConnectorSerialBase
from log.driver import driver_logger

from .udev_tty import SerialPortFromUsbSetting

class ConnectorSerialTty(ConnectorSerialBase):
    """
    """

    # Hold instances mutex
    __MUTEX = asyncio.Lock()

    # Contains instances
    __INSTANCES = {}

    # Local logs
    log = driver_logger("ConnectorSerialTty")

    ###########################################################################
    ###########################################################################

    @staticmethod
    async def Get(**kwargs):
        """Singleton main getter

        
        :Keyword Arguments:
        * *serial_port_name* (``str``) --
            serial port name
    
        * *serial_baudrate* (``int``) --
            serial baudrate
    
        * *usb_vendor* (``str``) --
            ID_VENDOR_ID
        * *usb_model* (``str``) --
            ID_MODEL_ID
        """
        # Log
        ConnectorSerialTty.log.debug(f"Get connector for {kwargs}")

        async with ConnectorSerialTty.__MUTEX:

            # Log
            ConnectorSerialTty.log.debug(f"Lock acquired !")


            # Get the serial port name
            serial_port_name = None
            if "serial_port_name" in kwargs:
                serial_port_name = kwargs["serial_port_name"]
            elif "usb_vendor" in kwargs:
                # Get the serial port name using "usb_vendor"
                serial_port_name = SerialPortFromUsbSetting(**kwargs)
                kwargs["serial_port_name"] = serial_port_name
        
            else:
                raise Exception("no way to identify the serial port")

            # Create the new connector
            if not (serial_port_name in ConnectorSerialTty.__INSTANCES):
                ConnectorSerialTty.__INSTANCES[serial_port_name] = None
                try:
                    new_instance = ConnectorSerialTty(**kwargs)
                    await new_instance.connect()
                    
                    ConnectorSerialTty.__INSTANCES[serial_port_name] = new_instance
                    ConnectorSerialTty.log.info("connector created")
                except Exception as e:
                    ConnectorSerialTty.__INSTANCES.pop(serial_port_name)
                    raise Exception('Error during initialization').with_traceback(e.__traceback__)
            else:
                ConnectorSerialTty.log.info("connector already created, use existing instance")

            # Return the previously created
            return ConnectorSerialTty.__INSTANCES[serial_port_name]

    ###########################################################################
    ###########################################################################

    def __init__(self, **kwargs):
        """Constructor
        """

        # Init local mutex
        self._mutex = asyncio.Lock()

        # Init command mutex
        self._cmd_mutex = asyncio.Lock()


        # Init time lock
        self._time_lock_s = None
        
        
        key = kwargs["serial_port_name"]
        
        if not (key in ConnectorSerialTty.__INSTANCES):
            raise Exception("You need to pass through Get method to create an instance")
        else:
            self.log = driver_logger(key)
            self.log.info(f"attached to the UART Serial Connector")

            
            # Configuration for UART communication

            self.serial_port_name = kwargs.get("serial_port_name", "/dev/ttyUSB0")
            self.serial_baudrate = kwargs.get("serial_baudrate", 9600)
        
        
        print(self.serial_port_name)    
        print(self.serial_baudrate)

    # ---

    async def connect(self):
        """Start the serial connection
        """
        self.aioserial_instance = aioserial.AioSerial(port=self.serial_port_name, baudrate=self.serial_baudrate)

        


    # =============================================================================
    # PRIVATE HELPER

    # ---

    async def _read(self, n_bytes = None):
        """
        """
        return await asyncio.wait_for(self.aioserial_instance.read_async(n_bytes), timeout=1.0)

    # ---

    async def _write(self, message, time_lock_s=None):
        """
        """        
        try:
            # Manage time lock by waiting for the remaining duration
            if self._time_lock_s:
                elapsed = time.time() - self._time_lock_s["t0"]
                if elapsed < self._time_lock_s["duration"]:

                    wait_time = self._time_lock_s["duration"] - elapsed
                    self.log.debug(f"wait lock {wait_time}")
                    await asyncio.sleep(wait_time)
                self._time_lock_s = None

            # Start sending the message
            await self.aioserial_instance.write_async(message.encode())

            # Set the time lock if requested by the user
            if time_lock_s != None:
                self._time_lock_s = {
                    "duration": time_lock_s,
                    "t0": time.time()
                }

        except Exception as e:
            raise Exception('Error during writing to uart').with_traceback(e.__traceback__)

    # ---

    async def __accumulate_date(self, data):
        while True:
            data.append(await self.aioserial_instance.read_async(1))

    # ---

    # =============================================================================
    # OVERRIDE FROM SERIAL_BASE


    # async def beg_cmd(self):
    #     await self._cmd_mutex.acquire()

    # async def end_cmd(self):
    #     self._cmd_mutex.release()

    # ---

    async def read(self, n_bytes = None):
        """Read from UART using asynchronous mode
        """
        async with self._mutex:
            return await asyncio.wait_for(self.aioserial_instance.read_async(n_bytes), timeout=1.0)

    # ---

    async def read_during(self, duration_s = 0.5):
        """
        """
        async with self._mutex:
            data = []
            try:
                await asyncio.wait_for(self.__accumulate_date(data), timeout=duration_s)
            except asyncio.TimeoutError as e: 
                pass
                # raise Exception('Error during reading uart').with_traceback(e.__traceback__)

            # Convert bytearray into bytes
            return b''.join(data)

    # ---

    async def write(self, message, time_lock_s=None):
        """write to UART using asynchronous mode
        """
        async with self._mutex:
            
            try:
                # Manage time lock by waiting for the remaining duration
                if self._time_lock_s:
                    elapsed = time.time() - self._time_lock_s["t0"]
                    if elapsed < self._time_lock_s["duration"]:

                        wait_time = self._time_lock_s["duration"] - elapsed
                        self.log.debug(f"wait lock {wait_time}")
                        await asyncio.sleep(wait_time)
                    self._time_lock_s = None

                # Start sending the message
                await self.aioserial_instance.write_async(message.encode())

                # Set the time lock if requested by the user
                if time_lock_s != None:
                    self._time_lock_s = {
                        "duration": time_lock_s,
                        "t0": time.time()
                    }

            except Exception as e:
                raise Exception('Error during writing to uart').with_traceback(e.__traceback__)


    # async def write_and_read(self, message, time_lock_s=0, n_bytes_to_read=10):
    #     async with self._mutex:
    #         await self._write(message, time_lock_s)
    #         await asyncio.sleep(time_lock_s)
    #         return await self._read(n_bytes_to_read)

    # ---

    async def write_and_read_until(self, message, time_lock_s=0, read_duration_s=0.5):
        async with self._mutex:
            await self._write(message, time_lock_s)
            data = []
            try:
                await asyncio.wait_for(self.__accumulate_date(data), timeout=read_duration_s)
            except asyncio.TimeoutError as e: 
                pass
            return b''.join(data)

    # ---



