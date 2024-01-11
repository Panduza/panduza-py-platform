import asyncio
from core.platform_device import PlatformDevice

from .itf_korad_ka3005p_bpc import InterfaceKoradKa3005pBPC
from .itf_korad_ka3005p_ammeter import InterfaceKoradKa3005pAmmeter
from .itf_korad_ka3005p_voltmeter import InterfaceKoradKa3005pVoltmeter


from connectors.udev_tty import HuntUsbDevs

from connectors.serial_tty import ConnectorSerialTty

class DeviceKoradKA3005P(PlatformDevice):
    """Power Supply From Korad
    """

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "BPS",
            "model": "KA3005P",
            "manufacturer": "Korad",
            "settings_props": [
                {
                    'name': 'serial_port_name',
                    'type': 'string',
                    'default': '/dev/ttyACM0'
                }
            ]
        }

    # ---

    async def _PZA_DEV_hunt(self):
        """
        """
        bag = []

        matches = HuntUsbDevs('0416', '5011', 'tty')
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

                    IDN=None
                    try:
                        IDN = await asyncio.wait_for(connector.write_and_read_until("*IDN?", time_lock_s=0.5), timeout=1)
                    except asyncio.TimeoutError:
                        self.log.debug("timeout comminucation")
                        continue
                    self.log.info(f">>>>>>>-------------------- {IDN}")

                    if IDN.decode().startswith("KORAD KD3005P"):
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
            "usb_vendor": '0416',
            "usb_model": '5011',
            "serial_baudrate": 9600
        }

        settings.update(const_settings)

        self.log.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{settings}")
        
        self.mount_interface(
            InterfaceKoradKa3005pBPC(name=f":channel_0:_ctrl", settings=settings)
        )
        self.mount_interface(
            InterfaceKoradKa3005pAmmeter(name=f":channel_0:_am", settings=settings)
        )
        self.mount_interface(
            InterfaceKoradKa3005pVoltmeter(name=f":channel_0:_vm", settings=settings)
        )




