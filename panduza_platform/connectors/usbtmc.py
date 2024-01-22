import time
import asyncio
import logging
import aioserial

import concurrent.futures


from log.driver import driver_logger

# from .udev_tty import SerialPortFromUsbSetting

import usbtmc
from .utils.usbtmc import FindUsbtmcDev

class ConnectorUsbtmc():
    """
    """

    # Hold instances mutex
    __MUTEX = asyncio.Lock()

    # Contains instances
    __INSTANCES = {}

    # Local logs
    log = driver_logger("ConnectorUsbtmc")

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
        * *usb_serial_short* (``str``) --
            ID_SERIAL_SHORT
        """
        # Log
        ConnectorUsbtmc.log.info(f"Get connector for {kwargs}")

        async with ConnectorUsbtmc.__MUTEX:

            # Log
            ConnectorUsbtmc.log.info(f"Lock acquired !")

            # Get the serial port name
            usbtmc_key = f"{kwargs['usb_vendor']}_{kwargs['usb_model']}_{kwargs['usb_serial_short']}"
            ConnectorUsbtmc.log.debug(f"Key {usbtmc_key}")

            # Create the new connector
            if not (usbtmc_key in ConnectorUsbtmc.__INSTANCES):
                ConnectorUsbtmc.__INSTANCES[usbtmc_key] = None
                try:
                    new_instance = ConnectorUsbtmc(**kwargs)

                    ConnectorUsbtmc.__INSTANCES[usbtmc_key] = new_instance
                    ConnectorUsbtmc.log.info("connector created")
                except Exception as e:
                    ConnectorUsbtmc.__INSTANCES.pop(usbtmc_key)
                    raise Exception('Error during initialization').with_traceback(e.__traceback__)
            else:
                ConnectorUsbtmc.log.info("connector already created, use existing instance")

            # Return the previously created
            return ConnectorUsbtmc.__INSTANCES[usbtmc_key]

    ###########################################################################
    ###########################################################################

    def __init__(self, **kwargs):
        """Constructor
        """

        # Init local mutex
        self._mutex = asyncio.Lock()

        # Init command mutex
        self._cmd_mutex = asyncio.Lock()


        self.log.info(kwargs)
        device_ref = FindUsbtmcDev(usb_vendor= kwargs["usb_vendor"], 
                      usb_model= kwargs["usb_model"], 
                      usb_serial_short=kwargs['usb_serial_short'])
        
        self.usbtmc_instance = usbtmc.Instrument(device_ref)
        self.usbtmc_instance.open()

    # ---

    # async def connect(self):
    #     """Start the serial connection
    #     """
    #     self.aioserial_instance = aioserial.AioSerial(port=self.serial_port_name, baudrate=self.serial_baudrate)

    # # =============================================================================
    # # OVERRIDE FROM SERIAL_BASE


    # # async def beg_cmd(self):
    # #     await self._cmd_mutex.acquire()

    # # async def end_cmd(self):
    # #     self._cmd_mutex.release()


    def close(self):
        self.usbtmc_instance.close()

    # ---

    async def ask(self, command):
        """
        """
        return await asyncio.wait_for(
            self.run_async_function(self.usbtmc_instance.ask, command),
            timeout=2.0)

    # ---

    def ask_e(self, command):
        """
        """
        return self.usbtmc_instance.ask(command)
        
    # ---

    async def run_async_function(self,function,*args):
        async with self._mutex:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Submit the function to the executor
                future = executor.submit(function, *args)
                
                # Wait for the future to complete
                while not future.done():
                    await asyncio.sleep(0.1)
                    #print(f"Waiting for the thread to complete...")
                
                # Retrieve the result from the future
                result = future.result()
                #print("Result:", result)
                
                return result

    # ---

    # async def read_during(self, duration_s = 0.5):
    #     """
    #     """
    #     async with self._mutex:
    #         data = []
    #         try:
    #             await asyncio.wait_for(self.__accumulate_date(data), timeout=duration_s)
    #         except asyncio.TimeoutError as e: 
    #             pass
    #             # raise Exception('Error during reading uart').with_traceback(e.__traceback__)

    #         # Convert bytearray into bytes
    #         return b''.join(data)

    # # ---

    # async def write(self, message, time_lock_s=None):
    #     """write to UART using asynchronous mode
    #     """
    #     async with self._mutex:
            
    #         try:
    #             # Manage time lock by waiting for the remaining duration
    #             if self._time_lock_s:
    #                 elapsed = time.time() - self._time_lock_s["t0"]
    #                 if elapsed < self._time_lock_s["duration"]:

    #                     wait_time = self._time_lock_s["duration"] - elapsed
    #                     self.log.info(f"wait lock {wait_time}")
    #                     await asyncio.sleep(wait_time)
    #                 self._time_lock_s = None

    #             # Start sending the message
    #             await self.aioserial_instance.write_async(message.encode())

    #             # Set the time lock if requested by the user
    #             if time_lock_s != None:
    #                 self._time_lock_s = {
    #                     "duration": time_lock_s,
    #                     "t0": time.time()
    #                 }

    #         except Exception as e:
    #             raise Exception('Error during writing to uart').with_traceback(e.__traceback__)


    # # async def write_and_read(self, message, time_lock_s=0, n_bytes_to_read=10):
    # #     async with self._mutex:
    # #         await self._write(message, time_lock_s)
    # #         await asyncio.sleep(time_lock_s)
    # #         return await self._read(n_bytes_to_read)

    # # ---

    # async def write_and_read_during(self, message, time_lock_s=0, read_duration_s=0.5):
    #     async with self._mutex:
    #         await self._write(message, time_lock_s)
    #         data = []
    #         try:
    #             await asyncio.wait_for(self.__accumulate_date(data), timeout=read_duration_s)
    #         except asyncio.TimeoutError as e: 
    #             pass
    #         return b''.join(data)

    # # ---



