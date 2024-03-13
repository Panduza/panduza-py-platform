import asyncio

from core.platform_device import PlatformDevice


from .itf_hameg_hm7044_bpc import InterfaceHamegHm7044Bpc

from connectors.udev_tty import HuntUsbDevs
from connectors.modbus_client_serial import ConnectorModbusClientSerial

from dataclasses import dataclass

@dataclass
class HM7044ChannelProps:
    volts: float = 0.0
    amps:  float = 0.0
    on:    bool  = False

class DeviceHamegHm7044(PlatformDevice):

    def _PZA_DEV_config(self):
        """
        """
        return {
            "family": "BPS",
            "model": "Hm7044",
            "manufacturer": "Hameg",
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
        
        # matches = HuntUsbDevs(USBID_VENDOR, USBID_MODEL, 'tty')
        # for match in matches:
        #     # print('------', match)
        #     devname = match.get('DEVNAME', None)
        #     if devname:
        #         try:
        #             self.log.info(devname)
        #             connector = await ConnectorModbusClientSerial.Get(
        #                 serial_port_name=devname,
        #                 serial_baudrate=9600
        #             )
        #             regs = await connector.read_holding_registers(address=0x03, size=1, unit=1)
        #             # self.log.debug(f"read  regs={regs}")
        #             if regs[0] == 3010:

        #                 ma = self._PZA_DEV_config()["manufacturer"]
        #                 mo = self._PZA_DEV_config()["model"]
        #                 ref = f"{ma}.{mo}"
        #                 bag.append({
        #                     "ref": ref,
        #                     "settings": {
        #                     }
        #                 })

        #         except asyncio.exceptions.TimeoutError:
        #             print("tiemout")

        return bag

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """
        
        self.shared_data = [HM7044ChannelProps(),HM7044ChannelProps(),HM7044ChannelProps(),HM7044ChannelProps()]
        
    
        print("mounting interfaces hm7044")

        settings = self.get_settings()

        const_settings = {
            "serial_baudrate": 9600
        }
        
        settings.update(const_settings)

        # settings["bytesize"]     = 8
        # settings["stopbits"]     = 2
        # settings["parity"  ]     = "N"
        # settings["rtscts"  ]     = False

        for i in range(4) :
            self.mount_interface(
                InterfaceHamegHm7044Bpc(name=f":channel_{i}:_ctrl", channel=i, serial_settings=settings, shared_data=self.shared_data)
            )
        # self.mount_interface(
        #     InterfaceHanmatekHM310tAmmeter(name=f":channel_0:_am", modbus_settings=modbus_settings)
        # )
        # self.mount_interface(
        #     InterfaceHanmatekHM310tVoltmeter(name=f":channel_0:_vm", modbus_settings=modbus_settings)
        # )
        

