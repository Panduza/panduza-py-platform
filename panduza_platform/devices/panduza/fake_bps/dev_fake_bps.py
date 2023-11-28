from core.platform_device import PlatformDevice, array_name

from .itf_bpc import InterfacePanduzaFakeBpc
from .itf_ammeter import InterfacePanduzaFakeAmmeter
from .itf_voltmeter import InterfacePanduzaFakeVoltmeter

class DevicePanduzaFakeBps(PlatformDevice):

    # ---

    def _PZA_DEV_config(self):
        return {
            "family": "BPS",
            "model": "FakeBps",
            "manufacturer": "Panduza",
            "settings_props": [
                {
                    'name': 'number_of_channel',
                    'type': 'int'
                }
            ]
        }

    # ---

    async def _PZA_DEV_mount_interfaces(self):
        """
        """

        number_of_channel = self.settings.get("number_of_channel", 1)
        
        for chan in range(0, number_of_channel):
            
            self.mount_interface(
                InterfacePanduzaFakeBpc(name=array_name("channel", chan, "ctrl"))
            )
            self.mount_interface(
                InterfacePanduzaFakeAmmeter(name=array_name("channel", chan, "am"))
            )
            self.mount_interface(
                InterfacePanduzaFakeVoltmeter(name=array_name("channel", chan, "vm"))
            )
         
    # ---

