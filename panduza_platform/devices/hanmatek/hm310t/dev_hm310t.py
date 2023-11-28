import asyncio

from core.platform_device import PlatformDevice

USBID_VENDOR="1a86"
USBID_MODEL="7523"
TTY_BASE="/dev/ttyUSB"

from .itf_hanmatek_hm310t_bpc import InterfaceHanmatekHm310tBpc
from .itf_hanmatek_hm310t_ammeter import InterfaceHanmatekHM310tAmmeter
from .itf_hanmatek_hm310t_voltmeter import InterfaceHanmatekHM310tVoltmeter

from connectors.udev_tty import HuntUsbDevs
from connectors.modbus_client_serial import ConnectorModbusClientSerial


class DeviceHanmatekHm310t(PlatformDevice):
    """Power Supply From Hanmatek
    """

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "BPS",
            "model": "Hm310t",
            "manufacturer": "Hanmatek",
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
                    self.log.info(devname)
                    connector = await ConnectorModbusClientSerial.Get(
                        serial_port_name=devname,
                        serial_baudrate=9600
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

        modbus_settings = {
            "usb_vendor": USBID_VENDOR,
            "usb_model": USBID_MODEL,
            "serial_baudrate": 9600
        }

        self.mount_interface(
            InterfaceHanmatekHm310tBpc(name=f":channel_0:_ctrl", modbus_settings=modbus_settings)
        )
        self.mount_interface(
            InterfaceHanmatekHM310tAmmeter(name=f":channel_0:_am", modbus_settings=modbus_settings)
        )
        self.mount_interface(
            InterfaceHanmatekHM310tVoltmeter(name=f":channel_0:_vm", modbus_settings=modbus_settings)
        )
        

