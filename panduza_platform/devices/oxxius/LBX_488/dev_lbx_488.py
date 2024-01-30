import asyncio
from core.platform_device import PlatformDevice
from pathlib import Path

import os

import usb


from pyftdi.ftdi import Ftdi

import usb.core
import usb.util

from .itf_lbx_488_blc import InterfaceLbx488Blc

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
            Ftdi.show_devices()
            
            usb_matches = Ftdi.list_devices()
            print(usb_matches)
            
            for usb_match in usb_matches:
                
                match = usb_match[0]
                
                if match.pid == 0x90d9:
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
                            "usb_serial_short": match.sn
                        }
                    })

        except Exception as e:
            print("errororoorroorororo")
            print(e)
            
            
            

    
            
            # # write the data
            
            # patcket_sizeee = 32
            # cmd = b"?SV"
            # packet_to_send = cmd + b'\x00' * (patcket_sizeee - len(cmd))
            # # packet_to_send = cmd
            # ep.write(packet_to_send)


            # ep_in = usb.util.find_descriptor(
            #     intf,
            #     # match the first OUT endpoint
            #     custom_match = \
            #     lambda e: \
            #         usb.util.endpoint_direction(e.bEndpointAddress) == \
            #         usb.util.ENDPOINT_IN)



            # data_array_b = ep_in.read(patcket_sizeee)
            # print(data_array_b)
            # bytes_object = data_array_b.tobytes()
            # print(bytes_object)
            
            # data = ep_in.read(1)
            # print(data)




        #     _usb_dev = dev
        #     # _usb_dev.open()
            
        #     _usb_dev.write(0x2, "?SV\n")
            
        #     # Create a read buffer
        #     data = _usb_dev.read(0x81,100000,1000)
            
        #     print( data)
            
        #     # config = _usb_dev.get_active_configuration()
        #     # print(config)
            
        #     # for endpoint in _usb_dev.get_active_configuration().endpoints:
        #     #     print("Endpoint Address: {}".format(endpoint.address))
        #     #     print("Endpoint Type: {}".format(endpoint.type))
        #     #     print("Endpoint Direction: {}".format(endpoint.direction))
            
    
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

        const_settings = {
            "usb_vendor": Ftdi.DEFAULT_VENDOR,
            "usb_model": 0x90d9, # for the laser oxxius
        }
        settings.update(const_settings)

        # self.log.info(f"=> {settings}")

        self.mount_interface(
            InterfaceLbx488Blc(name=f"blc", settings=settings)
        )




