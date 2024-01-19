import asyncio
from core.platform_device import PlatformDevice


from pathlib import Path
# from ThorlabsPM100 import ThorlabsPM100, USBTMC
import os

import usb


from pyftdi.ftdi import Ftdi


import usb.core
import usb.util

# from connectors.utils.usbtmc import HuntUsbtmcDevs
# from connectors.udev_tty import HuntUsbDevs

# from .itf_PM100A_powermeter import InterfaceThorlabsPM100APowermeter

class DeviceOxxiusLbx488(PlatformDevice):
    """
    """

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "Laser",
            "model": "LBX-488",
            "manufacturer": "Oxxius",
            "settings_props": [
                {
                    'name': 'usb_serial_short',
                    'type': 'string',
                    'default': ''
                }
            ]
        }

    # ---

    async def _PZA_DEV_hunt(self):
        """
        """
        bag = []

        # 0403:90d9 Future Technology Devices International, Ltd LaserBoxx

        try:


            # Get the list of available devices
            Ftdi.add_custom_product(Ftdi.DEFAULT_VENDOR, 0x90d9)
            devices = Ftdi.list_devices()
            Ftdi.show_devices()
            
            print("poooo")
            print(devices)
            # print("==")
            # print(devices[0])
            # dev = devices[0]
            # available_functions = dir(dev[0])
            # print(available_functions)

            # [(UsbDeviceDescriptor(vid=1027, pid=37081, bus=3, address=3, sn='las-05013', index=None, description='LaserBoxx'), 1)]
            
            dev_test = Ftdi()
            # dev_test.open_from_url("ftdi://ftdi:0x90d9:las-05013/1")
            
            
            # devices = usb.core.find(find_all=True)
            dev = usb.core.find(idVendor=Ftdi.DEFAULT_VENDOR, idProduct=0x90d9)
            # dev.set_configuration()
            print(dev)
            # dev.write(1, 'test')


            _usb_dev = dev
            # _usb_dev.open()
            try:
                _usb_dev.set_configuration()
            except USBError:
                pass
            
            _usb_dev.write(0x2, "?SV\n")
            
            # Create a read buffer
            data = _usb_dev.read(0x81,100000,1000)
            
            print( data)
            
            # config = _usb_dev.get_active_configuration()
            # print(config)
            
            # for endpoint in _usb_dev.get_active_configuration().endpoints:
            #     print("Endpoint Address: {}".format(endpoint.address))
            #     print("Endpoint Type: {}".format(endpoint.type))
            #     print("Endpoint Direction: {}".format(endpoint.direction))
            
    
        except Exception as e:
            print("errororoorroorororo")
            print(e)


        # try:
        #     matches = HuntUsbtmcDevs(0x1313, 0x8079)
        #     for match in matches:
        #         # print('------', match)
        #         # devlink = match.get('DEVLINKS', None)
        #         # if devlink:
        #         # print(f"pooookkkkk1 {devlink}")
        
        #         ma = self._PZA_DEV_config()["manufacturer"]
        #         mo = self._PZA_DEV_config()["model"]
        #         ref = f"{ma}.{mo}"
        #         bag.append({
        #             "ref": ref,
        #             "settings": {
        #                 # "usb_vendor": match.idVendor,
        #                 # "usb_model": match.idProduct,
        #                 "usb_serial_short": match.serial_number
        #             }
        #         })
        
        # except Exception as e:
        #     print("errororoorroorororo")
        #     print(e)


        return bag
    

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """

        settings = self.get_settings()
        print(settings)

        # if ('usb_serial_short' not in settings) and ('serial_port_name' not in settings):
        #     raise Exception("At least one settings must be set")

        # const_settings = {
        #     "usb_vendor": 0x1313,
        #     "usb_model": 0x8079,
        # }
        # settings.update(const_settings)

        # self.log.info(f"=> {settings}")

        # self.mount_interface(
        #     InterfaceThorlabsPM100APowermeter(name=f"powermeter", settings=settings)
        # )



