import asyncio

from core.platform_device import PlatformDevice

from connectors.udev_tty import HuntUsbDevs
from connectors.serial_tty import ConnectorSerialTty

from .itf_relay_voxpower_inhibiter import InterfaceVoxpowerInhibit

USBID_VENDOR="2341"
USBID_MODEL="0043"
TTY_BASE="/dev/ttyACM0"

class DeviceVoxpowerInhibiter(PlatformDevice):
    def _PZA_DEV_config(self):
        """ Inhibiter for the Voxpower
        """
        return {
            "family": "Inhibiter",
            "model": "VoxpowerInhibiter",
            "manufacturer": "Panduza",
            "settings_props": [
                {
                    'name': 'serial_port_name',
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
        
        matches = HuntUsbDevs(USBID_VENDOR, USBID_MODEL, 'tty')
        for match in matches:
            # print('------', match)
            devname = match.get('DEVNAME', None)
            if devname:
                try:
                    # self.log.info(devname)
                    connector = await ConnectorSerialTty.Get(
                        serial_port_name=devname,
                        serial_baudrate=115200
                    )
                    
                    regs = await connector.read_holding_registers(address=0x03, size=1, unit=1)
                    # self.log.debug(f"read  regs={regs}")
                    if regs[0] == 3010:

                        ma = self._PZA_DEV_config()["manufacturer"]
                        mo = self._PZA_DEV_config()["model"]
                        ref = f"{ma}.{mo}"
                        bag.append({
                            "ref": ref,
                            "settings": {
                            }
                        })

                except asyncio.exceptions.TimeoutError:
                    print("tiemout")

        return bag
    
    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """
        settings = self.get_settings()

        const_settings = {
            "usb_vendor": USBID_VENDOR,
            "usb_model": USBID_MODEL,
            "serial_baudrate": 115200
        }

        settings.update(const_settings)

        for i in range(2, 10):
            self.mount_interface(
                InterfaceVoxpowerInhibit(name=f"channel_{i}:_ctrl", channel=i, serial_settings=settings)
            )