import time
import asyncio
import logging
import aioserial
import os 

import concurrent.futures

import pyudev
from log.driver import driver_logger

# from .udev_tty import SerialPortFromUsbSetting

import usbtmc
from connectors.utils.usbtmc import FindUsbtmcDev

from connectors.udev_tty import HuntUsbDevs

from ThorlabsPM100 import ThorlabsPM100, USBTMC

class ConnectorThorlabsPM100():
    """
    """

    # Hold instances mutex
    __MUTEX = asyncio.Lock()

    # Contains instances
    __INSTANCES = {}

    # Local logs
    log = driver_logger("ConnectorThorlabsPM100")

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
        ConnectorThorlabsPM100.log.info(f"Get connector for {kwargs}")

        async with ConnectorThorlabsPM100.__MUTEX:

            # Log
            ConnectorThorlabsPM100.log.info(f"Lock acquired !")

            # Get the serial port name
            usbtmc_key = f"{kwargs['usb_vendor']}_{kwargs['usb_model']}_{kwargs['usb_serial_short']}"
            ConnectorThorlabsPM100.log.debug(f"Key {usbtmc_key}")

            # Create the new connector
            if not (usbtmc_key in ConnectorThorlabsPM100.__INSTANCES):
                ConnectorThorlabsPM100.__INSTANCES[usbtmc_key] = None
                try:
                    new_instance = ConnectorThorlabsPM100(**kwargs)

                    ConnectorThorlabsPM100.__INSTANCES[usbtmc_key] = new_instance
                    ConnectorThorlabsPM100.log.info("connector created")
                except Exception as e:
                    ConnectorThorlabsPM100.__INSTANCES.pop(usbtmc_key)
                    raise Exception('Error during initialization').with_traceback(e.__traceback__)
            else:
                ConnectorThorlabsPM100.log.info("connector already created, use existing instance")

            # Return the previously created
            return ConnectorThorlabsPM100.__INSTANCES[usbtmc_key]

    ###########################################################################
    ###########################################################################

    def __init__(self, **kwargs):
        """Constructor
        """

        # Init local mutex
        self._mutex = asyncio.Lock()

        # Init command mutex
        self._cmd_mutex = asyncio.Lock()


        # # self.log.info(kwargs)
        # device_ref = FindUsbtmcDev(usb_vendor= kwargs["usb_vendor"], 
        #               usb_model= kwargs["usb_model"], 
        #               usb_serial_short=kwargs['usb_serial_short'])
        
        # print(device_ref)
        # print(type(device_ref))
        
        print("================")
        
        # devsss = HuntUsbDevs(usb_vendor= kwargs["usb_vendor"], usb_model= kwargs["usb_model"])
        # print(devsss)

        usb_vendor = kwargs["usb_vendor"]
        if(type(usb_vendor) == int):
            usb_vendor = str(hex(usb_vendor))[2:]
        
        usb_model = kwargs["usb_model"]
        if(type(usb_model) == int):
            usb_model = str(hex(usb_model))[2:]
    
        usb_serial_short = kwargs['usb_serial_short']
        usbtmc_devname=f"/dev/usbtmc-{usb_vendor}-{usb_model}-{usb_serial_short}"
        real_path = os.path.realpath(usbtmc_devname)
        print(real_path)
    
        print("================")

        
        inst = USBTMC(device=real_path)
        self.pm_instance = ThorlabsPM100(inst=inst)
        



    # ---

    def read(self):
        """
        """
        return self.pm_instance.read

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



