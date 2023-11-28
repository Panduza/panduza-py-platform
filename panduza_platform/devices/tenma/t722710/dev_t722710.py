import asyncio

from hamcrest import has_key

from core.platform_device import PlatformDevice

from connectors.udev_tty import HuntUsbDevs
from connectors.serial_tty import ConnectorSerialTty

from .itf_tenma_722710_bpc import InterfaceTenma722710Bpc
from .itf_tenma_722710_ammeter import InterfaceTenma722710Ammeter
from .itf_tenma_722710_voltmeter import InterfaceTenma722710Voltmeter

USBID_VENDOR="0416"
USBID_MODEL="5011"
TTY_BASE="/dev/ttyACM0"

class DeviceTenma722710(PlatformDevice):
    """Power Supply From Tenma
    """

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "BPS",
            "model": "72-2710",
            "manufacturer": "Tenma",
            "settings_props": [
                {
                    'name': 'usb_serial_short',
                    'type': 'string',
                    'description': 'USB serial number of the device',
                    'default': ''
                },
                {
                    'name': 'serial_port_name',
                    'type': 'string',
                    'description': 'Serial port name, better use the usb_serial_short',
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
                        serial_baudrate=9600
                    )
                    IDN = await connector.write_and_read_until("*IDN?", time_lock_s=0.5)
                    # self.log.info(IDN)

                    if IDN.decode().startswith("TENMA 72-2710"):
                        ma = self._PZA_DEV_config()["manufacturer"]
                        mo = self._PZA_DEV_config()["model"]
                        ref = f"{ma}.{mo}"
                        bag.append({
                            "ref": ref,
                            "settings": {
                                "usb_serial_short": match.get('ID_SERIAL_SHORT', None)
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

        if ('usb_serial_short' not in settings) and ('serial_port_name' not in settings):
            raise Exception("At least one settings must be set")

        const_settings = {
            "usb_vendor": USBID_VENDOR,
            "usb_model": USBID_MODEL,
            "serial_baudrate": 9600
        }
        
        settings.update(const_settings)

        self.mount_interface(
            InterfaceTenma722710Bpc(name=f":channel_0:_ctrl", settings=settings)
        )
        self.mount_interface(
            InterfaceTenma722710Ammeter(name=f":channel_0:_am", settings=settings)
        )
        self.mount_interface(
            InterfaceTenma722710Voltmeter(name=f":channel_0:_vm", settings=settings)
        )

        
        
        
