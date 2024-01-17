import asyncio
from core.platform_device import PlatformDevice


from pathlib import Path
# from ThorlabsPM100 import ThorlabsPM100, USBTMC
import os

import usb
import usbtmc

from connectors.utils.usbtmc import HuntUsbtmcDevs
# from connectors.udev_tty import HuntUsbDevs

from .itf_PM100A_powermeter import InterfaceThorlabsPM100APowermeter

class DeviceThorlabsPM100A(PlatformDevice):
    """Power Supply From Korad
    """

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "Powermeter",
            "model": "PM100A",
            "manufacturer": "Thorlabs",
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
        
        # 1313:8079 ThorLabs PM100A

        # try:
        #     print("start")
        #     a = usbtmc.list_devices()
        #     print(a[0])
        #     print(a[0].idVendor)
        #     print(a[0].idProduct)
        #     print(a[0].iSerialNumber)
        #     print(a[0].serial_number) # ok
        #     # inst = usbtmc.Instrument(a[0])
        #     # print(inst.ask("*IDN?"))
        #     # print(dev)
        #     print("stop")
        # except Exception as e:
        #     print("errororoorroorororo")
        #     print(e)


        try:
            matches = HuntUsbtmcDevs(0x1313, 0x8079)
            for match in matches:
                # print('------', match)
                # devlink = match.get('DEVLINKS', None)
                # if devlink:
                # print(f"pooookkkkk1 {devlink}")
        
                ma = self._PZA_DEV_config()["manufacturer"]
                mo = self._PZA_DEV_config()["model"]
                ref = f"{ma}.{mo}"
                bag.append({
                    "ref": ref,
                    "settings": {
                        # "usb_vendor": match.idVendor,
                        # "usb_model": match.idProduct,
                        "usb_serial_short": match.serial_number
                    }
                })
        
        except Exception as e:
            print("errororoorroorororo")
            print(e)


        return bag
    

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """

        settings = self.get_settings()
        print(settings)

        # if ('usb_serial_short' not in settings) and ('serial_port_name' not in settings):
        #     raise Exception("At least one settings must be set")

        const_settings = {
            "usb_vendor": 0x1313,
            "usb_model": 0x8079,
        }
        settings.update(const_settings)

        self.log.info(f"=> {settings}")

        self.mount_interface(
            InterfaceThorlabsPM100APowermeter(name=f"powermeter", settings=settings)
        )




