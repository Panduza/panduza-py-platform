import asyncio
from core.platform_device import PlatformDevice


from pathlib import Path
# from ThorlabsPM100 import ThorlabsPM100, USBTMC
import os

import usb
# import usbtmc

# from connectors.utils.usbtmc import HuntUsbtmcDevs
from connectors.udev_tty import HuntUsbDevs

from .itf_cobolt_0501_blc import InterfaceCobolt0501Blc

class DeviceCobolt0501(PlatformDevice):
    """Power Supply From Korad
    """

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "laser",
            "model": "0501",
            "manufacturer": "Cobolt",
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
        
        try:
            # 25dc:0006 Cobolt AB Cobolt Laser Driver 05-71
            matches = HuntUsbDevs('25dc', '0006', 'tty')
            for match in matches:
                print('------', match)
                devname = match.get('DEVNAME', None)
                if devname:
                    self.log.info(devname)
                    
                    ma = self._PZA_DEV_config()["manufacturer"]
                    mo = self._PZA_DEV_config()["model"]
                    ref = f"{ma}.{mo}"
                    bag.append({
                        "ref": ref,
                        "settings": {
                            "usb_serial_short": match.get('ID_SERIAL_SHORT', None)
                        }
                    })

        except Exception as e:
            print("error")
            print(e)

        return bag
    
    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """

        settings = self.get_settings()
        print("in blc !!!")
        print(settings)

        const_settings = {
            "usb_vendor": '25dc',
            "usb_model": '0006',
            "serial_baudrate": 115200
        }
        settings.update(const_settings)

        self.log.info(f"=> {settings}")

        self.mount_interface(
            InterfaceCobolt0501Blc(name=f"blc", settings=settings)
        )




